from pathlib import Path
from app.config import SEED_URLS
from app.fetchers.lh_fetcher import fetch_page
from app.pipeline import process_html
from app.utils.hash_util import make_hash
from app.utils.file_util import write_text, read_text, write_json

STATE_DIR = Path("data/state")
RAW_HTML_DIR = Path("data/raw_html")
OUTPUT_DIR = Path("output/json")
POLICY_SCHEMA_DIR = OUTPUT_DIR / "policy_schema"
CHUNK_SCHEMA_DIR = OUTPUT_DIR / "chunk_schema"
RAW_EXTRACTION_DIR = OUTPUT_DIR / "raw_extraction"

def make_page_id(url: str) -> str:
    return url.split("mid=")[-1]

def track_pages() -> None:
    for url in SEED_URLS:
        page_id = make_page_id(url)

        html = fetch_page(url)
        html_hash = make_hash(html)

        state_path = STATE_DIR / f"{page_id}.hash"
        old_hash = read_text(str(state_path))

        if old_hash == html_hash:
            print(f"[SKIP] 변경 없음: {page_id}")
            continue

        print(f"[UPDATE] 변경 감지: {page_id}")

        write_text(str(RAW_HTML_DIR / f"{page_id}.html"), html)
        write_text(str(state_path), html_hash)

        result = process_html(url, html)

        write_json(str(RAW_EXTRACTION_DIR / f"{page_id}.json"), result["raw_extraction"])
        write_json(str(POLICY_SCHEMA_DIR / f"{page_id}.json"), result["policy_schema"])
        write_json(str(CHUNK_SCHEMA_DIR / f"{page_id}.json"), {"chunks": result["chunk_schema"]})