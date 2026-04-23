import re

def extract_residence_period(text: str) -> dict:
    periods = re.findall(r"(\d+\s*년)", text)
    recontracts = re.findall(r"(재계약\s*\d+\s*회\s*가능)", text)
    max_terms = re.findall(r"(최장\s*\d+\s*년)", text)

    return {
        "periods": periods,
        "recontracts": recontracts,
        "max_terms": max_terms,
        "residence_period_text": text
    }