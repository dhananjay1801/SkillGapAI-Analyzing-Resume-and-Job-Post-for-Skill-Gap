import spacy
from spacy.matcher import PhraseMatcher
from transformers import pipeline, AutoTokenizer
from functools import lru_cache
from data.skills.technical_skills import TECHNICAL_SKILLS
from data.skills.soft_skills import SOFT_SKILLS

# spacy setup
@lru_cache(maxsize=1)
def get_nlp():
    try:
        return spacy.load('en_core_web_sm')
    except OSError:
        from spacy.cli import download
        download('en_core_web_sm')
        return spacy.load('en_core_web_sm')

@lru_cache(maxsize=1)
def build_matchers():
    nlp = get_nlp()
    tech_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
    soft_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
    tech_patterns = [nlp.make_doc(skill) for skill in TECHNICAL_SKILLS]
    soft_patterns = [nlp.make_doc(skill) for skill in SOFT_SKILLS]
    tech_matcher.add('TECH', tech_patterns)
    soft_matcher.add('SOFT', soft_patterns)

    return tech_matcher, soft_matcher

def extract_skills_spacy(text):
    nlp = get_nlp()
    doc = nlp(text)
    tech_matcher, soft_matcher = build_matchers()

    found_technical = set()
    found_soft = set()

    for match_id, start, end in tech_matcher(doc):
        found_technical.add(doc[start:end].text.title())

    for match_id, start, end in soft_matcher(doc):
        found_soft.add(doc[start:end].text.title())

    return{'technical': found_technical, 'soft': found_soft}


# bert setup
@lru_cache(maxsize=1)
def get_ner_pipeline():
    return pipeline('ner', model='jjzha/jobbert_skill_extraction', aggregation_strategy='simple')

@lru_cache(maxsize=1)
def get_tokenizer():
    return AutoTokenizer.from_pretrained('jjzha/jobbert_skill_extraction')

def extract_skills_bert(text):
    ner = get_ner_pipeline()
    tokenizer = get_tokenizer()

    # Properly truncate using tokenizer
    encoded = tokenizer(text, truncation=True, max_length=512, return_tensors=None)
    truncated_text = tokenizer.decode(encoded['input_ids'], skip_special_tokens=True)

    entities = ner(truncated_text)

    found_technical = set()
    found_soft = set()

    for entity in entities:
        word = entity['word'].lower().replace('##', '')

        if word in TECHNICAL_SKILLS:
            found_technical.add(word.title())
        elif word in SOFT_SKILLS:
            found_soft.add(word.title())
    
    return {'technical': found_technical, 'soft': found_soft}

# merge both results
def extract_skills(text):
    spacy_results = extract_skills_spacy(text)
    bert_results = extract_skills_bert(text)

    technical = spacy_results['technical'] | bert_results['technical']
    soft = spacy_results['soft'] | bert_results['soft']

    return {
        'technical' : sorted(technical),
        'soft' : sorted(soft)
    }
