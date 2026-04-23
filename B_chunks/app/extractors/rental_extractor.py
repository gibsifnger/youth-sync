import re

def extract_rental_terms(text: str) -> dict:
    deposits = re.findall(r"(보증금\s*[^,.\n]+)", text)
    rents = re.findall(r"(임대료\s*[^,.\n]+)", text)
    interests = re.findall(r"(연\s*\d+(?:\.\d+)?\s*~\s*\d+(?:\.\d+)?%\s*이자[^,.\n]*)", text)

    return {
        "deposits": deposits,
        "rents": rents,
        "interests": interests,
        "rental_text": text
    }