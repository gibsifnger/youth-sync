def normalize_region(region: str | None) -> str | None:
    if not region:
        return None

    region_map = {
        "서울시": "서울",
        "서울특별시": "서울",
        "경기도": "경기",
        "부산시": "부산",
        "대구시": "대구",
        "인천시": "인천",
    }
    return region_map.get(region, region)

def normalize_employment_status(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip()

    mapping = {
        "미취업자": "미취업",
        "취업준비": "미취업",
        "취업 준비": "미취업",
        "구직중": "구직자",
        "구직 중": "구직자",
        "재직중": "재직",
        "재직 중": "재직",
    }

    return mapping.get(value, value)

def map_to_user_profile_schema(front_input: dict) -> dict:
    return {
        "age": front_input.get("age"),
        "region": normalize_region(front_input.get("region")),
        "employment_status": normalize_employment_status(front_input.get("employment_status") or front_input.get("job_status")),
        "housing_status": front_input.get("housing_status"),
        "income_level": front_input.get("income_level"),
        "interest_tags": front_input.get("interest_tags", []),
        "unknown_fields": front_input.get("unknown_fields", []),
        "raw_text": front_input.get("raw_text")
    }