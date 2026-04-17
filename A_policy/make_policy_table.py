import pandas as pd
from datetime import datetime

# -----------------------------
# 1. CSV 불러오기
# -----------------------------
job_path = "policy_master_일자리_11000.csv"
house_path = "policy_master_주거_11000.csv"

df_job = pd.read_csv(job_path)
df_house = pd.read_csv(house_path)

# -----------------------------
# 2. 데이터 합치기
# -----------------------------
df = pd.concat([df_job, df_house], ignore_index=True)

print(f"📊 원본 데이터 개수: {len(df)}")

# -----------------------------
# 3. 컬럼명 통일
# -----------------------------
df = df.rename(columns={
    "plcyNo": "policy_id",
    "plcyNm": "policy_name",
    "operInstCdNm": "institution",
    "zipCd": "region",
    "sprtTrgtMinAge": "age_min",
    "sprtTrgtMaxAge": "age_max",
    "lclsfNm": "category",
    "bizPrdBgngYmd": "apply_start_date",
    "bizPrdEndYmd": "apply_end_date",
    "aplyUrlAddr": "source_url"
})

# -----------------------------
# 4. 필요한 컬럼만 선택
# -----------------------------
df = df[
    [
        "policy_id", "policy_name", "institution",
        "region", "age_min", "age_max",
        "category", "apply_start_date",
        "apply_end_date", "source_url"
    ]
]

# -----------------------------
# 5. 날짜 변환
# -----------------------------
def parse_date(date_val):
    try:
        if pd.isna(date_val):
            return None
        date_val = str(int(date_val))
        return datetime.strptime(date_val, "%Y%m%d").strftime("%Y-%m-%d")
    except:
        return None

df["apply_start_date"] = df["apply_start_date"].apply(parse_date)
df["apply_end_date"] = df["apply_end_date"].apply(parse_date)

# -----------------------------
# 6. 상태값 생성
# -----------------------------
def get_status(start, end):
    today = datetime.today().date()

    try:
        if start and end:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()

            if start_date <= today <= end_date:
                return "신청중"
            elif today < start_date:
                return "예정"
            else:
                return "마감"
        return "상시"
    except:
        return "상시"

df["apply_status"] = df.apply(
    lambda x: get_status(x["apply_start_date"], x["apply_end_date"]),
    axis=1
)

# -----------------------------
# 7. 지역 정규화 (🔥 개선)
# -----------------------------
def normalize_region(region, policy_name):
    text = str(region) + " " + str(policy_name)

    if "서울" in text or "중랑" in text:
        return "서울"
    elif "경기" in text or "고양" in text:
        return "경기"
    elif "광양" in text:
        return "전남"
    elif "부산" in text:
        return "부산"
    elif "대구" in text:
        return "대구"
    elif "인천" in text:
        return "인천"
    elif "국토부" in text:
        return "전국"
    else:
        return "기타"

df["region"] = df.apply(
    lambda x: normalize_region(x["region"], x["policy_name"]),
    axis=1
)

# -----------------------------
# 8. 카테고리 정리
# -----------------------------
def normalize_category(cat):
    if pd.isna(cat):
        return "기타"

    cat = str(cat)

    if "일자리" in cat or "취업" in cat:
        return "취업"
    elif "주거" in cat:
        return "주거"
    else:
        return "기타"

df["category"] = df["category"].apply(normalize_category)
df = df[df["category"].isin(["취업", "주거"])]

# -----------------------------
# 9. 나이 처리
# -----------------------------
df["age_min"] = pd.to_numeric(df["age_min"], errors="coerce")
df["age_max"] = pd.to_numeric(df["age_max"], errors="coerce")

df.loc[df["age_min"] == 0, "age_min"] = None
df.loc[df["age_max"] == 0, "age_max"] = None

# -----------------------------
# 10. 기관 null 처리 (🔥 추가)
# -----------------------------
df["institution"] = df["institution"].fillna("정보없음")

# -----------------------------
# 11. 중복 제거
# -----------------------------
df = df.drop_duplicates(subset=["policy_name", "institution"])

print(f"📊 정제 후 데이터 개수: {len(df)}")

# -----------------------------
# 12. 최종 컬럼 정리
# -----------------------------
final_columns = [
    "policy_id", "policy_name", "institution",
    "region", "age_min", "age_max",
    "category", "apply_start_date",
    "apply_end_date", "apply_status",
    "source_url"
]

df = df[final_columns]

# -----------------------------
# 13. 저장
# -----------------------------
df.to_csv("policy_master.csv", index=False, encoding="utf-8-sig")
df.to_json("policy_metadata.json", orient="records", force_ascii=False, indent=2)

print("✅ policy_master.csv 생성 완료")
print("✅ policy_metadata.json 생성 완료")

# -----------------------------
# 14. 샘플 출력
# -----------------------------
print("\n📌 샘플 데이터:")
print(df.head(5))

print("\n📌 지역 분포:")
print(df["region"].value_counts())

print("\n📌 기관 null 여부 확인:")
print(df["institution"].isnull().sum())