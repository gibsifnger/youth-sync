import json
from pathlib import Path

from app.fetchers.lh_fetcher import fetch_page
from app.pipeline import process_html

TEST_URLS = [
    "https://www.lh.or.kr/menu.es?mid=a10401020200",
    "https://www.lh.or.kr/menu.es?mid=a10401020300",
    "https://www.lh.or.kr/menu.es?mid=a10401020400",
]


def save_json(path: str, data: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    for url in TEST_URLS:
        page_id = url.split("mid=")[-1]
        print(f"\n[TEST] {url}")

        html = fetch_page(url)
        result = process_html(url, html)

        save_json(f"output/manual_test/{page_id}_raw.json", result["raw_extraction"])
        save_json(f"output/manual_test/{page_id}_policy.json", result["policy_schema"])
        save_json(f"output/manual_test/{page_id}_chunks.json", {"chunks": result["chunk_schema"]})

        print(f"저장 완료: {page_id}")
        print(json.dumps(result["policy_schema"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
    