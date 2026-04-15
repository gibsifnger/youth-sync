import re
from bs4 import BeautifulSoup

def extract_title(soup: BeautifulSoup) -> str:
    if soup.title:
        return soup.title.get_text(" ", strip=True)
    h1 = soup.find(["h1", "h2", "h3"])
    return h1.get_text(" ", strip=True) if h1 else ""

def extract_main_text(soup: BeautifulSoup) -> str:
    # 1차: main/article/div 중 본문 길이 큰 영역 우선
    candidates = soup.find_all(["main", "article", "div", "section"])
    best_text = ""

    for tag in candidates:
        text = tag.get_text("\n", strip=True)
        if len(text) > len(best_text):
            best_text = text

    # 너무 짧으면 전체 문서 텍스트 fallback
    if len(best_text) < 300:
        best_text = soup.get_text("\n", strip=True)

    # 공백 정리
    best_text = re.sub(r"[ \t]+", " ", best_text)
    best_text = re.sub(r"\n{2,}", "\n", best_text)
    return best_text.strip()