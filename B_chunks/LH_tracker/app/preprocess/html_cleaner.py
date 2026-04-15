from bs4 import BeautifulSoup

def strip_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")