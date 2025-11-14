import re

def normalize_text(text):
    if not text:
        return ""
    
    text = text.lower()
    
    # replace any run of whitespace characters (spaces, tabs, newlines) with a single space.
    text = re.sub(r'\s+', " ", text)
    return text.strip()

def clean_text(text):
    if not text:
        return ""
    
    # Remove emails
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b", " ", text)

    # Remove URLs
    text = re.sub(r"http[s]?://\S+|www\.\S+", " ", text)

    # Remove repeated punctuation / odd characters (keep letters, numbers, punctuation, spaces)
    text = re.sub(r"[^a-z0-9.,;:!?()\-\s]", " ", text)

    # Collapse spaces again after removals
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def process_text(text):
    if not text:
        return ""
    
    text = normalize_text(text)
    text = clean_text(text)
    return text