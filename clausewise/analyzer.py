import re
import json
from docx import Document
import transformers
import spacy
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

DOCUMENT_TYPES = [
    "Non-Disclosure Agreement",
    "Lease Agreement", 
    "Employment Contract",
    "Service Agreement",
    "Other"
]

def extract_text(file, filetype):
    """Extract text from various file formats."""
    if filetype == "pdf":
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            return "PDF processing requires PyPDF2. Please install: pip install PyPDF2"
    elif filetype == "docx":
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif filetype == "txt":
        return file.read().decode("utf-8")
    else:
        return ""

def extract_clauses(text):
    """Extract clauses using rule-based approach."""
    # Split by common legal separators
    separators = [r'\n\s*\n', r'\.\s+', r';\s+', r'\.\s*\n']
    
    clauses = []
    current_text = text
    
    for separator in separators:
        if clauses:  # If we already have clauses, break
            break
        parts = re.split(separator, current_text)
        # Filter out very short parts and clean up
        clauses = [part.strip() for part in parts if len(part.strip()) > 20]
    
    # If no clauses found, split by sentences
    if not clauses:
        sentences = re.split(r'[.!?]+', text)
        clauses = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    return clauses[:10]  # Limit to first 10 clauses

def simplify_clause(clause):
    """Simplify legal language using rule-based approach."""
    # Common legal term simplifications
    simplifications = {
        r'\bhereby\b': 'by this agreement',
        r'\bwhereas\b': 'considering that',
        r'\baforesaid\b': 'mentioned above',
        r'\bhereinafter\b': 'from now on',
        r'\bnotwithstanding\b': 'despite',
        r'\bprovided that\b': 'on condition that',
        r'\bsubject to\b': 'depending on',
        r'\bin accordance with\b': 'following',
        r'\bfor the purpose of\b': 'to',
        r'\bwith respect to\b': 'regarding',
        r'\bprior to\b': 'before',
        r'\bsubsequent to\b': 'after',
        r'\bterminate\b': 'end',
        r'\bcease\b': 'stop',
        r'\bcommence\b': 'begin',
        r'\bobligation\b': 'duty',
        r'\bliability\b': 'responsibility',
        r'\bindemnify\b': 'protect from loss',
        r'\bbreach\b': 'violation',
        r'\bremedy\b': 'solution'
    }
    
    simplified = clause
    for legal_term, simple_term in simplifications.items():
        simplified = re.sub(legal_term, simple_term, simplified, flags=re.IGNORECASE)
    
    # Break long sentences
    if len(simplified.split()) > 30:
        sentences = re.split(r'[,;]', simplified)
        simplified = '. '.join([s.strip() for s in sentences if s.strip()])
    
    return simplified

def named_entity_recognition(text):
    """Extract named entities using spaCy."""
    doc = nlp(text)
    entities = {
        'PERSON': [],
        'ORG': [],
        'DATE': [],
        'MONEY': [],
        'CARDINAL': [],
        'GPE': []
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            if ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)
    
    # Also extract patterns for dates, money, etc.
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b'
    money_pattern = r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:\.\d{2})?\s*(?:dollars?|USD|EUR|GBP)\b'
    
    dates = re.findall(date_pattern, text)
    money = re.findall(money_pattern, text)
    
    if dates:
        entities['DATE'].extend(dates)
    if money:
        entities['MONEY'].extend(money)
    
    return entities

def classify_document(text):
    """Classify document type using TF-IDF and Naive Bayes."""
    # Document type keywords
    doc_keywords = {
        "Non-Disclosure Agreement": ["confidential", "non-disclosure", "trade secret", "proprietary"],
        "Lease Agreement": ["lease", "tenant", "landlord", "rent", "property"],
        "Employment Contract": ["employment", "employee", "employer", "salary", "benefits"],
        "Service Agreement": ["service", "provider", "client", "deliverables", "scope"]
    }
    
    # Create training data
    training_texts = []
    training_labels = []
    
    for doc_type, keywords in doc_keywords.items():
        for keyword in keywords:
            training_texts.append(keyword)
            training_labels.append(doc_type)
    
    # Add some generic text
    training_texts.extend(["agreement", "contract", "terms", "conditions"])
    training_labels.extend(["Other"] * 4)
    
    # Create TF-IDF features
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    X_train = vectorizer.fit_transform(training_texts)
    
    # Train classifier
    classifier = MultinomialNB()
    classifier.fit(X_train, training_labels)
    
    # Predict
    X_test = vectorizer.transform([text])
    prediction = classifier.predict(X_test)[0]
    
    return prediction

def analyze_document(text):
    """Analyze document and return comprehensive results."""
    # Extract clauses
    clauses = extract_clauses(text)
    
    # Simplify clauses
    simplified_clauses = [simplify_clause(clause) for clause in clauses]
    
    # Extract entities
    entities = named_entity_recognition(text)
    
    # Classify document
    doc_type = classify_document(text)
    
    return {
        "clauses": clauses,
        "simplified_clauses": simplified_clauses,
        "entities": entities,
        "classification": doc_type,
        "summary": f"Document classified as {doc_type} with {len(clauses)} clauses extracted."
    }
