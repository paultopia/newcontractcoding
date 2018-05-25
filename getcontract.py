import requests
from bs4 import BeautifulSoup

browheader = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7"}


def fetch(link):
    try:
        response = requests.get(link, timeout=2, headers=browheader)
    except:
        return None
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    return None


def extract_text(soup):
    if soup is None:
        return None
    for crap in soup(["script", "style", "meta"]):
        crap.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n\n'.join(chunk for chunk in chunks if chunk)
    return text


def get_contract(url):
    soup = fetch(url)
    text = extract_text(soup)
    if text is None:
        return None
    return text
