from typing import Dict, List, Set, Tuple
import logging

logger = logging.getLogger("twinrank.skillgraph")

class SkillOntologyGraph:
    """
    Skill Graph Reasoning Engine.
    Handles skill normalization, adjacency logic, and transferable skill detection.
    """
    def __init__(self):
        # Adjacency list: node -> {neighbor: transferability_weight}
        self.graph: Dict[str, Dict[str, float]] = {}
        self._build_seed_ontology()

    def _build_seed_ontology(self):
        """Pre-populates the ontology with industry standard transferable skills and categories."""
        edges = [
            # Frontend
            ("react", "next.js", 0.9),
            ("react", "javascript", 0.8),
            ("next.js", "javascript", 0.8),
            ("vue", "javascript", 0.8),
            ("react", "vue", 0.7), # High transferability between frameworks
            
            # Backend / Data
            ("kafka", "distributed messaging", 0.9),
            ("rabbitmq", "distributed messaging", 0.9),
            ("kafka", "rabbitmq", 0.8),
            ("kafka", "java", 0.6),
            
            # AI / ML
            ("pytorch", "deep learning", 0.9),
            ("pytorch", "machine learning", 0.8),
            ("pytorch", "python", 0.8),
            ("tensorflow", "deep learning", 0.9),
            ("tensorflow", "pytorch", 0.8), # Highly transferable paradigms
            ("python", "machine learning", 0.7),
            
            # Cloud & DevOps
            ("aws", "cloud computing", 0.9),
            ("gcp", "cloud computing", 0.9),
            ("azure", "cloud computing", 0.9),
            ("aws", "gcp", 0.7),
            ("aws", "azure", 0.7),
            
            # DBs
            ("sql", "databases", 0.9),
            ("postgresql", "sql", 0.95),
            ("mysql", "sql", 0.95),
            ("postgresql", "mysql", 0.8),
            
            # Infrastructure
            ("docker", "kubernetes", 0.8),
            ("docker", "containers", 0.95),
            ("kubernetes", "containers", 0.9),
        ]
        
        for n1, n2, weight in edges:
            self._add_edge(n1, n2, weight)
        
        logger.info(f"SkillOntologyGraph initialized with {len(self.graph)} canonical nodes.")

    def _add_edge(self, node1: str, node2: str, weight: float):
        if node1 not in self.graph:
            self.graph[node1] = {}
        if node2 not in self.graph:
            self.graph[node2] = {}
        # Undirected graph for bi-directional transferability
        self.graph[node1][node2] = weight
        self.graph[node2][node1] = weight

    def normalize_skill(self, skill: str) -> str:
        """Normalizes skill text to its canonical graph representation."""
        if not skill:
            return ""
        s = skill.lower().strip()
        # Common aliases dictionary
        aliases = {
            "js": "javascript",
            "reactjs": "react",
            "react.js": "react",
            "nextjs": "next.js",
            "postgres": "postgresql",
            "k8s": "kubernetes",
            "ml": "machine learning",
            "dl": "deep learning",
            "amazon web services": "aws",
            "google cloud": "gcp",
            "google cloud platform": "gcp"
        }
        return aliases.get(s, s)

    def get_adjacency_similarity(self, skill1: str, skill2: str) -> float:
        """
        Returns the similarity score between two skills utilizing the ontology.
        - 1.0 if identical.
        - Direct edge weight if adjacent.
        - Product of weights if 1-hop away.
        - 0.0 otherwise.
        """
        s1 = self.normalize_skill(skill1)
        s2 = self.normalize_skill(skill2)
        
        if not s1 or not s2:
            return 0.0
            
        if s1 == s2:
            return 1.0
            
        # Direct edge match
        if s1 in self.graph and s2 in self.graph[s1]:
            return self.graph[s1][s2]
            
        # 1-hop (common neighbor/parent category)
        max_sim = 0.0
        if s1 in self.graph and s2 in self.graph:
            for neighbor, w1 in self.graph[s1].items():
                if neighbor in self.graph[s2]:
                    w2 = self.graph[s2][neighbor]
                    max_sim = max(max_sim, w1 * w2)
                    
        return float(max_sim)

    def detect_transferable_skills(self, job_skills: List[str], candidate_skills: List[str]) -> Tuple[float, List[Dict[str, str]]]:
        """
        Calculates how much of the job requirement is covered by the candidate's skills,
        accounting for transferable adjacent skills.
        
        Returns:
            - coverage_score (float): 0.0 to 1.0
            - transfer_mappings (List[Dict]): Audit trail of which skills transferred.
        """
        if not job_skills:
            return 1.0, []
            
        norm_job_skills = [self.normalize_skill(s) for s in job_skills]
        norm_cand_skills = set(self.normalize_skill(s) for s in candidate_skills)
        
        total_score = 0.0
        transfer_mappings = []
        
        for js in norm_job_skills:
            best_match_score = 0.0
            best_cand_skill = None
            
            for cs in norm_cand_skills:
                sim = self.get_adjacency_similarity(js, cs)
                if sim > best_match_score:
                    best_match_score = sim
                    best_cand_skill = cs
                    
            total_score += best_match_score
            
            # If it wasn't an exact match but had transferability, log it for explainability
            if 0.0 < best_match_score < 1.0 and best_cand_skill:
                transfer_mappings.append({
                    "required_skill": js,
                    "matched_skill": best_cand_skill,
                    "transfer_score": round(best_match_score, 2)
                })
                
        # Average coverage
        coverage = total_score / len(norm_job_skills)
        return float(min(coverage, 1.0)), transfer_mappings

# Export singleton instance
skill_graph = SkillOntologyGraph()
