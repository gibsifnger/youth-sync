import re

def extract_supply_timing(text: str) -> dict:
    frequency = []
    for keyword in ["분기별", "반기별", "상시", "정기"]:
        if keyword in text:
            frequency.append(keyword)

    months = re.findall(r"(\d{1,2})\s*월", text)

    if not months:
        compact = re.search(r"\(([\d,\s]+)월\)", text)
        if compact:
            nums = compact.group(1).split(",")
            months = [f"{n.strip()}월" for n in nums if n.strip()]

    return {
        "frequency": sorted(list(set(frequency))),
        "months": sorted(list(set(months))),
        "supply_timing_text": text
    }