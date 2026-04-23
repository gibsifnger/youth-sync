import re
from app.config import TARGET_KEYWORDS, HOUSING_KEYWORDS

def extract_age(text: str) -> dict:
    patterns = [
        r"만\s*(\d{1,2})\s*세\s*이상\s*만\s*(\d{1,2})\s*세\s*이하",
        r"(\d{1,2})\s*세\s*[~\-]\s*(\d{1,2})\s*세",
        r"만\s*(\d{1,2})\s*세\s*이상",
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            if len(m.groups()) == 2:
                return {"age_min": int(m.group(1)), "age_max": int(m.group(2))}
            return {"age_min": int(m.group(1)), "age_max": None}

    return {"age_min": None, "age_max": None}

def extract_target_groups(text: str) -> list[str]:
    found = []
    for keyword in TARGET_KEYWORDS:
        if keyword in text:
            found.append(keyword)
    return sorted(list(set(found)))

def extract_housing_condition(text: str) -> list[str]:
    found = []
    for keyword in HOUSING_KEYWORDS:
        if keyword in text:
            found.append(keyword)
    return sorted(list(set(found)))

def extract_eligibility(text: str) -> dict:
    age = extract_age(text)
    return {
        "age_min": age["age_min"],
        "age_max": age["age_max"],
        "target_groups": extract_target_groups(text),
        "housing_conditions": extract_housing_condition(text),
        "eligibility_text": text
    }