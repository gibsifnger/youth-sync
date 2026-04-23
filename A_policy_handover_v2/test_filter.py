import pandas as pd

# -----------------------------
# 1. 데이터 불러오기
# -----------------------------
df = pd.read_csv("policy_master.csv")

print("📊 전체 데이터 개수:", len(df))


# -----------------------------
# 2. 필터 함수
# -----------------------------
def filter_policies(region=None, age=None, category=None, status=None):
    result = df.copy()

    # 지역 필터 (전국 포함)
    if region:
        result = result[
            (result["region"] == region) | (result["region"] == "전국")
        ]

    # 카테고리 필터
    if category:
        result = result[result["category"] == category]

    # 상태 필터
    if status:
        result = result[result["apply_status"] == status]

    # 나이 필터 (null 허용 유지)
    if age:
        result = result[
            (result["age_min"].isna() | (result["age_min"] <= age)) &
            (result["age_max"].isna() | (result["age_max"] >= age))
        ]

    return result


# -----------------------------
# 3. 데이터 분포 확인 (디버깅용)
# -----------------------------
print("\n📌 region 분포")
print(df["region"].value_counts())

print("\n📌 category 분포")
print(df["category"].value_counts())

print("\n📌 상태 분포")
print(df["apply_status"].value_counts())


# -----------------------------
# 4. 테스트 1 (완화 버전)
# -----------------------------
print("\n✅ 테스트 1: 서울 27세 주거 (전국 포함)")

test1 = filter_policies(region="서울", age=27, category="주거")

print("결과 개수:", len(test1))
print(test1[["policy_name", "region", "category"]].head(5))


# -----------------------------
# 5. 테스트 2 (완화 버전)
# -----------------------------
print("\n✅ 테스트 2: 경기 25세 취업 (전국 포함)")

test2 = filter_policies(region="경기", age=25, category="취업")

print("결과 개수:", len(test2))
print(test2[["policy_name", "region", "category"]].head(5))


# -----------------------------
# 6. 테스트 3 (완화 버전)
# -----------------------------
print("\n✅ 테스트 3: 서울 26세 신청중 (전국 포함)")

test3 = filter_policies(region="서울", age=26, status="신청중")

print("결과 개수:", len(test3))
print(test3[["policy_name", "region", "apply_status"]].head(5))


# -----------------------------
# 7. 추가 안전 테스트
# -----------------------------
print("\n🔥 전체 조건 완화 테스트")

test_all = filter_policies(age=25)

print("결과 개수:", len(test_all))
print(test_all[["policy_name", "region", "category"]].head(5))