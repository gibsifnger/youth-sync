import pandas as pd
import re
from datetime import datetime
import os

def clean_html(text):
    """HTML 태그 제거 및 공백 정제"""
    if pd.isna(text):
        return None
    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[\r\n\t]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def parse_date(date_val):
    """YYYYMMDD 형태의 날짜를 YYYY-MM-DD 포맷으로 변환"""
    if pd.isna(date_val) or str(date_val).strip() == "":
        return None
    
    # 텍스트에서 숫자만 추출
    nums = re.sub(r'\D', '', str(date_val))
    if len(nums) >= 8:
        return f"{nums[0:4]}-{nums[4:6]}-{nums[6:8]}"
    return None

def determine_status(start_date, end_date):
    """시작/종료일을 기준으로 현재 모집 상태 계산"""
    if not start_date and not end_date:
        return "상시모집"
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if start_date and start_date > today:
        return "예정"
    elif end_date and end_date < today:
        return "마감"
    else:
        return "진행중"

def main():
    print(">> 최신 API 스키마 맞춤형 데이터 전처리 시작")
    
    # 질문자님의 파일명(20260420)에 맞추거나 오늘 날짜로 자동 탐색
    today = datetime.now().strftime("%Y%m%d")
    file_name = f"policy_master_{today}.csv" 
    
    # 만약 파일 이름이 다르면 직접 지정 (예: file_name = "policy_master_20260420.csv")
    if not os.path.exists(file_name):
        file_name = "policy_master_20260420.csv" 
        
    if not os.path.exists(file_name):
        print(f"[오류] 원본 파일을 찾을 수 없습니다: {file_name}")
        return
        
    df = pd.read_csv(file_name)
    transformed_data = []
    
    for _, row in df.iterrows():
        # 1. 날짜 추출 (bizPrdBgngYmd, bizPrdEndYmd)
        apply_start = parse_date(row.get('bizPrdBgngYmd'))
        apply_end = parse_date(row.get('bizPrdEndYmd'))
        
        # 2. 상태 계산
        status = determine_status(apply_start, apply_end)
        
        # 3. 나이 추출 (업데이트된 스키마에서는 숫자로 바로 제공됨!)
        age_min = float(row.get('sprtTrgtMinAge')) if pd.notna(row.get('sprtTrgtMinAge')) else 19.0
        age_max = float(row.get('sprtTrgtMaxAge')) if pd.notna(row.get('sprtTrgtMaxAge')) else 39.0
        
        # 4. 기관명 (운영기관 또는 주관기관)
        institution = clean_html(row.get('operInstCdNm')) or clean_html(row.get('sprvsnInstCdNm')) or "정보없음"
        
        # 5. 지역 추출 (등록 상위 기관명 등에서 서울/경기/인천 필터링)
        region_raw = str(row.get('rgtrHghrkInstCdNm', '')) + " " + str(row.get('rgtrInstCdNm', ''))
        if "서울" in region_raw: region = "서울"
        elif "경기" in region_raw: region = "경기"
        elif "인천" in region_raw: region = "인천"
        else: region = "기타"
        
        # 6. 카테고리 (수집 시 추가한 _category가 우선, 없으면 lclsfNm 활용)
        category = row.get('_category') if pd.notna(row.get('_category')) else clean_html(row.get('lclsfNm'))
        
        # 새로운 스키마로 최종 매핑
        new_row = {
            "policy_id": str(row.get('plcyNo', '')),
            "policy_name": clean_html(row.get('plcyNm', '')),
            "institution": institution,
            "region": region,
            "age_min": age_min,
            "age_max": age_max,
            "category": category,
            "apply_start_date": apply_start,
            "apply_end_date": apply_end,
            "apply_status": status,
            "source_url": row.get('aplyUrlAddr') if pd.notna(row.get('aplyUrlAddr')) else row.get('refUrlAddr1')
        }
        transformed_data.append(new_row)
        
    final_df = pd.DataFrame(transformed_data)
    
    # JSON 파일로 저장
    processed_json_fname = f"policy_master_preprocessed_{today}.json"
    final_df.to_json(
        processed_json_fname, 
        orient="records", 
        force_ascii=False, 
        indent=4
    )
    print(f"[성공] 데이터가 꽉 찬 JSON 파일 저장 완료: {processed_json_fname} ({len(final_df)}건)")

if __name__ == "__main__":
    main()