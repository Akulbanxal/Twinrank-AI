import time
from typing import List
from app.schemas.requests import JobDescription, Candidate
from app.schemas.responses import RankResponse, RankedCandidate
from app.utils.logger import logger
from app.utils.errors import InvalidInputException

from models.schemas import CandidateProfile, JobProfile
from models.pipelines.ranking_engine import ranking_engine
from models.explainability.explainer import explainer

def execute_ranking_pipeline(job: JobDescription, candidates: List[Candidate]) -> List[RankedCandidate]:
    """
    Connects the FastAPI requests to the core ML Hybrid Ranking Engine.
    """
    if not candidates:
        raise InvalidInputException("Candidates list cannot be empty")
        
    logger.info(f"API Bridge: Converting schemas for job {job.id}")
    
    # 1. Convert API schemas to ML internal schemas
    ml_job = JobProfile(
        id=job.id,
        title=job.title,
        description=job.description,
        required_skills=job.required_skills,
        seniority=job.seniority
    )
    
    ml_candidates = []
    for c in candidates:
        ml_candidates.append(CandidateProfile(
            id=c.id,
            name=c.name,
            resume_text=c.resume_text,
            skills=c.skills,
            experience_years=c.experience_years
        ))
        
    # 2. Execute actual ML Pipeline
    logger.info("API Bridge: Handing off to HybridRankingEngine...")
    scored_results = ranking_engine.rank_and_score(ml_job, ml_candidates)
    
    # 3. Format Explanations and Return to API layer
    final_results = []
    for rank, item in enumerate(scored_results, 1):
        cand = item["candidate"]
        score = item["score"]
        honeypot_prob = item["honeypot_prob"]
        features = item["features"]
        
        # Utilize dedicated explainability engine
        explanation_obj = explainer.generate_explanation(ml_job, cand, features, score)
        
        final_results.append(RankedCandidate(
            candidate_id=cand.id,
            score=round(score, 4),
            rank=rank,
            is_honeypot=(honeypot_prob > 0.5),
            explanation=explanation_obj,
            match_reasons=explanation_obj["strengths"]
        ))
        
    return final_results
