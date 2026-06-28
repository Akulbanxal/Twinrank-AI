import os
import json
import asyncio
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.api.endpoints import get_candidates, get_candidate_detail

async def generate_static():
    print("Generating static JSON files for frontend deployment...")
    
    # 1. Ensure target directory exists
    out_dir = "frontend/public/api/candidates"
    os.makedirs(out_dir, exist_ok=True)
    
    # 2. Get list of candidates
    candidates = await get_candidates()
    
    # Save candidates.json
    candidates_json_path = "frontend/public/api/candidates.json"
    with open(candidates_json_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2)
    print(f"Saved {candidates_json_path}")
    
    # 3. Save each candidate detail
    for cand in candidates:
        cand_id = cand["id"]
        detail = await get_candidate_detail(cand_id)
        
        detail_json_path = os.path.join(out_dir, f"{cand_id}.json")
        with open(detail_json_path, 'w', encoding='utf-8') as f:
            json.dump(detail, f, indent=2)
            
    print("Successfully generated all static candidates API endpoints!")

if __name__ == "__main__":
    asyncio.run(generate_static())
