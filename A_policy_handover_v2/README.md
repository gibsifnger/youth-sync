# A_policy

정형 정책 메타데이터 레이어

주요 산출물:

- policy_master.csv
- policy_metadata.json

데이터명: 청년 정책 통합 데이터 (policy_master)

설명:
청년 대상 일자리 및 주거 정책 정보를 통합하여 정제한 데이터로,
챗봇 추천 및 검색 시스템에 활용됨.

---

[컬럼 정의]

1. policy_id

- 설명: 정책 고유 식별자
- 타입: string
- 예시: "20260415005400212748"
- null 허용: X

2. policy_name

- 설명: 정책 이름
- 타입: string
- 예시: "청년월세 지원사업"
- null 허용: X

3. institution

- 설명: 정책 운영 기관
- 타입: string
- 예시: "중소벤처기업진흥공단"
- null 허용: O (없을 경우 "정보없음")

4. region

- 설명: 정책 적용 지역
- 타입: string
- 허용값:
  - 서울
  - 경기
  - 전남
  - 전국
  - 기타
- null 허용: X

5. age_min

- 설명: 최소 신청 가능 나이
- 타입: number
- 예시: 19
- null 허용: O

6. age_max

- 설명: 최대 신청 가능 나이
- 타입: number
- 예시: 34
- null 허용: O

7. category

- 설명: 정책 유형
- 타입: string
- 허용값:
  - 취업
  - 주거
- null 허용: X

8. apply_start_date

- 설명: 신청 시작일
- 타입: string (YYYY-MM-DD)
- 예시: "2026-05-21"
- null 허용: O

9. apply_end_date

- 설명: 신청 종료일
- 타입: string (YYYY-MM-DD)
- 예시: "2026-06-18"
- null 허용: O

10. apply_status

- 설명: 신청 상태
- 타입: string
- 허용값:
  - 신청중
  - 예정
  - 마감
  - 상시
- null 허용: X

11. source_url

- 설명: 정책 상세 페이지 URL
- 타입: string
- 예시: "https://bokjiro.go.kr"
- null 허용: O

---

[데이터 특징]

- 정책 1건 = 1 row 구조
- 일자리 / 주거 정책만 포함
- 중복 정책 제거 완료
- 날짜 기반 신청 상태 자동 생성
- 지역 정보 일부는 정책명 기반으로 보완됨

---

[활용 목적]

- 청년 정책 추천 챗봇
- 조건 기반 정책 검색 시스템

※ 본 데이터는 청년정책 API 기반으로 수집 후 정제된 데이터임
