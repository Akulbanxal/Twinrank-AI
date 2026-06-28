import time
from typing import List
from app.schemas.requests import JobDescription, Candidate
from app.schemas.responses import RankResponse, RankedCandidate
from app.services.ranking_service import execute_ranking_pipeline
from app.services.cache_service import cache_store
from app.utils.logger import logger

def rank_candidates(job_description: JobDescription, candidates: List[Candidate]) -> RankResponse:
    """
    Entrypoint for ML Service. Handles caching and orchestration.
    """
    start_time = time.time()
    
    # Prepare cache key (simple extract of ids)
    cache_key = {
        "job_id": job_description.id,
        "candidate_ids": sorted([c.id for c in candidates])
    }
    
    cached_result = cache_store.get(cache_key)
    if cached_result:
        logger.info("Returning cached ranking result")
        processing_time = (time.time() - start_time) * 1000
        return RankResponse(
            job_id=job_description.id,
            ranked_candidates=cached_result,
            processing_time_ms=processing_time,
            cached=True
        )
        
    # Execute actual ML pipeline
    ranked_candidates = execute_ranking_pipeline(job_description, candidates)
    
    # Save to cache
    cache_store.set(cache_key, ranked_candidates)
    
    processing_time = (time.time() - start_time) * 1000
    
    return RankResponse(
        job_id=job_description.id,
        ranked_candidates=ranked_candidates,
        processing_time_ms=processing_time,
        cached=False
    )
