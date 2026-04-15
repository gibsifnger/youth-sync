import sys
sys.path.append(".")

from app.pipeline import process_html

def fake_html(body_text: str) -> str:
    return f"""
    <html>
      <head><title>테스트 페이지</title></head>
      <body>
        <main>
          {body_text.replace(chr(10), "<br>")}
        </main>
      </body>
    </html>
    """

def test_lh_sample_a_schema():
    text = """청년매입임대주택

입주대상
무주택 요건 및 소득·자산 기준을 충족하고 다음 어느 하나에 해당하는 미혼 청년
만 19세 이상 만 39세 이하인 사람
대학생(입학 및 복학 예정자 포함)
취업준비생(고등학교 · 대학교 등을 졸업 · 중퇴 2년 이내인 미취업자)

소득 자산 기준
1순위 : 생계·주거·의료급여 수급자 가구
2순위 : 본인과 부모의 월평균 소득 100% 이하
3순위 : 본인의 월평균 소득 100% 이하

임대조건
1순위 : 보증금 100만원, 임대료 시중시세 40%

거주기간
2년(요건 충족 시 재계약 4회 가능, 최장 10년)

공급시기
분기별 공급
(3,6,9,12월)
"""
    result = process_html("https://www.lh.or.kr/menu.es?mid=a10401020200", fake_html(text))

    policy = result["policy_schema"]
    chunks = result["chunk_schema"]

    assert policy["policy_id"] == "a10401020200"
    assert policy["policy_name"] != ""
    assert policy["category"] == "주거"
    assert policy["age_min"] == 19
    assert policy["age_max"] == 39
    assert policy["housing_condition"] is not None
    assert policy["source_org"] == "LH"
    assert policy["source_type"] == "web_page"

    assert len(chunks) >= 4
    assert "chunk_id" in chunks[0]
    assert "section_title" in chunks[0]
    assert "chunk_text" in chunks[0]