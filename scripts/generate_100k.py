import json
import random
import sys

skills_pool = [
    "python", "java", "c++", "go", "javascript", "typescript", "react", "node.js",
    "aws", "gcp", "azure", "docker", "kubernetes", "sql", "postgresql", "mysql",
    "mongodb", "redis", "kafka", "rabbitmq", "fastapi", "django", "spring boot"
]

def generate_candidates(count, filepath):
    print(f"Generating {count} candidates...")
    with open(filepath, 'w', encoding='utf-8') as f:
        for i in range(count):
            age = random.randint(22, 60)
            exp = max(0, age - 22 + random.randint(-2, 2))
            
            # Inject some honeypots (impossible experience)
            if random.random() < 0.05:  # 5% honeypot
                exp = age + 5 

            cand = {
                "id": f"cand_{i}",
                "name": f"Candidate {i}",
                "resume_text": "Experienced software engineer.",
                "skills": random.sample(skills_pool, k=random.randint(3, 15)),
                "current_title": random.choice(["Backend Developer", "Senior Engineer", "CTO", "Junior Developer"]),
                "current_industry": "technology",
                "education_level": random.choice(["bachelors", "masters", "phd", "none"]),
                "experience_years": exp,
                "promotions_count": random.randint(0, 5),
                "company_scales": [random.randint(10, 5000) for _ in range(random.randint(1, 4))],
                "expected_salary": random.randint(60000, 200000),
                "notice_period_days": random.choice([14, 30, 60, 90]),
                "last_active_days_ago": random.randint(0, 300),
                "response_rate": random.uniform(0.1, 1.0),
                "recruiter_saves": random.randint(0, 50),
                "interview_completion_rate": random.uniform(0.4, 1.0),
                "age": age
            }
            f.write(json.dumps(cand) + "\n")
    print(f"Saved to {filepath}")

if __name__ == '__main__':
    generate_candidates(100000, "data/candidates.jsonl")
