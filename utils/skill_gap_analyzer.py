import torch
import numpy as np
from transformers import AutoModel, AutoTokenizer
from functools import lru_cache

# threshold for skill matching
EXACT_MATCH_THRESHOLD = 0.85
PARTIAL_MATCH_THRESHOLD = 0.65

# BERT model setup
@lru_cache(maxsize=1)
def get_embedding_model():
    return AutoModel.from_pretrained('bert-base-uncased')

@lru_cache(maxsize=1)
def get_embedding_tokenizer():
    return AutoTokenizer.from_pretrained('bert-base-uncased')


def get_skill_embedding(skill):
    model = get_embedding_model()
    tokenizer = get_embedding_tokenizer()

    inputs = tokenizer(skill, return_tensors='pt', truncation=True, padding=True, max_length=64)

    with torch.no_grad():
        outputs = model(**inputs)

    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding


def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def analyze_skill_gap(jd_skills, resume_skills):
    if not jd_skills:
        return {'matched': [], 'partial': [], 'missing': []}

    if not resume_skills:
        return {
            'matched': [],
            'partial': [],
            'missing': [(skill, 0.0) for skill in jd_skills]
        }

    jd_embeddings = {skill: get_skill_embedding(skill) for skill in jd_skills}
    resume_embeddings = {skill: get_skill_embedding(skill) for skill in resume_skills}

    matched = []
    partial = []
    missing = []

    for jd_skill in jd_skills:
        jd_skill_lower = jd_skill.lower()
        best_match = None
        best_score = 0.0

        for resume_skill in resume_skills:
            if resume_skill.lower() == jd_skill_lower:
                matched.append((jd_skill, resume_skill, 1.0))
                best_match = resume_skill
                best_score = 1.0
                break
        
        if best_score < 1.0:
            jd_emb = jd_embeddings[jd_skill]

            for resume_skill in resume_skills:
                resume_emb = resume_embeddings[resume_skill]
                similarity = cosine_similarity(jd_emb, resume_emb)
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = resume_skill

            if best_score >= EXACT_MATCH_THRESHOLD:
                matched.append((jd_skill, best_match, round(best_score, 2)))
            elif best_score >= PARTIAL_MATCH_THRESHOLD:
                partial.append((jd_skill, best_match, round(best_score, 2)))
            else:
                missing.append((jd_skill, round(best_score, 2)))
    return {
        'matched': sorted(matched, key=lambda x: -x[2]),
        'partial': sorted(partial, key=lambda x: -x[2]),
        'missing': sorted(missing, key=lambda x: x[1])
    }

def analyze_complete_skill_gap(jd_skills, resume_skills):
    return{
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