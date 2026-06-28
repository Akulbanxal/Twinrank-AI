import json
import os
import logging
from typing import List, Dict, Optional
from pydantic import ValidationError
from models.schemas import CandidateProfile, JobProfile

logger = logging.getLogger("twinrank.data")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

class DataIngestor:
    """
    Handles robust ingestion, validation, and caching of ML datasets.
    """
    def __init__(self):
        # Cache mapping file_path -> parsed objects to avoid re-parsing
        self._candidates_cache: Dict[str, List[CandidateProfile]] = {}
        self._jobs_cache: Dict[str, List[JobProfile]] = {}

    def load_candidates(self, filepath: str) -> List[CandidateProfile]:
        """
        Loads candidate data from a JSONL file.
        - Validates against CandidateProfile schema
        - Rejects and logs malformed lines
        - Caches the final list of typed objects
        """
        if filepath in self._candidates_cache:
            logger.info(f"DataIngestor: Cache hit for {filepath}")
            return self._candidates_cache[filepath]

        if not os.path.exists(filepath):
            logger.error(f"DataIngestor: File not found -> {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")

        valid_candidates = []
        malformed_count = 0

        logger.info(f"DataIngestor: Parsing candidates from {filepath}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    
                    profile = data.get("profile", {})
                    signals = data.get("redrob_signals", {})
                    
                    mapped_data = {
                        "id": data.get("candidate_id", ""),
                        "name": profile.get("anonymized_name", ""),
                        "resume_text": profile.get("summary", ""),
                        "skills": [s.get("name") for s in data.get("skills", []) if isinstance(s, dict) and "name" in s],
                        "experience_years": profile.get("years_of_experience", 0.0),
                        "current_title": profile.get("current_title"),
                        "current_industry": profile.get("current_industry"),
                        "education_level": data.get("education", [{}])[0].get("degree") if data.get("education") else None,
                        "response_rate": signals.get("recruiter_response_rate", 0.0) if signals.get("recruiter_response_rate") != -1 else 0.0,
                        "recruiter_saves": signals.get("saved_by_recruiters_30d", 0),
                        "last_active_days_ago": 0,
                        "interview_completion_rate": signals.get("interview_completion_rate", 0.0) if signals.get("interview_completion_rate") != -1 else 0.0,
                        "expected_salary": signals.get("expected_salary_range_inr_lpa", {}).get("min", 0.0) if isinstance(signals.get("expected_salary_range_inr_lpa"), dict) else 0.0,
                        "notice_period_days": signals.get("notice_period_days", 0),
                        "is_honeypot_label": data.get("is_honeypot_label", None)
                    }
                    
                    candidate = CandidateProfile(**mapped_data)
                    valid_candidates.append(candidate)
                except json.JSONDecodeError as e:
                    logger.warning(f"Malformed JSON on line {line_no} in {filepath}: {e}")
                    malformed_count += 1
                except ValidationError as e:
                    logger.warning(f"Schema validation failed on line {line_no} in {filepath}: {e}")
                    malformed_count += 1

        logger.info(
            f"DataIngestor: Loaded {len(valid_candidates)} valid candidates. "
            f"Rejected {malformed_count} malformed records."
        )
        
        self._candidates_cache[filepath] = valid_candidates
        return valid_candidates

    def clear_cache(self):
        """Clears memory caches."""
        self._candidates_cache.clear()
        self._jobs_cache.clear()
        logger.info("DataIngestor: Cache cleared.")

# Export a singleton instance for use across the pipeline
ingestor = DataIngestor()
