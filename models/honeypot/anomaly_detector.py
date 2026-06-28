import numpy as np
from typing import Dict, List, Tuple
import logging
from sklearn.ensemble import IsolationForest

from models.schemas import CandidateProfile

logger = logging.getLogger("twinrank.honeypot")

class HoneypotDetector:
    """
    Dedicated Honeypot Detection Module.
    Combines ensemble heuristics with anomaly detection to identify 
    fake, synthetic, or artificially stuffed profiles.
    """
    def __init__(self):
        logger.info("Initializing HoneypotDetector ensemble...")
        # In a full deployment, this IsolationForest is trained on offline data.
        # Here we initialize it for API readiness, but lean heavily on 
        # deterministic heuristics for the zero-shot offline evaluation constraint.
        self.iso_forest = IsolationForest(contamination=0.05, random_state=42)

    def detect(self, candidate: CandidateProfile, feature_scores: Dict[str, float] = None) -> float:
        """
        Evaluates a candidate profile against fraud heuristics.
        
        Args:
            candidate: Parsed CandidateProfile
            feature_scores: Optional dictionary of extracted NLP features
            
        Returns:
            honeypot_probability (float): 0.0 to 1.0 representing fraud risk.
        """
        anomaly_score = 0.0
        flags = []

        # 1. Impossible timelines
        if candidate.age is not None and candidate.experience_years > 0:
            working_age = candidate.age - 16 # Assuming typical minimum working age
            if candidate.experience_years > working_age:
                anomaly_score += 0.4
                flags.append(f"impossible_timeline: {candidate.experience_years}y exp at age {candidate.age}")

        # 2. Fake career growth
        if candidate.experience_years > 0:
            promos_per_year = candidate.promotions_count / candidate.experience_years
            # More than 1.5 promotions per year consistently is highly anomalous
            if promos_per_year > 1.5:
                anomaly_score += 0.3
                flags.append(f"hyper_promotion_velocity: {promos_per_year:.2f}/year")
        elif candidate.promotions_count > 3:
            # High promotions but 0 experience
            anomaly_score += 0.5
            flags.append("promotions_without_experience")

        # 3. Excessive skills (Skill Stuffing)
        skill_count = len(candidate.skills)
        if skill_count > 15:
            anomaly_score += 0.4
            flags.append(f"excessive_skill_stuffing: {skill_count} skills")
        elif skill_count > 8:
            anomaly_score += 0.15

        # 4. Contradictory titles
        if candidate.current_title:
            title_lower = candidate.current_title.lower()
            exec_keywords = ["cto", "ceo", "chief", "director", "vp", "president"]
            junior_keywords = ["junior", "intern", "trainee", "entry"]
            
            is_exec = any(kw in title_lower for kw in exec_keywords)
            is_junior = any(kw in title_lower for kw in junior_keywords)
            
            if is_exec and is_junior:
                anomaly_score += 0.6
                flags.append(f"contradictory_titles: '{candidate.current_title}'")

        # 5. Unrealistic perfection
        if feature_scores:
            # Check if capability features are suspiciously perfect
            cap_scores = [v for k, v in feature_scores.items() if k.startswith("cap_")]
            if len(cap_scores) >= 3 and np.mean(cap_scores) > 0.98:
                anomaly_score += 0.25
                flags.append(f"synthetic_perfection: mean cap score {np.mean(cap_scores):.2f}")

        # Map heuristic anomaly_score to a bounded 0-1 probability 
        # Using a simple clamp for hard rules, or could use 1 - exp(-k * score)
        probability = float(np.clip(anomaly_score, 0.0, 1.0))
        
        if probability >= 0.4:
            logger.warning(
                f"Honeypot risk high for candidate {candidate.id}: "
                f"Prob={probability:.2f}. Flags: {flags}"
            )
        elif probability > 0.0:
            logger.debug(f"Honeypot flags for {candidate.id}: {flags}")

        return probability

# Export singleton instance
honeypot_detector = HoneypotDetector()
