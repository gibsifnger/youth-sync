from app.preprocess.html_cleaner import strip_html
from app.preprocess.content_extractor import extract_title, extract_main_text
from app.preprocess.chunker import split_lines, build_chunks, get_chunk_text

from app.extractors.eligibility_extractor import extract_eligibility
from app.extractors.income_asset_extractor import extract_income_asset
from app.extractors.rental_extractor import extract_rental_terms
from app.extractors.residence_period_extractor import extract_residence_period
from app.extractors.supply_timing_extractor import extract_supply_timing

from app.mappers.policy_mapper import map_to_policy_schema
from app.mappers.chunk_mapper import map_chunks_to_schema


def build_search_text(title: str, chunks: list[dict]) -> str:
    important = []
    for chunk in chunks:
        if chunk["section"] in ["입주대상", "소득 자산 기준", "소득 기준", "임대조건"]:
            important.append(chunk["text"])
    return f"{title} " + " ".join(important)


def process_html(url: str, html: str) -> dict:
    soup = strip_html(html)
    title = extract_title(soup)
    main_text = extract_main_text(soup)

    lines = split_lines(main_text)
    chunks = build_chunks(lines)

    eligibility_text = get_chunk_text(chunks, "입주대상")
    income_asset_text = get_chunk_text(chunks, "소득 자산 기준") or get_chunk_text(chunks, "소득 기준")
    rental_text = get_chunk_text(chunks, "임대조건")
    residence_period_text = get_chunk_text(chunks, "거주기간")
    supply_timing_text = get_chunk_text(chunks, "공급시기")

    # 내부 추출용 원시 결과
    raw_result = {
        "policy_id": url.split("mid=")[-1] if "mid=" in url else None,
        "url": url,
        "title": title,
        "eligibility": extract_eligibility(eligibility_text),
        "income_asset": extract_income_asset(income_asset_text),
        "rental_terms": extract_rental_terms(rental_text),
        "residence_period": extract_residence_period(residence_period_text),
        "supply_timing": extract_supply_timing(supply_timing_text),
        "chunks": chunks,
        "search_text": build_search_text(title, chunks)
    }

    # 스키마 호환 결과
    policy_schema = map_to_policy_schema(raw_result)
    chunk_schema = map_chunks_to_schema(raw_result)

    return {
        "raw_extraction": raw_result,
        "policy_schema": policy_schema,
        "chunk_schema": chunk_schema
    }