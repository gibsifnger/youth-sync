def infer_category_from_title(title: str) -> tuple[str, str]:
    title = title or ""

    if "전세임대" in title:
        return "주거", "전세임대"
    if "매입임대" in title:
        return "주거", "매입임대"
    if "행복주택" in title:
        return "주거", "행복주택"
    if "기숙사형" in title:
        return "주거", "기숙사형 청년주택"

    return "주거", "기타"

def infer_region_scope(chunks: list[dict], title: str = "") -> str:
    combined = " ".join([title] + [c.get("text", "") for c in chunks])

    if "전국" in combined:
        return "전국"

    # 필요하면 나중에 지역 사전 확장
    for region in ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
                   "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]:
        if region in combined:
            return region

    return "전국"

def infer_apply_status(chunks: list[dict]) -> str | None:
    combined = " ".join(c.get("text", "") for c in chunks)

    if "상시" in combined:
        return "상시"
    if "마감" in combined:
        return "마감"
    if "모집" in combined or "공급" in combined:
        return "안내중"

    return None

def build_income_condition_text(income_asset: dict) -> str | None:
    rules = income_asset.get("priority_rules", [])
    if not rules:
        return None
    return " ".join(rules)

def build_housing_condition(eligibility: dict) -> str | None:
    conditions = eligibility.get("housing_conditions", [])
    if not conditions:
        return None
    return ", ".join(conditions)

def build_employment_condition(eligibility: dict) -> str | None:
    targets = eligibility.get("target_groups", [])

    # 스키마 상 employment_condition은 문자열 1개로 맞춤
    # LH 특성상 엄밀히 고용조건만은 아니지만, 현재는 대상군 요약으로 저장
    if not targets:
        return None

    return ", ".join(targets)

def build_summary(raw_result: dict) -> str:
    title = raw_result.get("title", "")
    search_text = raw_result.get("search_text", "")
    return f"{title} {search_text}".strip()

def map_to_policy_schema(raw_result: dict) -> dict:
    eligibility = raw_result.get("eligibility", {})
    income_asset = raw_result.get("income_asset", {})
    chunks = raw_result.get("chunks", [])
    title = raw_result.get("title", "")

    category, subcategory = infer_category_from_title(title)

    return {
        "policy_id": raw_result.get("policy_id"),
        "policy_name": title,
        "category": category,
        "subcategory": subcategory,
        "region_scope": infer_region_scope(chunks, title),
        "age_min": eligibility.get("age_min"),
        "age_max": eligibility.get("age_max"),
        "employment_condition": build_employment_condition(eligibility),
        "housing_condition": build_housing_condition(eligibility),
        "income_condition_text": build_income_condition_text(income_asset),
        "apply_start_date": None,
        "apply_end_date": None,
        "apply_status": infer_apply_status(chunks),
        "source_org": "LH",
        "source_url": raw_result.get("url"),
        "summary": build_summary(raw_result),
        "source_type": "web_page"
    }