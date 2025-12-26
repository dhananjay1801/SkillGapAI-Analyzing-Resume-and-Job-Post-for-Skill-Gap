from utils.skill_gap_analyzer import get_skill_embedding, cosine_similarity

def find_closest_existing_skill(missing_skill, existing_skills):
    if not existing_skills:
        return None, 0.0
    
    missing_emb = get_skill_embedding(missing_skill)
    best_match = None
    best_score = 0.0
    
    for existing_skill in existing_skills:
        existing_emb = get_skill_embedding(existing_skill)
        score = cosine_similarity(missing_emb, existing_emb)
        if score > best_score:
            best_score = score
            best_match = existing_skill
    
    return best_match, best_score

def find_related_missing_skills(target_skill, all_missing_skills, threshold=0.5):
    related = []
    target_emb = get_skill_embedding(target_skill)
    
    for skill, _ in all_missing_skills:
        if skill.lower() != target_skill.lower():
            skill_emb = get_skill_embedding(skill)
            similarity = cosine_similarity(target_emb, skill_emb)
            if similarity >= threshold:
                related.append((skill, similarity))
    
    related.sort(key=lambda x: x[1], reverse=True)
    return related[:3] # top 3 similar missing skills

def calculate_match_impact(skill, gap_analysis, category):
    total_skills = len(gap_analysis[category]['matched']) + len(gap_analysis[category]['partial']) + len(gap_analysis[category]['missing'])
    if total_skills == 0:
        return 0.0
    current_score = len(gap_analysis[category]['matched']) + (len(gap_analysis[category]['partial']) * 0.5)
    new_score = current_score + 1
    current_pct = (current_score / total_skills) * 100
    new_pct = (new_score / total_skills) * 100
    return round(new_pct - current_pct, 1)

def estimate_learning_time(similarity_score):
    if similarity_score > 0.7:
        return "1-2 weeks"
    elif similarity_score > 0.5:
        return "2-4 weeks"
    elif similarity_score > 0.3:
        return "1-2 months"
    else:
        return "more than 2 months"

def get_smart_recommendations(gap_analysis, resume_skills):
    recommendations = []
    
    for skill, similarity_score in gap_analysis['technical']['missing']:
        closest_skill = find_closest_existing_skill(skill, resume_skills['technical'])
        related_missing = find_related_missing_skills(skill, gap_analysis['technical']['missing'])
        match_impact = calculate_match_impact(skill, gap_analysis, 'technical')
        learning_time = estimate_learning_time(similarity_score)
        
        recommendations.append({
            'skill': skill,
            'category': 'technical',
            'similarity_score': similarity_score,
            'closest_existing': closest_skill[0] if closest_skill else None,
            'closest_similarity': closest_skill[1] if closest_skill else 0.0,
            'related_missing': related_missing, 
            'match_impact': match_impact,
            'learning_time': learning_time
        })
    
    for skill, similarity_score in gap_analysis['soft']['missing']:
        closest_skill = find_closest_existing_skill(skill, resume_skills['soft'])
        related_missing = find_related_missing_skills(skill, gap_analysis['soft']['missing'])
        match_impact = calculate_match_impact(skill, gap_analysis, 'soft')
        learning_time = estimate_learning_time(similarity_score)
        
        recommendations.append({
            'skill': skill,
            'category': 'soft',
            'similarity_score': similarity_score,
            'closest_existing': closest_skill[0] if closest_skill else None,
            'closest_similarity': closest_skill[1] if closest_skill else 0.0,
            'related_missing': related_missing,
            'match_impact': match_impact,
            'learning_time': learning_time
        })
    
    return recommendations

