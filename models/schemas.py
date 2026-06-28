from pydantic import BaseModel, Field
from typing import List, Optional

class CandidateProfile(BaseModel):
    id: str = Field(..., description="Unique identifier for the candidate")
    name: str = Field(..., description="Full name of the candidate")
    resume_text: str = Field(..., description="Raw or parsed resume text")
    skills: List[str] = Field(default_factory=list, description="Explicitly extracted skills")
    experience_years: float = Field(0.0, description="Total years of professional experience")
    
    # Capability & General
    current_title: Optional[str] = None
    current_industry: Optional[str] = None
    education_level: Optional[str] = None
    
    # Growth
    promotions_count: int = Field(0, description="Number of times promoted")
    company_scales: List[int] = Field(default_factory=list, description="Sizes of previous companies")
    
    # Behavior
    response_rate: float = Field(0.0, description="0.0 to 1.0 reply rate to recruiters")
    recruiter_saves: int = Field(0, description="Times saved by other recruiters")
    last_active_days_ago: int = Field(0, description="Days since last platform activity")
    interview_completion_rate: float = Field(0.0, description="Percentage of interviews attended vs scheduled")
    
    # Risk
    expected_salary: float = Field(0.0, description="Expected annual salary")
    notice_period_days: int = Field(0, description="Days required before starting")
    
    # Fraud Detection Context
    age: Optional[int] = Field(None, description="Age if available, for anomaly detection")
    is_honeypot_label: Optional[bool] = Field(None, description="Ground truth label for training")

class JobProfile(BaseModel):
    id: str
    title: str
    description: str
    required_skills: List[str] = Field(default_factory=list)
    seniority: Optional[str] = None
    industry: Optional[str] = None
    required_education: Optional[str] = None
    min_salary: float = Field(0.0)
    max_salary: float = Field(0.0)
