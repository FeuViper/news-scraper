import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin, urlparse
import re
import json

HEADERS = {"User-Agent": "Mozilla/5.0"}

APIS_KNOWN = {
    "newsapi.org": "https://newsapi.org/v2/top-headlines",
}

def get_domain(url):
    return urlparse(url).netloc.lower()

def is_scraping_allowed(url):
    domain = get_domain(url)
    robots_url = f"https://{domain}/robots.txt"
    try:
        response = requests.get(robots_url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            return True
        content = response.text.lower()
        if "disallow: /" in content:
            return False
        return True
    except Exception:
        return True

def find_api(url):
    domain = get_domain(url)
    for site, api_url in APIS_KNOWN.items():
        if site in domain:
            return api_url
    return None

def fetch_api_articles(api_url):
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        articles = []
        if "articles" in data:
            for art in data["articles"][:5]:
                articles.append({
                    "titre": art.get("title", ""),
                    "lien": art.get("url", ""),
                    "résumé": art.get("description", "")
                })
        else:
            if isinstance(data, list):
                for art in data[:5]:
                    articles.append({
                        "titre": art.get("title", ""),
                        "lien": art.get("url", ""),
                        "résumé": art.get("summary", "")
                    })
        return articles
    except Exception as e:
        print(f"❌ Erreur API : {e}")
        return []

def find_rss_feed(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("link", type=re.compile("rss|atom", re.I))
        for link in links:
            href = link.get("href")
            if href:
                return urljoin(url, href)
        for suffix in ["/rss", "/feed", "/feeds", "/rss.xml"]:
            test_url = urljoin(url, suffix)
            feed = feedparser.parse(test_url)
            if feed.entries:
                return test_url
    except Exception:
        pass
    return None

def scrape_html_auto(url):
    if not is_scraping_allowed(url):
        print("🚫 Le scraping est interdit par robots.txt, arrêt.")
        return []
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
        articles = []
        for tag in soup.find_all(["article", "div"], limit=10):
            title_tag = tag.find(["h1", "h2", "h3"])
            link_tag = tag.find("a", href=True)
            if title_tag and link_tag:
                titre = title_tag.get_text(strip=True)
                lien = urljoin(url, link_tag["href"])
                articles.append({
                    "titre": titre,
                    "lien": lien
                })
        return articles
    except Exception as e:
        print(f"❌ Erreur scraping HTML : {e}")
        return []

def scrape_rss(rss_url):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:5]:
        articles.append({
            "titre": entry.title,
            "lien": entry.link,
            "date": entry.get("published", ""),
            "résumé": entry.get("summary", "")
        })
    return articles

def process_source(source_url):
    print(f"\n🔍 Traitement de : {source_url}")

    api_url = find_api(source_url)
    if api_url:
        print(f"✅ API détectée : {api_url}")
        return fetch_api_articles(api_url)

    rss = find_rss_feed(source_url)
    if rss:
        print(f"✅ Flux RSS trouvé : {rss}")
        return scrape_rss(rss)

    print("❌ Aucun flux RSS ni API trouvés, tentative de scraping HTML si autorisé...")
    if not is_scraping_allowed(source_url):
        print("🚫 Scraping interdit par robots.txt. Aucune donnée récupérée.")
        return []
    return scrape_html_auto(source_url)

__all__ = ["process_source"]