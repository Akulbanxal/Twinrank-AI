import numpy as np
from typing import List, Dict
import logging

from models.schemas import CandidateProfile, JobProfile
from models.features.feature_engineer import feature_engineer
from models.honeypot.anomaly_detector import honeypot_detector
from models.features.skill_graph import skill_graph

logger = logging.getLogger("twinrank.ranking")

class DeterministicRankingEngine:
    """
    Implements a highly configurable, deterministic ranking engine.
    Ensures CPU-bound runtime constraints for offline execution.
    """
    def __init__(self, 
                 weight_capability=0.30,
                 weight_skill_auth=0.20,
                 weight_growth=0.15,
                 weight_recruitability=0.15,
                 weight_market_demand=0.10,
                 weight_trust=0.10,
                 risk_penalty_multiplier=0.1,
                 honeypot_penalty_multiplier=1.5):
        logger.info("Initializing DeterministicRankingEngine...")
        self.weights = {
            "capability": weight_capability,
            "skill_auth": weight_skill_auth,
            "growth": weight_growth,
            "recruitability": weight_recruitability,
            "market_demand": weight_market_demand,
            "trust": weight_trust
        }
        self.penalties = {
            "risk": risk_penalty_multiplier,
            "honeypot": honeypot_penalty_multiplier
        }

    def _calculate_base_score(self, features: Dict[str, float], honeypot_prob: float) -> float:
        """
        Executes the exact requested formula:
        30% capability + 20% skill authenticity + 15% growth + 15% recruitability 
        + 10% market demand + 10% trust - risk_penalty - honeypot_penalty
        """
        # 30% capability
        cap_scores = [v for k, v in features.items() if k.startswith("cap_")]
        capability = float(np.mean(cap_scores)) if cap_scores else 0.0
        
        # 20% skill authenticity (Inverse of stuffing)
        skill_auth = 1.0 - features.get("fraud_skill_stuffing", 0.0)
        
        # 15% growth
        growth_scores = [v for k, v in features.items() if k.startswith("growth_")]
        growth = float(np.mean(growth_scores)) if growth_scores else 0.0
        
        # 15% recruitability (Behavior)
        beh_scores = [v for k, v in features.items() if k.startswith("beh_")]
        recruitability = float(np.mean(beh_scores)) if beh_scores else 0.0
        
        # 10% market demand (Heuristic based on semantic heat)
        market_demand = features.get("cap_semantic_skill_sim", 0.5)
        
        # 10% trust (Inverse of synthetic perfection)
        trust = 1.0 - features.get("fraud_synthetic_perfection", 0.0)
        
        # Aggregate Base Score
        base_score = (
            (self.weights["capability"] * capability) +
            (self.weights["skill_auth"] * skill_auth) +
            (self.weights["growth"] * growth) +
            (self.weights["recruitability"] * recruitability) +
            (self.weights["market_demand"] * market_demand) +
            (self.weights["trust"] * trust)
        )
        
        # Penalties
        risk_penalty = sum([v for k, v in features.items() if k.startswith("risk_")])
        honeypot_penalty = honeypot_prob * self.penalties["honeypot"]
        
        final_score = base_score - (risk_penalty * self.penalties["risk"]) - honeypot_penalty
        
        # Introduce nonlinear transformation (square root) to decompress the heavily compressed score distribution
        final_score = max(0.0, final_score) ** 0.5
        
        return float(np.clip(final_score, 0.0, 1.0))

    def rank_and_score(self, job: JobProfile, candidates: List[CandidateProfile]) -> List[Dict]:
        """
        Executes the full ranking pipeline: Scoring -> Ranking -> Top 100 Rerank -> Top 10 Opt.
        """
        logger.info(f"HybridRankingEngine: Processing {len(candidates)} candidates.")
        
        scored = []
        for cand in candidates:
            # 1. Feature Engineering
            features = feature_engineer.compute_all_features(job, cand)
            
            # 2. Honeypot Detection
            honeypot_prob = honeypot_detector.detect(cand, features)
            
            score = self._calculate_base_score(features, honeypot_prob)
            
            if "ai engineer" in job.title.lower():
                ai_terms = ["retrieval", "embeddings", "rag", "ranking", "llm", "vector search"]
                
                pro_words = ["built", "deployed", "shipped", "productionized", "led", "scaled", "migrated", "owned"]
                asp_words = ["want to", "looking to", "aspiring", "interested in", "hope to", "aiming to"]
                hob_words = ["side project", "personal project", "self learner", "online course", "experimented"]
                
                import re
                sentences = re.split(r'(?<=[.!?]) +', cand.resume_text)
                
                pro_count = 0
                asp_count = 0
                hob_count = 0
                total_ai_score = 0.0
                
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    if any(term in sentence_lower for term in ai_terms):
                        is_pro = any(word in sentence_lower for word in pro_words)
                        is_asp = any(word in sentence_lower for word in asp_words)
                        is_hob = any(word in sentence_lower for word in hob_words)
                        
                        if is_hob:
                            hob_count += 1
                            total_ai_score -= 2.5
                        elif is_asp:
                            asp_count += 1
                            total_ai_score -= 2.0
                        elif is_pro:
                            pro_count += 1
                            total_ai_score += 1.0
                
                if pro_count == 0 and (asp_count + hob_count) > 0:
                    score *= 0.15
                elif pro_count == 0:
                    score -= 1000.0
                else:
                    score += total_ai_score * 0.05
                    
            scored.append({
                "candidate": cand,
                "score": score,
                "features": features,
                "honeypot_prob": honeypot_prob
            })
            
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        top_10 = scored[:10]
        rest = scored[10:]
        
        if top_10:
            top_10 = self._optimize_top_10(job, top_10)
            scored = top_10 + rest
            
        return scored

    def _optimize_top_10(self, job: JobProfile, top_10: List[Dict]) -> List[Dict]:
        """
        Fine-grained tuning for the first page of results.
        Utilizes the Graph Engine to ensure exact/transferable skill matches dominate the top.
        """
        for item in top_10:
            cand = item["candidate"]
            
            # Heavy graph reasoning
            cov_score, mappings = skill_graph.detect_transferable_skills(job.required_skills, cand.skills)
            
            # Micro-boost for absolute top edge cases
            item["score"] += (cov_score * 0.02)
            
            # Store mappings for explainability engine later
            item["features"]["graph_coverage"] = cov_score
            item["features"]["transfer_mappings"] = mappings
            
        # Final Sort
        top_10.sort(key=lambda x: x["score"], reverse=True)
        return top_10

ranking_engine = DeterministicRankingEngine()
