import requests
import pandas as pd
import time
from datetime import datetime

# ── API 설정 ──────────────────────────────────────────
URL     = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
API_KEY = "2bbe939c-244e-48be-bc27-b658929481c0"

# ── 서울·수도권 법정시군구코드(5자리) ──────────────────
# 서울(11xxx), 인천(23xxx), 경기(41xxx)
METRO_ZIP_CODES = [
    # 서울 25개 자치구
    "11110", "11140", "11170", "11200", "11215",
    "11230", "11260", "11290", "11305", "11320",
    "11350", "11380", "11410", "11440", "11470",
    "11500", "11530", "11545", "11560", "11590",
    "11620", "11650", "11680", "11710", "11740",
    # 인천 8개 구·군
    "23110", "23140", "23170", "23200", "23230",
    "23260", "23290", "23320",
    # 경기 28개 시·군
    "41110", "41130", "41150", "41170", "41190",
    "41210", "41220", "41230", "41250", "41270",
    "41280", "41290", "41310", "41360", "41370",
    "41390", "41410", "41430", "41450", "41461",
    "41480", "41500", "41550", "41570", "41590",
    "41610", "41630", "41650",
]

# API는 zipCd를 콤마로 묶어서 한 번에 전송
ZIP_PARAM = ",".join(METRO_ZIP_CODES)

# ── 수집 대상 카테고리 ────────────────────────────────
CATEGORIES = ["일자리", "주거"]


# ═════════════════════════════════════════════════════
# 단일 (카테고리 × 페이지) 요청
# ═════════════════════════════════════════════════════

def fetch_page(api_key: str, category: str, page: int, page_size: int = 100) -> list[dict]:
    """
    파라미터:
      apiKeyNm   : 인증키
      pageNum    : 페이지 번호
      pageSize   : 페이지당 건수
      pageType   : 1(목록)
      rtnType    : json
      lclsfNm    : 정책대분류명 (일자리 / 주거)
      zipCd      : 법정시군구코드 콤마 구분 (서울+인천+경기)
    """
    params = {
        "apiKeyNm": api_key,
        "pageNum":  page,
        "pageSize": page_size,
        "pageType": "1",           # 1 = 목록
        "rtnType":  "json",
        "lclsfNm":  category,
        "zipCd":    ZIP_PARAM,
    }

    resp = requests.get(URL, params=params, timeout=15)
    resp.raise_for_status()

    data     = resp.json()
    policies = data.get("result", {}).get("youthPolicyList", [])
    return policies


# ═════════════════════════════════════════════════════
# 카테고리별 전체 페이지 수집
# ═════════════════════════════════════════════════════

def fetch_category(api_key: str, category: str, page_size: int = 100) -> list[dict]:
    all_rows = []
    page     = 1

    while True:
        try:
            rows = fetch_page(api_key, category, page, page_size)
        except Exception as e:
            print(f"\n  ❌ [{category}] 페이지 {page} 오류: {e}")
            break

        if not rows:
            break

        # 각 행에 카테고리 태그 추가 (나중에 구분 편하게)
        for row in rows:
            row["_category"] = category

        all_rows.extend(rows)
        print(f"  [{category}] {page}페이지 → {len(rows)}건 (누적 {len(all_rows)}건)", end="\r")

        # 마지막 페이지 판단: 받은 건수가 page_size보다 적으면 종료
        if len(rows) < page_size:
            break

        page += 1
        time.sleep(0.3)   # 서버 부하 방지

    print(f"  [{category}] 완료 — 총 {len(all_rows)}건" + " " * 20)
    return all_rows


# ═════════════════════════════════════════════════════
# 메인 실행
# ═════════════════════════════════════════════════════

def main():
    print("=" * 55)
    print("온통청년 정책 데이터 수집 (서울·수도권 / 일자리·주거)")
    print("=" * 55)
    print(f"대상 지역 코드: {len(METRO_ZIP_CODES)}개 (서울 25, 인천 8, 경기 28)")
    print(f"대상 카테고리: {CATEGORIES}")
    print()

    all_policies = []

    for category in CATEGORIES:
        print(f"▶ {category} 수집 중...")
        rows = fetch_category(API_KEY, category)
        all_policies.extend(rows)
        print()

    if not all_policies:
        print("❌ 수집된 데이터가 없습니다.")
        return

    # ── 데이터프레임 변환 ─────────────────────────
    df = pd.DataFrame(all_policies)

    # 중복 제거 (같은 정책이 여러 지역 코드에 걸릴 수 있음)
    before = len(df)
    if "plcyNo" in df.columns:
        df = df.drop_duplicates(subset=["plcyNo"])
    after = len(df)
    if before != after:
        print(f"중복 제거: {before}건 → {after}건")

    # ── 카테고리별 분리 저장 ──────────────────────
    today = datetime.now().strftime("%Y%m%d")

    for category in CATEGORIES:
        sub = df[df["_category"] == category].drop(columns=["_category"])
        fname = f"policy_master_{category}_{today}.csv"
        sub.to_csv(fname, index=False, encoding="utf-8-sig")
        print(f"✅ {fname} 저장 완료 ({len(sub)}건)")

    # ── 통합 파일 저장 ────────────────────────────
    df_all = df.copy()
    fname_all = f"policy_master_수도권_{today}.csv"
    df_all.to_csv(fname_all, index=False, encoding="utf-8-sig")
    print(f"✅ {fname_all} 저장 완료 ({len(df_all)}건, 통합)")

    # ── 수집 요약 ─────────────────────────────────
    print()
    print("─" * 40)
    print("수집 완료 요약")
    print("─" * 40)
    if "_category" in df.columns:
        for cat, cnt in df["_category"].value_counts().items():
            print(f"  {cat}: {cnt}건")
    print(f"  합계: {len(df)}건")


if __name__ == "__main__":
    main()