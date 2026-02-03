import spacy
from spacy.cli.download import download as spacy_download
from spacy.matcher import PhraseMatcher
from transformers import AutoTokenizer, pipeline
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache
import torch
from data.skills.technical_skills import TECHNICAL_SKILLS
from data.skills.soft_skills import SOFT_SKILLS


@lru_cache(maxsize=1)
def get_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        spacy_download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


@lru_cache(maxsize=1)
def build_tech_matcher():
    nlp = get_nlp()
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in TECHNICAL_SKILLS]
    matcher.add("TECH", patterns)
    return matcher


@lru_cache(maxsize=1)
def get_sentence_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_soft_skill_embeddings():
    model = get_sentence_model()
    return model.encode(list(SOFT_SKILLS), convert_to_tensor=True)


def extract_soft_skills_semantic(text: str) -> set[str]:
    if not text or not isinstance(text, str):
        return set()

    nlp = get_nlp()
    model = get_sentence_model()
    soft_skill_embeddings = get_soft_skill_embeddings()
    soft_skill_list = list(SOFT_SKILLS)

    doc = nlp(text)
    resume_sentences = [sent.text for sent in doc.sents if len(sent.text.split()) > 3]
    if not resume_sentences:
        return set()

    resume_embeddings = model.encode(resume_sentences, convert_to_tensor=True)
    cosine_scores = util.cos_sim(soft_skill_embeddings, resume_embeddings)

    found_soft: set[str] = set()
    SEMANTIC_THRESHOLD = 0.45

    for i, skill_scores in enumerate(cosine_scores):
        best_score = torch.max(skill_scores)
        if best_score > SEMANTIC_THRESHOLD:
            found_soft.add(soft_skill_list[i].title())

    return found_soft


@lru_cache(maxsize=1)
def get_ner_pipeline():
    return pipeline("ner", model="jjzha/jobbert_skill_extraction", aggregation_strategy="simple")  # type: ignore


@lru_cache(maxsize=1)
def get_tokenizer():
    return AutoTokenizer.from_pretrained("jjzha/jobbert_skill_extraction")


def extract_skills_bert_ner(text: str) -> set[str]:
    if not text:
        return set()

    ner = get_ner_pipeline()
    tokenizer = get_tokenizer()

    encoded = tokenizer(text, truncation=True, max_length=512, return_tensors=None)
    truncated_text = tokenizer.decode(encoded["input_ids"], skip_special_tokens=True)

    entities = ner(truncated_text)
    found_technical: set[str] = set()

    for entity in entities:
        word = entity.get("word") or entity.get("entity_group") or entity.get("entity")
        if not word:
            continue

        clean_word = word.lower().strip().replace("##", "")
        if clean_word in TECHNICAL_SKILLS:
            found_technical.add(clean_word.title())

    return found_technical


def extract_skills(text: str) -> dict[str, list[str]]:
    nlp = get_nlp()
    doc = nlp(text)
    tech_matcher = build_tech_matcher()

    found_technical_spacy: set[str] = set()
    for _, start, end in tech_matcher(doc):
        found_technical_spacy.add(doc[start:end].text.title())

    found_technical_bert = extract_skills_bert_ner(text)
    found_soft_semantic = extract_soft_skills_semantic(text)

    technical = found_technical_spacy | found_technical_bert

    return {
        "technical": sorted(technical),
        "soft": sorted(found_soft_semantic),
    }
