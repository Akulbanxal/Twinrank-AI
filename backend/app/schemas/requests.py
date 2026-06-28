from pydantic import BaseModel, Field
from typing import List, Optional

class JobDescription(BaseModel):
    id: str = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Full text description")
    required_skills: List[str] = Field(default_factory=list)
    seniority: Optional[str] = None

class Candidate(BaseModel):
    id: str = Field(..., description="Unique candidate identifier")
    name: str
    resume_text: str = Field(..., description="Full resume text")
    skills: List[str] = Field(default_factory=list)
    experience_years: float = Field(0.0)

class RankRequest(BaseModel):
    job_description: JobDescription
    candidates: List[Candidate] = Field(..., description="List of candidates to rank (max 1000)")
