def extract_priority_rules(text: str) -> list[str]:
    rules = []
    for marker in ["1순위", "2순위", "3순위"]:
        if marker in text:
            start = text.find(marker)
            next_positions = [text.find(m, start + 1) for m in ["1순위", "2순위", "3순위"] if text.find(m, start + 1) != -1]
            end = min(next_positions) if next_positions else len(text)
            rules.append(text[start:end].strip())
    return rules

def extract_income_asset(text: str) -> dict:
    return {
        "priority_rules": extract_priority_rules(text),
        "income_asset_text": text
    }