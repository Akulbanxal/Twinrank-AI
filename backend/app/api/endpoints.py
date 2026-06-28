from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.requests import RankRequest
from app.schemas.responses import RankResponse
from app.services.ml_service import rank_candidates
from app.utils.logger import logger
import os
import csv
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CSV_PATH = os.path.join(BASE_DIR, "data", "submissions", "submission.csv")
CANDIDATES_PATH = os.path.join(BASE_DIR, "data", "candidates.jsonl")

# Helper to read submission.csv
def read_submission_csv():
    rankings = {}
    if not os.path.exists(CSV_PATH):
        logger.warning(f"Submission CSV not found at: {CSV_PATH}")
        return rankings
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rankings[row["candidate_id"]] = {
                    "rank": int(row["rank"]),
                    "score": float(row["score"]),
                    "honeypot_probability": float(row["honeypot_probability"]),
                    "confidence_score": float(row["confidence_score"]),
                    "why_selected": row["why_selected"],
                    "strengths": [s.strip() for s in row["strengths_summary"].split("|") if s.strip()]
                }
    except Exception as e:
        logger.error(f"Error reading submission.csv: {e}")
    return rankings

# Helper to read profiles from candidates.jsonl for specific IDs
def read_candidate_profiles(target_ids):
    profiles = {}
    if not os.path.exists(CANDIDATES_PATH):
        logger.warning(f"Candidates JSONL not found at: {CANDIDATES_PATH}")
        return profiles
    try:
        with open(CANDIDATES_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                cand_id = data.get("candidate_id", "")
                if cand_id in target_ids:
                    profile = data.get("profile", {})
                    signals = data.get("redrob_signals", {})
                    skills = [s.get("name") for s in data.get("skills", []) if isinstance(s, dict) and "name" in s]
                    profiles[cand_id] = {
                        "name": profile.get("anonymized_name", f"Candidate {cand_id[:6]}"),
                        "title": profile.get("current_title", "Software Engineer"),
                        "summary": profile.get("summary", ""),
                        "skills": skills,
                        "experience_years": profile.get("years_of_experience", 0.0),
                        "current_industry": profile.get("current_industry"),
                        "response_rate": signals.get("recruiter_response_rate", 0.0) if signals.get("recruiter_response_rate") != -1 else 0.0,
                        "recruiter_saves": signals.get("saved_by_recruiters_30d", 0),
                        "notice_period_days": signals.get("notice_period_days", 0),
                        "expected_salary": signals.get("expected_salary_range_inr_lpa", {}).get("min", 0.0) if isinstance(signals.get("expected_salary_range_inr_lpa"), dict) else 0.0,
                        "is_honeypot_label": data.get("is_honeypot_label", None)
                    }
                    if len(profiles) == len(target_ids):
                        break
    except Exception as e:
        logger.error(f"Error reading candidates.jsonl: {e}")
    return profiles

router = APIRouter()

@router.post("/rank", response_model=RankResponse)
async def rank_job_candidates(request: RankRequest):
    """
    Ranks a list of candidates against a job description using the ML Engine.
    """
    logger.info(f"Received rank request for job {request.job_description.id} with {len(request.candidates)} candidates")
    try:
        result = rank_candidates(request.job_description, request.candidates)
        return result
    except Exception as e:
        logger.error(f"Error processing ranking: {e}")
        raise

@router.get("/candidates")
async def get_candidates():
    rankings = read_submission_csv()
    if not rankings:
        return []
    target_ids = set(rankings.keys())
    profiles = read_candidate_profiles(target_ids)
    
    joined = []
    for cand_id, rank_info in rankings.items():
        prof = profiles.get(cand_id, {
            "name": f"Candidate {cand_id[:6]}",
            "title": "Software Engineer",
            "summary": "",
            "skills": [],
            "experience_years": 0.0,
            "current_industry": "",
            "response_rate": 0.0,
            "recruiter_saves": 0,
            "notice_period_days": 0,
            "expected_salary": 0.0,
            "is_honeypot_label": None
        })
        joined.append({
            "id": cand_id,
            **rank_info,
            **prof
        })
    return sorted(joined, key=lambda x: x["rank"])

@router.get("/candidates/{candidate_id}")
async def get_candidate_detail(candidate_id: str):
    rankings = read_submission_csv()
    rank_info = rankings.get(candidate_id)
    
    # Read the individual profile
    profiles = read_candidate_profiles({candidate_id})
    prof = profiles.get(candidate_id)
    
    if not prof:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    score = rank_info.get("score", 0.5) if rank_info else 0.5
    honeypot_prob = rank_info.get("honeypot_probability", 0.0) if rank_info else 0.0
    exp = prof.get("experience_years", 0.0)
    resp = prof.get("response_rate", 0.0)
    sal = prof.get("expected_salary", 0.0)
    
    chart_data = {
        "capability": score,
        "growth": min(exp / 12.0, 1.0) if exp > 0 else 0.1,
        "behavior": resp if resp > 0 else 0.1,
        "trust": max(1.0 - honeypot_prob, 0.0),
        "market": min(max(sal / 100.0, 0.1), 1.0)
    }
    
    risks = []
    if honeypot_prob > 0.4:
        risks.append("Flagged for high honeypot risk (potential bot/synthetic profile)")
    if prof.get("notice_period_days", 0) > 60:
        risks.append(f"Notice period is relatively long ({prof.get('notice_period_days')} days)")
    if sal > 80.0:
        risks.append(f"Expected salary of {sal} LPA is on the higher end")
    if not risks:
        risks.append("No immediate risk flags detected.")
        
    return {
        "id": candidate_id,
        "name": prof["name"],
        "title": prof["title"],
        "score": score,
        "skills": prof["skills"],
        "experience_years": exp,
        "summary": prof["summary"],
        "is_honeypot": honeypot_prob > 0.4,
        "explainability": {
            "why_selected": rank_info.get("why_selected", "Matches key requirements.") if rank_info else "Matches key requirements.",
            "strengths": rank_info.get("strengths", ["Solid backend and logic foundations."]) if rank_info else ["Solid backend and logic foundations."],
            "risks": risks,
            "recruiter_notes": f"Candidate has {exp} years of experience and {len(prof['skills'])} skills. Notice period: {prof['notice_period_days']} days. Expected salary: {sal} LPA. Priority level: {'High' if score > 0.8 else 'Medium'}.",
            "confidence_score": rank_info.get("confidence_score", score * 100) if rank_info else score * 100
        },
        "chartData": chart_data
    }
