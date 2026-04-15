# 📊 LH 정책 비정형 데이터 추출 모듈 (B 파트)

> LH 정책 페이지의 비정형 데이터를 구조화하여 검색 및 추천 시스템에 활용 가능한 형태로 변환하는 모듈

---

## 📌 1. 개요

본 모듈은 LH 홈페이지의 정책 설명 페이지를 대상으로  
비정형 텍스트 데이터를 수집하고, 이를 구조화된 JSON 데이터로 변환하는 기능을 수행합니다.

- 대상: LH 청년 주거 정책 페이지
- 목적: 정책 정보를 분석하여 백엔드 및 검색 시스템에서 활용 가능한 데이터 생성

---

## 📌 2. 주요 기능

### 🔹 웹 페이지 수집

- 특정 URL 패턴의 LH 정책 페이지 HTML 수집

### 🔹 본문 텍스트 추출

- HTML에서 정책 설명 영역만 추출

### 🔹 청킹 (Chunking)

- 텍스트를 의미 단위로 분리
  - 입주대상
  - 소득 기준
  - 임대조건
  - 거주기간
  - 공급시기

### 🔹 정보 추출

- 연령 조건 (age_min, age_max)
- 대상군 (청년, 대학생, 취업준비생 등)
- 주택 조건 (무주택 등)
- 소득 조건 (순위 기반 텍스트)
- 임대 조건 (보증금, 임대료)
- 거주 기간

### 🔹 스키마 변환

추출된 데이터를 아래 2가지 형태로 변환:

- 정책 데이터 (policy_schema)
- 청크 데이터 (chunk_schema)

---

## 📌 3. 데이터 구조

### 🔹 정책 데이터 (policy_schema)

```json
{
  "policy_id": "a10401020400",
  "policy_name": "청년 전세임대주택",
  "category": "주거",
  "subcategory": "전세임대",
  "region_scope": "전국",
  "age_min": 19,
  "age_max": 39,
  "employment_condition": "청년, 대학생, 취업준비생",
  "housing_condition": "무주택",
  "income_condition_text": "...",
  "apply_start_date": null,
  "apply_end_date": null,
  "apply_status": "안내중",
  "source_org": "LH",
  "source_url": "...",
  "summary": "...",
  "source_type": "web_page"
}
### 청크 데이터
{
  "chunks": [
    {
      "chunk_id": "a10401020400_1",
      "policy_id": "a10401020400",
      "policy_name": "청년 전세임대주택",
      "issuing_org": "LH",
      "source_doc_name": "청년 전세임대주택",
      "source_url": "...",
      "section_title": "입주대상",
      "chunk_text": "...",
      "chunk_order": 1,
      "has_table": false,
      "doc_type": "web_page",
      "created_from": "section_chunking"
    }
  ]
}
📌 4. 실행 방법
python -m app.run_real_test

📌 5. 결과 확인

output/manual_test/
raw_extraction.json (원본 추출 데이터)
policy_schema.json (정책 데이터)
chunk_schema.json (청크 데이터)

📌 6. 백엔드 연동 방법
🔹 정책 데이터 전송
POST /api/policies
Body:
{ policy_schema }
🔹 청크 데이터 전송
POST /api/chunks

Body:

{
  "chunks": [...]
}
📌 7. 협업 규칙
🔹 필드명 규칙
policy_name (title 사용 금지)
source_url (url 사용 금지)
🔹 타입 규칙
age: int
리스트: 배열 형태 유지
🔹 Null 허용
날짜 필드: null 가능

📌 8. 디렉토리 구조
app/
├── fetchers/
├── preprocess/
├── extractors/
├── mappers/
├── pipeline.py
├── run_real_test.py

📌 9. 향후 개선
소득 조건 정량화
지역 정보 정밀화
벡터 검색 연동
사용자 조건 매칭 기능 추가

📌 10. 담당 역할
비정형 데이터 수집 및 정제
텍스트 구조화 및 스키마 변환
백엔드 연동용 데이터 제공
```
