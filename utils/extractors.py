import re
import spacy
from spacy.pipeline import EntityRuler

SECTION_HEADERS = {
    "skills": r"(skills|technical skills|core skills|tools)",
    "education": r"(education|academic background|qualifications)",
    "experience": r"(experience|work experience|internships|internship)"
}

NORMALIZATION_MAP = {
    "ml": "machine learning",
    "dl": "deep learning",
    "py": "python",
    "b tech": "b.tech",
    "b. tech": "b.tech"
}

def load_nlp():
    nlp = spacy.load("en_core_web_sm")

    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
    else:
        ruler = nlp.get_pipe("entity_ruler")

    patterns = [
        {"label": "SKILL", "pattern": [{"LOWER": "python"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "kafka"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "spark"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "xgboost"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "machine"}, {"LOWER": "learning"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "deep"}, {"LOWER": "learning"}]},

        {"label": "DEGREE", "pattern": [{"LOWER": "b"}, {"LOWER": "."}, {"LOWER": "tech"}]},
        {"label": "DEGREE", "pattern": [{"LOWER": "b"}, {"LOWER": "tech"}]},
        {"label": "DEGREE", "pattern": [{"LOWER": "bachelor"}, {"LOWER": "of"}, {"LOWER": "technology"}]},
        {"label": "DEGREE", "pattern": [{"LOWER": "computer"}, {"LOWER": "engineering"}]},
        {"label": "DEGREE", "pattern": [{"LOWER": "computer"}, {"LOWER": "science"}]},

        {"label": "JOB_TITLE", "pattern": [{"LOWER": "mlops"}, {"LOWER": "engineer"}]},
        {"label": "JOB_TITLE", "pattern": [{"LOWER": "data"}, {"LOWER": "scientist"}]},
        {"label": "JOB_TITLE", "pattern": [{"LOWER": "data"}, {"LOWER": "analyst"}]},
        {"label": "JOB_TITLE", "pattern": [{"LOWER": "internship"}]},
        {"label": "JOB_TITLE", "pattern": [{"LOWER": "intern"}]},

        {"label": "COMPANY", "pattern": [{"LOWER": "accenture"}]},
    ]
    ruler.add_patterns(patterns)
    return nlp

NLP = load_nlp()

def extract_section(text, section):
    header = SECTION_HEADERS[section]
    regex = rf"{header}(.+?)(?=\n[A-Z][A-Z\s]{{2,}}|\Z)"
    match = re.search(regex, text, re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else ""

def extract_entities(text, label):
    doc = NLP(text)
    return list(set(ent.text.lower().strip() for ent in doc.ents if ent.label_ == label))

def skill_list_fallback(text, skills_file="data/skills_list.txt"):
    found = set()
    text_lower = text.lower()

    with open(skills_file, encoding="utf-8") as f:
        for skill in f:
            s = skill.strip().lower()
            if re.search(rf"\b{s}\b", text_lower):
                found.add(s)

    return list(found)

EDUCATION_REGEX = [
    r"b\.?\s*tech",
    r"bachelor\s+of\s+technology",
    r"computer\s+engineering",
    r"computer\s+science",
    r"information\s+technology"
]

def education_fallback(text):
    found = set()
    text_lower = text.lower()

    for pattern in EDUCATION_REGEX:
        match = re.search(pattern, text_lower)
        if match:
            found.add(match.group().strip())

    return list(found)

def experience_fallback(text):
    found = set()
    text_lower = text.lower()

    if "internship" in text_lower or "intern" in text_lower:
        found.add("internship")

    # company fallback (simple + safe)
    company_match = re.search(r"\b(accenture)\b", text_lower)
    if company_match:
        found.add(company_match.group(1))

    return list(found)

def normalize(items):
    normalized = set()
    for item in items:
        key = item.lower().strip()
        normalized.add(NORMALIZATION_MAP.get(key, key))
    return list(normalized)

def confidence_score(section_found, count):
    if section_found and count >= 2:
        return 0.9
    if count > 0:
        return 0.7
    return 0.4

def extract_all(text):
    skills_section = extract_section(text, "skills")
    edu_section = extract_section(text, "education")
    exp_section = extract_section(text, "experience")

    skills = extract_entities(skills_section or text, "SKILL")
    if len(skills) < 5:
        skills += skill_list_fallback(skills_section or text)
    skills = normalize(skills)

    education = extract_entities(edu_section or text, "DEGREE")
    if not education:
        education = education_fallback(edu_section or text)
    education = normalize(education)

    experience = extract_entities(exp_section or text, "JOB_TITLE")
    companies = extract_entities(exp_section or text, "COMPANY")

    if not experience and not companies:
        fallback = experience_fallback(exp_section or text)
        experience.extend(fallback)

    experience = normalize(experience + companies)

    return {
        "skills": {
            "values": skills,
            "confidence": confidence_score(bool(skills_section), len(skills))
        },
        "education": {
            "values": education,
            "confidence": confidence_score(bool(edu_section), len(education))
        },
        "experience": {
            "values": experience,
            "confidence": confidence_score(bool(exp_section), len(experience))
        }
    }
