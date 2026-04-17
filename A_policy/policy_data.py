import requests
import pandas as pd
import time

# API 엔드포인트
url = "https://www.youthcenter.go.kr/go/ythip/getPlcy"

def fetch_all_policies(api_key):
    all_policies = []
    page = 1
    display_count = 100  # 한 페이지당 가져올 건수 (최대치인 100 권장)

    print("🚀 전체 청년 정책 데이터 수집을 시작합니다...")

    while True:
        # 특정 카테고리(lclsfNm)나 지역(zipCd) 파라미터를 제외하면 전체 데이터를 불러옵니다.
        params = {
            "apiKeyNm": api_key,
            "pageIndex": page,
            "display": 100
        }

        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # API 응답에서 정책 리스트 추출
                # 데이터 구조: data -> result -> youthPolicyList
                policies = data.get("result", {}).get("youthPolicyList", [])

                if not policies:
                    print(f"\n🏁 모든 데이터를 수집했습니다. (총 {len(all_policies)}건)")
                    break

                all_policies.extend(policies)
                print(f"   [{page}페이지] {len(policies)}건 수집 중... (누적: {len(all_policies)}건)", end="\r")
                
                # 다음 페이지로
                page += 1
                
                # 서버 부하 방지를 위해 아주 짧은 휴식 (필요 시 주석 해제)
                # time.sleep(0.1) 
            else:
                print(f"\n❌ API 호출 에러: {response.status_code}")
                break

        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            break

    return all_policies

if __name__ == "__main__":
    # 1. 실제 발급받은 키 입력
    MY_API_KEY = "2bbe939c-244e-48be-bc27-b658929481c0" 

    # 2. 데이터 가져오기
    policy_data = fetch_all_policies(MY_API_KEY)

    # 3. 데이터프레임 변환 및 저장
    if policy_data:
        df = pd.DataFrame(policy_data)
        
        # 파일명을 'all_policies_날짜.csv' 형태로 저장하면 관리가 편합니다.
        output_name = "policy_master_all.csv"
        df.to_csv(output_name, index=False, encoding="utf-8-sig")
        print(f"✅ 저장 완료: {output_name}")
    else:
        print("데이터를 가져오지 못해 파일을 생성하지 않았습니다.")