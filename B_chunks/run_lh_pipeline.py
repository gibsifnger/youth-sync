import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.fetchers.lh_fetcher import fetch_page
from app.pipeline import process_html


# =========================
# 기본 설정
# =========================
BASE_URL = "https://www.lh.or.kr"
START_URL = "https://www.lh.or.kr/menu.es?mid=a10401020100"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
HISTORY_DIR = ROOT_DIR / "data" / "history"
LOG_DIR = ROOT_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LATEST_ITEMS_PATH = HISTORY_DIR / "latest_items.json"

logging.basicConfig(
    filename=LOG_DIR / "lh_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


# =========================
# 유틸 함수
# =========================
def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: Path, default):
    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 메뉴 링크 수집
# =========================
def get_depth4_menu_links(url: str) -> list[str]:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    menu_area = soup.find("ul", id="depth4_menu_ul")

    if not menu_area:
        raise ValueError("depth4_menu_ul 영역을 찾지 못했습니다.")

    links = []
    seen = set()

    for tag in menu_area.select("a[href]"):
        href = tag.get("href", "").strip()

        if "menu.es?mid" not in href:
            continue

        full_url = urljoin(BASE_URL, href)

        if full_url in seen:
            continue

        seen.add(full_url)
        links.append(full_url)

    return links


# =========================
# 신규 공고 감지 로직
# =========================
def build_item_key(item: dict) -> str:
    """
    변경감지용 고유키 생성
    우선순위:
    1) url
    2) page_id
    3) title + date
    """
    url = (item.get("url") or "").strip()
    page_id = (item.get("page_id") or "").strip()
    title = (item.get("title") or "").strip()
    date = (item.get("date") or "").strip()

    if url:
        return url
    if page_id:
        return page_id

    return f"{title}::{date}"

# =========================
# 비교용 데이터 추출
# =========================
def extract_items_for_diff(page_id: str, page_url: str, result: dict) -> list[dict]:
    policy = result.get("policy_schema", {})

    if not isinstance(policy, dict) or not policy:
        return []

    item = {
        "page_id": policy.get("policy_id") or page_id,
        "source_page": page_url,
        "title": policy.get("policy_name", ""),
        "url": policy.get("source_url", ""),
        "date": policy.get("apply_start_date") or policy.get("apply_end_date") or "",
        "apply_status": policy.get("apply_status"),
        "category": policy.get("category"),
        "subcategory": policy.get("subcategory"),
        "summary": policy.get("summary", ""),
        "content_hash": build_content_hash(policy),
        "raw": policy
    }

    return [item]
# =========================
# 해시
# =========================
def build_content_hash(policy: dict) -> str:
    """
    정책 내용이 바뀌었는지 비교하기 위한 해시값
    변경감지에 중요한 필드만 묶어서 hash 생성
    """
    payload = {
        "policy_name": policy.get("policy_name"),
        "category": policy.get("category"),
        "subcategory": policy.get("subcategory"),
        "region_scope": policy.get("region_scope"),
        "employment_condition": policy.get("employment_condition"),
        "housing_condition": policy.get("housing_condition"),
        "income_condition_text": policy.get("income_condition_text"),
        "apply_start_date": policy.get("apply_start_date"),
        "apply_end_date": policy.get("apply_end_date"),
        "apply_status": policy.get("apply_status"),
        "summary": policy.get("summary"),
    }

    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
# =========================
# 메인 파이프라인
# =========================
def run_pipeline():
    logging.info("=== LH pipeline started ===")

    test_urls = get_depth4_menu_links(START_URL)
    logging.info(f"Collected {len(test_urls)} menu links")

    current_all_items = []

    for url in test_urls:
        page_id = url.split("mid=")[-1]
        logging.info(f"Processing: {url}")

        html = fetch_page(url)
        result = process_html(url, html)

        save_json(OUTPUT_DIR / f"{page_id}_raw.json", result["raw_extraction"])
        save_json(OUTPUT_DIR / f"{page_id}_policy.json", result["policy_schema"])
        save_json(OUTPUT_DIR / f"{page_id}_chunks.json", {"chunks": result["chunk_schema"]})

        items = extract_items_for_diff(page_id, url, result)
        current_all_items.extend(items)

    previous_items = load_json(LATEST_ITEMS_PATH, default=[])

    new_items = detect_new_items(previous_items, current_all_items)
    updated_items = detect_updated_items(previous_items, current_all_items)

    today = datetime.now().strftime("%Y-%m-%d")

    save_json(HISTORY_DIR / f"new_items_{today}.json", {"items": new_items})
    save_json(HISTORY_DIR / f"updated_items_{today}.json", {"items": updated_items})
    save_json(LATEST_ITEMS_PATH, current_all_items)

    logging.info(f"Total items: {len(current_all_items)}")
    logging.info(f"New items: {len(new_items)}")
    logging.info(f"Updated items: {len(updated_items)}")

    print(f"전체 수집: {len(current_all_items)}")
    print(f"신규 항목: {len(new_items)}")
    print(f"변경 항목: {len(updated_items)}")

    logging.info("=== LH pipeline finished ===")
# =========================
# 몰라
# =========================
def detect_new_items(previous_items: list[dict], current_items: list[dict]) -> list[dict]:
    previous_keys = {build_item_key(item) for item in previous_items}
    return [item for item in current_items if build_item_key(item) not in previous_keys]
def detect_updated_items(previous_items: list[dict], current_items: list[dict]) -> list[dict]:
    previous_map = {build_item_key(item): item for item in previous_items}
    updated_items = []

    for item in current_items:
        key = build_item_key(item)

        if key not in previous_map:
            continue

        prev_hash = previous_map[key].get("content_hash")
        curr_hash = item.get("content_hash")

        if prev_hash != curr_hash:
            updated_items.append({
                "before": previous_map[key],
                "after": item
            })

    return updated_items
# =========================
# 실행
# =========================
def main():
    try:
        run_pipeline()
    except Exception as e:
        logging.exception(f"Pipeline failed: {e}")
        print("실행 중 오류 발생:", e)
        raise


if __name__ == "__main__":
    main()