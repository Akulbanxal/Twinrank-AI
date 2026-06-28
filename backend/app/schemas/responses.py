from pydantic import BaseModel
from typing import List, Dict, Any

class RankedCandidate(BaseModel):
    candidate_id: str
    score: float
    rank: int
    is_honeypot: bool
    explanation: Dict[str, Any]
    match_reasons: List[str]

class RankResponse(BaseModel):
    job_id: str
    ranked_candidates: List[RankedCandidate]
    processing_time_ms: float
    cached: bool = False
