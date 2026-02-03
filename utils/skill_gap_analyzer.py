import torch
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache

EXACT_MATCH_THRESHOLD = 0.85
PARTIAL_MATCH_THRESHOLD = 0.65


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def get_skill_embedding(skill: str):
    # Return a sentence-transformer embedding for a single skill string
    model = get_model()
    return model.encode(skill, convert_to_tensor=True)


def cosine_similarity(vec1, vec2) -> float:
    # Cosine similarity between two embedding tensors as a Python float
    return float(util.cos_sim(vec1, vec2).item())


def analyze_skill_gap(jd_skills, resume_skills):
    if not jd_skills:
        return {'matched': [], 'partial': [], 'missing': []}

    # If resume has no skills, everything is missing
    if not resume_skills:
        return {
            'matched': [],
            'partial': [],
            'missing': [(skill, 0.0) for skill in jd_skills]
        }

    model = get_model()
    
    # Encode lists to vectors
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)
    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)

    matched = []
    partial = []
    missing = []

    # Calculate similarity matrix efficiently
    similarity_matrix = util.cos_sim(jd_embeddings, resume_embeddings)

    for i, jd_skill in enumerate(jd_skills):
        # Find best match in resume for this specific JD skill
        best_score = float(torch.max(similarity_matrix[i]))
        best_match_idx = int(torch.argmax(similarity_matrix[i]))
        best_match_name = resume_skills[best_match_idx]

        # Categorize
        if best_score >= EXACT_MATCH_THRESHOLD:
            matched.append((jd_skill, best_match_name, round(best_score, 2)))
        elif best_score >= PARTIAL_MATCH_THRESHOLD:
            partial.append((jd_skill, best_match_name, round(best_score, 2)))
        else:
            missing.append((jd_skill, round(best_score, 2)))

    return {
        'matched': sorted(matched, key=lambda x: -x[2]),
        'partial': sorted(partial, key=lambda x: -x[2]),
        'missing': sorted(missing, key=lambda x: x[1])
    }

def analyze_complete_skill_gap(jd_skills, resume_skills):
    return {
        'technical': analyze_skill_gap(
            jd_skills.get('technical', []),
            resume_skills.get('technical', [])
        ),
        'soft': analyze_skill_gap(
            jd_skills.get('soft', []),
            resume_skills.get('soft', [])
        )
    }

def calculate_match_percentage(analysis):
    total = len(analysis['matched']) + len(analysis['partial']) + len(analysis['missing'])
    if total == 0:
        return 100.0

    score = len(analysis['matched']) + (len(analysis['partial']) * 0.5)
    return round((score / total) * 100, 1)