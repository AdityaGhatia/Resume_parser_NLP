# Resume Parser using NLP

A rule-based resume parser that extracts structured information
from PDF resumes using NLP techniques.

## Features
- PDF resume parsing
- Skill extraction (spaCy EntityRuler + dictionary fallback)
- Education extraction
- Experience & company extraction
- Confidence scoring
- JSON output

## Tech Stack
- Python
- spaCy
- Regex
- PyPDF2

## How to Run
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py
