import numpy as np
from typing import Dict, Any, List
from collections import Counter
import re
import logging

from models.schemas import CandidateProfile, JobProfile

logger = logging.getLogger("twinrank.features")

class FeatureEngineer:
    """
    Advanced Feature Engineering Pipeline computing Capability, Growth, 
    Behavior, Risk, and Fraud signals.
    """
    def __init__(self):
        pass

    def _get_model(self):
        pass

    def compute_all_features(self, job: JobProfile, candidate: CandidateProfile) -> Dict[str, float]:
        """Orchestrates all feature extraction modules."""
        features = {}
        features.update(self._extract_capability_features(job, candidate))
        features.update(self._extract_growth_features(candidate))
        features.update(self._extract_behavior_features(candidate))
        features.update(self._extract_risk_features(job, candidate))
        features.update(self._extract_fraud_features(candidate, features))
        
        return features

    def _get_semantic_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        # Fast fallback: Token-based Jaccard similarity instead of heavy SentenceTransformer
        # Guarantees < 5 minute runtime on CPU for 100,000 records.
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return float(len(intersection)) / max(1, len(union))

    def _extract_capability_features(self, job: JobProfile, candidate: CandidateProfile) -> Dict[str, float]:
        # 1. Skill Overlap (Jaccard)
        j_skills = set(s.lower() for s in job.required_skills)
        c_skills = set(s.lower() for s in candidate.skills)
        overlap = len(j_skills.intersection(c_skills))
        skill_overlap = overlap / max(len(j_skills), 1)

        # 2. Semantic Skill Similarity (treating lists as a single semantic document)
        j_skill_doc = " ".join(j_skills)
        c_skill_doc = " ".join(c_skills)
        semantic_skill_sim = self._get_semantic_similarity(j_skill_doc, c_skill_doc)

        # 3. Title Similarity
        title_sim = self._get_semantic_similarity(job.title, candidate.current_title or "")

        # 4. Industry Match
        industry_match = 1.0 if (job.industry and candidate.current_industry and job.industry.lower() == candidate.current_industry.lower()) else 0.0

        # 5. Education Relevance
        # Simple exact match logic for MVP, could be expanded to hierarchy (Bachelors < Masters)
        edu_match = 1.0 if (job.required_education and candidate.education_level and job.required_education.lower() in candidate.education_level.lower()) else 0.0

        return {
            "cap_skill_overlap": float(skill_overlap),
            "cap_semantic_skill_sim": float(semantic_skill_sim),
            "cap_title_sim": float(title_sim),
            "cap_industry_match": float(industry_match),
            "cap_education_match": float(edu_match)
        }

    def _extract_growth_features(self, candidate: CandidateProfile) -> Dict[str, float]:
        # 1. Promotion Velocity: promos / years of experience
        velocity = candidate.promotions_count / max(candidate.experience_years, 1.0)
        
        # 2. Company Scale Progression: positive if they moved to bigger companies
        scales = candidate.company_scales
        scale_progression = 0.0
        if len(scales) > 1:
            diffs = [scales[i] - scales[i-1] for i in range(1, len(scales))]
            scale_progression = float(np.mean(diffs))

        return {
            "growth_promotion_velocity": float(velocity),
            "growth_scale_progression": scale_progression
        }

    def _extract_behavior_features(self, candidate: CandidateProfile) -> Dict[str, float]:
        # Simple pass-through or normalization of behavior metrics
        freshness_score = max(0.0, 1.0 - (candidate.last_active_days_ago / 365.0))
        
        return {
            "beh_response_rate": candidate.response_rate,
            "beh_recruiter_saves_log": float(np.log1p(candidate.recruiter_saves)), # log scale for long tail
            "beh_activity_freshness": freshness_score,
            "beh_interview_completion": candidate.interview_completion_rate
        }

    def _extract_risk_features(self, job: JobProfile, candidate: CandidateProfile) -> Dict[str, float]:
        # 1. Salary Mismatch
        salary_mismatch = 0.0
        if candidate.expected_salary > 0 and job.max_salary > 0:
            if candidate.expected_salary > job.max_salary:
                # Penalty ratio
                salary_mismatch = (candidate.expected_salary - job.max_salary) / job.max_salary
                
        # 2. Notice period penalty
        notice_penalty = candidate.notice_period_days / 90.0 # Normalize against 3 months
        
        # 3. Inactivity penalty (distinct from freshness)
        inactivity_penalty = 1.0 if candidate.last_active_days_ago > 180 else 0.0

        return {
            "risk_salary_mismatch": float(salary_mismatch),
            "risk_notice_penalty": float(notice_penalty),
            "risk_inactivity_penalty": float(inactivity_penalty)
        }

    def _extract_fraud_features(self, candidate: CandidateProfile, current_features: Dict[str, float]) -> Dict[str, float]:
        # 1. Impossible experience
        imp_exp = 0.0
        if candidate.age is not None:
            # e.g., 20 years experience at age 30 means they started at 10. Flag as suspicious.
            if candidate.experience_years > (candidate.age - 18):
                imp_exp = 1.0
                
        # 2. Skill stuffing
        skill_count = len(candidate.skills)
        skill_stuffing = 1.0 if skill_count > 100 else (skill_count / 100.0)
        
        # 3. Keyword spam
        words = re.findall(r'\w+', candidate.resume_text.lower())
        word_counts = Counter(words)
        # Find if any word is repeated unusually often (excluding stop words normally, simplified here)
        max_repeats = max(word_counts.values()) if word_counts else 0
        keyword_spam = 1.0 if max_repeats > 50 else (max_repeats / 50.0)
        
        # 4. Synthetic Perfection
        # If all capability features are perfectly 1.0, it's highly suspicious
        cap_scores = [v for k, v in current_features.items() if k.startswith("cap_")]
        syn_perf = 1.0 if (len(cap_scores) > 0 and sum(cap_scores)/len(cap_scores) > 0.98) else 0.0

        return {
            "fraud_impossible_experience": float(imp_exp),
            "fraud_skill_stuffing": float(skill_stuffing),
            "fraud_keyword_spam": float(keyword_spam),
            "fraud_synthetic_perfection": float(syn_perf)
        }

# Singleton accessor
feature_engineer = FeatureEngineer()
