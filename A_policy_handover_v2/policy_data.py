import requests
import pandas as pd
import time
from datetime import datetime

URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
API_KEY = "2bbe939c-244e-48be-bc27-b658929481c0"

METRO_ZIP_CODES = [
    # 서울 25개 자치구
    "11110", "11140", "11170", "11200", "11215",
    "11230", "11260", "11290", "11305", "11320",
    "11350", "11380", "11410", "11440", "11470",
    "11500", "11530", "11545", "11560", "11590",
    "11620", "11650", "11680", "11710", "11740",

    # 인천 10개 구·군 (실제 코드 28xxx)
    "28110", "28140", "28177", "28185", "28200",
    "28237", "28245", "28260", "28710", "28720",

    # 경기 47개 시·군·구 (실제 코드)
    "41111", "41113", "41115", "41117",  # 수원시 4개 구
    "41131", "41133", "41135",           # 성남시 3개 구
    "41150",                             # 의정부시
    "41171", "41173",                    # 안양시 2개 구
    "41192", "41194", "41196",           # 부천시 3개 구
    "41210",                             # 광명시
    "41220",                             # 평택시
    "41250",                             # 동두천시
    "41271", "41273",                    # 안산시 2개 구
    "41281", "41285", "41287",           # 고양시 3개 구
    "41290",                             # 과천시
    "41310",                             # 구리시
    "41360",                             # 남양주시
    "41370",                             # 오산시
    "41390",                             # 시흥시
    "41410",                             # 군포시
    "41430",                             # 의왕시
    "41450",                             # 하남시
    "41461", "41463", "41465",           # 용인시 3개 구
    "41480",                             # 파주시
    "41500",                             # 이천시
    "41550",                             # 안성시
    "41570",                             # 김포시
    "41591", "41593", "41595", "41597",  # 화성시 4개 구
    "41610",                             # 광주시
    "41630",                             # 양주시
    "41650",                             # 포천시
    "41670",                             # 여주시
    "41800",                             # 연천군
    "41820",                             # 가평군
    "41830",                             # 양평군
]
# 11110,11140,11170,...41650
ZIP_PARAM = ",".join(METRO_ZIP_CODES)
CATEGORIES = ["일자리", "주거"]


def fetch_page(api_key, category, page, page_size=100):
    params = {
        "apiKeyNm": api_key,
        "pageNum": page,
        "pageSize": page_size,
        "pageType": "1",
        "rtnType": "json",
        "lclsfNm": category,
        "zipCd": ZIP_PARAM,
    }
    resp = requests.get(URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    policies = data.get("result", {}).get("youthPolicyList", [])
    return policies


def fetch_category(api_key, category, page_size=100):
    all_rows = []
    page = 1

    while True:
        try:
            rows = fetch_page(api_key, category, page, page_size)
        except Exception as e:
            print("\n  오류 [" + category + "] 페이지 " + str(page) + ": " + str(e))
            break

        if not rows:
            break

        for row in rows:
            row["_category"] = category

        all_rows.extend(rows)
        print("  [" + category + "] " + str(page) + "페이지 -> " + str(len(rows)) + "건 (누적 " + str(len(all_rows)) + "건)")

        if len(rows) < page_size:
            break

        page += 1
        time.sleep(0.3)

    print("  [" + category + "] 완료 - 총 " + str(len(all_rows)) + "건")
    return all_rows


def main():
    print("온통청년 정책 데이터 수집 시작")
    print("지역: 서울 + 인천 + 경기")
    print("카테고리: 일자리, 주거")
    print("")

    all_policies = []

    for category in CATEGORIES:
        print(">> " + category + " 수집 중...")
        rows = fetch_category(API_KEY, category)
        all_policies.extend(rows)
        print("")

    if not all_policies:
        print("수집된 데이터가 없습니다.")
        return

    df = pd.DataFrame(all_policies)

    before = len(df)
    if "plcyNo" in df.columns:
        df = df.drop_duplicates(subset=["plcyNo"])
    after = len(df)
    if before != after:
        print("중복 제거: " + str(before) + "건 -> " + str(after) + "건")

    today = datetime.now().strftime("%Y%m%d")

    for category in CATEGORIES:
        sub = df[df["_category"] == category].drop(columns=["_category"])
        fname = "policy_master_" + category + "_" + today + ".csv"
        sub.to_csv(fname, index=False, encoding="utf-8-sig")
        print("저장 완료: " + fname + " (" + str(len(sub)) + "건)")

    fname_all = "policy_master_" + today + ".csv"
    df.to_csv(fname_all, index=False, encoding="utf-8-sig")
    print("저장 완료: " + fname_all + " (" + str(len(df)) + "건, 통합)")


if __name__ == "__main__":
    main()