import sys
import os
import json
import csv
import yaml
import logging
from datetime import datetime
from pathlib import Path

# Add project root to python path to allow direct script execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import JobProfile
from models.data_ingestion import ingestor
from models.pipelines.ranking_engine import ranking_engine
from models.explainability.explainer import explainer

logger = logging.getLogger("twinrank.submission")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_submission(job_path: str, candidates_path: str, output_dir: str):
    """
    Executes the end-to-end offline submission pipeline.
    Produces the final CSV and metadata.yaml required for competition scoring.
    """
    logger.info("Starting TwinRank AI submission pipeline...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. Load Job
    logger.info(f"Loading Job Profile from {job_path}...")
    with open(job_path, 'r', encoding='utf-8') as f:
        job_data = json.load(f)
        job = JobProfile(**job_data)
        
    # 2. Load Candidates
    candidates = ingestor.load_candidates(candidates_path)
    logger.info(f"Loaded {len(candidates)} valid candidate profiles.")
    
    # 3. Rank (Executes Feature Eng -> Honeypot -> Ranking -> Reranking)
    logger.info("Running Hybrid Ranking Engine...")
    scored_results = ranking_engine.rank_and_score(job, candidates)
    
    # 4. Filter Top 100 for submission constraints
    top_100 = scored_results[:100]
    logger.info(f"Filtering to top {len(top_100)} candidates for final output.")
    
    # 5. Generate Explanations and build CSV rows
    csv_rows = []
    for rank, item in enumerate(top_100, 1):
        cand = item["candidate"]
        score = item["score"]
        features = item["features"]
        
        # Heavy explainability pass
        explanation = explainer.generate_explanation(job, cand, features, score)
        
        csv_rows.append({
            "rank": rank,
            "candidate_id": cand.id,
            "score": round(score, 4),
            "honeypot_probability": round(item["honeypot_prob"], 4),
            "confidence_score": explanation["confidence_score"],
            "why_selected": explanation["why_selected"],
            "strengths_summary": " | ".join(explanation["strengths"])
        })
        
    # 6. Write CSV
    csv_path = os.path.join(output_dir, "submission.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        if csv_rows:
            writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)
    logger.info(f"Generated submission file: {csv_path}")
        
    # 7. Write Metadata YAML
    metadata = {
        "submission_meta": {
            "team_name": "TwinRank AI",
            "submission_date": datetime.now().isoformat(),
            "model_version": "1.0.0",
            "environment": "CPU-only",
            "runtime_constraint": "< 5 mins"
        },
        "pipeline_stats": {
            "candidates_processed": len(candidates),
            "candidates_output": len(top_100),
            "features_used": [
                "capability", "growth", "behavior", 
                "risk", "fraud", "semantic_skill_graph"
            ]
        }
    }
    
    yaml_path = os.path.join(output_dir, "metadata.yaml")
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
    logger.info(f"Generated metadata file: {yaml_path}")
    
    # 8. Run Validator
    _validate_submission(csv_path, len(top_100))

def _validate_submission(csv_path: str, expected_count: int):
    """
    Runs integrity checks to ensure the generated CSV perfectly matches 
    the competition's submission schema.
    """
    logger.info("Running submission validator...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
            
        assert len(reader) == expected_count, f"Validation Failed: Expected {expected_count} rows, got {len(reader)}"
        
        for idx, row in enumerate(reader):
            assert int(row['rank']) == idx + 1, "Validation Failed: Ranks must be strictly sequential"
            assert 0.0 <= float(row['honeypot_probability']) <= 1.0, "Validation Failed: Probabilities must be bounded 0-1"
            assert row['candidate_id'], "Validation Failed: Candidate ID missing"
            assert 'score' in row and row['score'] != '', "Validation Failed: Score missing"
            
        logger.info("✅ Validation Passed: Submission is perfect and ready for scoring!")
        
    except Exception as e:
        logger.error(f"❌ Validation Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TwinRank AI Offline Submission Pipeline")
    parser.add_argument("--job", type=str, required=True, help="Path to job_description.json")
    parser.add_argument("--candidates", type=str, required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", type=str, default="data/submissions", help="Output directory for CSV/YAML")
    
    args = parser.parse_args()
    run_submission(args.job, args.candidates, args.out)
