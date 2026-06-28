import numpy as np
from typing import Dict, List, Any
import logging

from models.schemas import CandidateProfile, JobProfile

logger = logging.getLogger("twinrank.explainability")

class ExplainabilityEngine:
    """
    Generates human-readable, recruiter-friendly explanations for candidate rankings.
    Grounds all text strictly in extracted feature evidence (no hallucinations).
    """
    def __init__(self):
        pass

    def generate_explanation(self, job: JobProfile, candidate: CandidateProfile, features: Dict[str, Any], score: float) -> Dict[str, Any]:
        """
        Translates raw features and scores into a structured explanation format.
        """
        why_selected = self._generate_why_selected(job, candidate, features)
        strengths = self._generate_strengths(features, candidate)
        risks = self._generate_risks(features, candidate)
        notes = self._generate_recruiter_notes(features, candidate, score)
        
        # Confidence score derived from overall score and heavily penalized by risk/fraud signals
        base_confidence = min(1.0, score * 1.1)
        risk_penalty = features.get("risk_salary_mismatch", 0.0) + features.get("risk_notice_penalty", 0.0)
        fraud_penalty = sum([v for k, v in features.items() if k.startswith("fraud_")])
        
        confidence = float(np.clip(base_confidence - risk_penalty - fraud_penalty, 0.0, 1.0))

        return {
            "why_selected": why_selected,
            "strengths": strengths,
            "risks": risks,
            "recruiter_notes": notes,
            "confidence_score": round(confidence * 100, 1) # Percentage 0-100
        }

    def _generate_why_selected(self, job: JobProfile, candidate: CandidateProfile, features: Dict[str, Any]) -> str:
        # Experience and Title
        title = candidate.current_title if candidate.current_title else "their field"
        exp = f"{candidate.experience_years:.1f} years experience in {title}"
        
        # 2-3 specific matched skills
        job_skills = {s.lower() for s in job.required_skills}
        matched = [s for s in candidate.skills if s.lower() in job_skills]
        if not matched:
            matched = candidate.skills[:3]
        
        skills_str = ""
        if len(matched) >= 3:
            skills_str = f" with {matched[0]}, {matched[1]}, and {matched[2]}"
        elif len(matched) == 2:
            skills_str = f" with {matched[0]} and {matched[1]}"
        elif len(matched) == 1:
            skills_str = f" with {matched[0]}"
            
        # Behavioral signal
        behavior = ""
        if candidate.response_rate > 0.0:
            behavior = f"Strong recruiter responsiveness ({int(candidate.response_rate * 100)}%)"
        elif candidate.recruiter_saves > 0:
            behavior = f"Saved by {candidate.recruiter_saves} recruiters recently"
        else:
            behavior = "Solid platform activity"
            
        # Optional concern
        concern = ""
        if candidate.notice_period_days and candidate.notice_period_days >= 30:
            concern = f", minor concern: {candidate.notice_period_days}-day notice"
        elif features.get("risk_salary_mismatch", 0.0) > 0.0:
            concern = f", minor concern: high salary expectation"
            
        return f"{exp}{skills_str}. {behavior}{concern}."

    def _generate_strengths(self, features: Dict[str, Any], candidate: CandidateProfile) -> List[str]:
        strengths = []
        if features.get("cap_industry_match", 0.0) == 1.0:
            strengths.append(f"Direct experience in required industry")
            
        if features.get("cap_title_sim", 0.0) > 0.8:
            strengths.append(f"Current title ({candidate.current_title}) is highly relevant")
            
        # Evidence-backed transferable skills
        mappings = features.get("transfer_mappings", [])
        if mappings:
            # Limit to top 3 to keep it concise
            for m in mappings[:3]:
                strengths.append(f"Transferable skill: '{m['matched_skill']}' fulfills requirement for '{m['required_skill']}'")
                
        if features.get("beh_response_rate", 0.0) > 0.8:
            strengths.append(f"Highly responsive to recruiter outreach ({(features['beh_response_rate']*100):.0f}%)")
            
        return strengths

    def _generate_risks(self, features: Dict[str, Any], candidate: CandidateProfile) -> List[str]:
        risks = []
        if features.get("risk_salary_mismatch", 0.0) > 0.0:
            mismatch_pct = features['risk_salary_mismatch'] * 100
            risks.append(f"Expected salary exceeds budget by {mismatch_pct:.0f}%")
            
        if features.get("risk_notice_penalty", 0.0) > 0.5:
            risks.append(f"Long notice period ({candidate.notice_period_days} days)")
            
        if features.get("beh_activity_freshness", 1.0) < 0.2:
            risks.append("Candidate has been inactive recently on the platform")
            
        if any(v > 0 for k, v in features.items() if k.startswith("fraud_")):
            risks.append("Automated flags detected unusual profile patterns (e.g., potential skill stuffing or timeline inconsistencies)")
            
        return risks

    def _generate_recruiter_notes(self, features: Dict[str, Any], candidate: CandidateProfile, score: float) -> str:
        if any(v > 0.5 for k, v in features.items() if k.startswith("fraud_")):
            return "CAUTION: High risk profile. Please manually verify experience timelines and skill claims before outreach."
            
        if score > 0.85:
            return "Fast-track candidate. Extremely strong match across capability and growth dimensions. Prioritize immediate outreach."
        elif score > 0.65:
            return "Solid candidate. Review transferable skills and verify salary expectations before proceeding."
        else:
            return "Borderline match. May require upskilling or compromises on core requirements."

# Singleton export
explainer = ExplainabilityEngine()
