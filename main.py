import json
import os
from utils.pdf_reader import extract_text_from_pdf
from utils.text_cleaner import clean_text
from utils.extractors import extract_all

def parse_resume(file_path):
    if file_path.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

    cleaned_text = clean_text(raw_text)
    return extract_all(cleaned_text)

if __name__ == "__main__":
    resume_path = "resumes/sample_resume.pdf"
    result = parse_resume(resume_path)

    os.makedirs("output", exist_ok=True)
    with open("output/parsed_resume.json", "w") as f:
        json.dump(result, f, indent=4)

    print("Resume parsed successfully ✅")
    print(json.dumps(result, indent=4))
