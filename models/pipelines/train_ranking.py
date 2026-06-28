import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
import os
import logging
from typing import List, Dict

logger = logging.getLogger("twinrank.training")

class RankingTrainer:
    """
    Trains a Pairwise Learning-to-Rank model (LightGBMRanker) to optimize NDCG.
    """
    def __init__(self, model_path: str = "models/weights/lgbm_ranker.joblib"):
        self.model_path = model_path
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
    def generate_synthetic_data(self, num_queries: int = 100, candidates_per_query: int = 50):
        """
        Generates synthetic feature matrices and relevance labels for training,
        grouped by queries (jobs).
        """
        logger.info(f"Generating synthetic training data: {num_queries} queries, {candidates_per_query} per query.")
        
        X_list, y_list, group_list = [], [], []
        num_features = 15
        
        for q in range(num_queries):
            # Random feature distributions
            features = np.random.rand(candidates_per_query, num_features)
            
            # Ground truth relevance (0 to 4, where 4 is highly relevant)
            # Simulated based heavily on the first few capability features
            relevance = (features[:, 0]*2 + features[:, 1]*1.5 + features[:, 2] - np.random.rand(candidates_per_query)).clip(0, 4)
            relevance = np.round(relevance).astype(int)
            
            X_list.append(features)
            y_list.append(relevance)
            group_list.append(candidates_per_query)
            
        X = np.vstack(X_list)
        y = np.concatenate(y_list)
        groups = np.array(group_list)
        
        # Hardcoded feature matrix columns expected from our pipeline
        feature_names = [
            "cap_skill_overlap", "cap_semantic_skill_sim", "cap_title_sim", 
            "cap_industry_match", "cap_education_match", "growth_promotion_velocity", 
            "growth_scale_progression", "beh_response_rate", "beh_recruiter_saves_log", 
            "beh_activity_freshness", "beh_interview_completion", "risk_salary_mismatch", 
            "risk_notice_penalty", "risk_inactivity_penalty", "fraud_skill_stuffing"
        ]
        
        return pd.DataFrame(X, columns=feature_names), y, groups

    def train_and_save(self):
        """Trains LightGBM pairwise ranker optimizing specifically for NDCG@10, NDCG@50."""
        X_train, y_train, groups_train = self.generate_synthetic_data(num_queries=800)
        X_val, y_val, groups_val = self.generate_synthetic_data(num_queries=200)
        
        logger.info("Training LightGBMRanker (objective: lambdarank, metric: ndcg)...")
        
        ranker = lgb.LGBMRanker(
            objective="lambdarank",
            metric="ndcg",
            boosting_type="gbdt",
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=42
        )
        
        # Fit optimizing directly for NDCG at cutoffs
        ranker.fit(
            X_train, y_train,
            group=groups_train,
            eval_set=[(X_val, y_val)],
            eval_group=[groups_val],
            eval_at=[10, 50],
            callbacks=[lgb.early_stopping(stopping_rounds=15)]
        )
        
        logger.info(f"Saving trained LightGBM model to {self.model_path}")
        joblib.dump(ranker, self.model_path)
        logger.info("Model serialized and saved successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    trainer = RankingTrainer()
    trainer.train_and_save()
