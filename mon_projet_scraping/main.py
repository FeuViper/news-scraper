from scraper.extractor import scrape_rss
from utils.storage import save_articles_individual, save_articles_combined
from datetime import datetime, timedelta, timezone
import feedparser
from email.utils import parsedate_to_datetime

# Médias et leurs flux RSS
MEDIA_SOURCES = {
    "Le Monde": "https://www.lemonde.fr/rss/en_continu.xml",
    "France Info": "https://www.francetvinfo.fr/titres.rss",
    "Le Figaro": "https://www.lefigaro.fr/rss/figaro_actualites.xml",
    "Libération": "https://www.liberation.fr/arc/outboundfeeds/rss-all/collection/accueil-une/",
    "Valeurs Actuelles": "https://www.valeursactuelles.com/feed?post_type=post"
}

def is_recent(pub_date_str):
    try:
        pub_dt = parsedate_to_datetime(pub_date_str)
        if not pub_dt:
            return False
        if pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        else:
            pub_dt = pub_dt.astimezone(timezone.utc)
        now = datetime.now(timezone.utc)
        return now - pub_dt <= timedelta(hours=24)
    except Exception as e:
        print(f"Erreur dans is_recent pour '{pub_date_str}': {e}")
        return False



def normalize_article(raw_article, source_name="source inconnue"):
    return {
        "source": source_name,
        "title": raw_article.get("titre", ""),
        "published_at": raw_article.get("date", ""),
        "text": raw_article.get("résumé", "")
    }

def main():
    all_articles = []

    for media_name, rss_url in MEDIA_SOURCES.items():
        print(f"\n📰 Traitement de {media_name}...")
        raw_articles = scrape_rss(rss_url)

        today_articles = []
        for a in raw_articles:
            date_raw = a.get("date", "")
            print(f"   - Article : {a.get('titre', '')}")
            print(f"     Date brute : {date_raw}")
            if is_recent(date_raw):
                print("     ✅ Article récent (<24h)")
                today_articles.append(normalize_article(a, source_name=media_name))
            else:
                print("     ❌ Article trop ancien")

        print(f"   ➕ {len(today_articles)} articles du jour récupérés.")
        all_articles.extend(today_articles)

    save_articles_combined(all_articles)

if __name__ == "__main__":
    main()