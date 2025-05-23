# utils/storage.py
import json
from pathlib import Path
from datetime import datetime

def save_articles_individual(articles, directory="data/articles"):
    Path(directory).mkdir(parents=True, exist_ok=True)
    for i, article in enumerate(articles):
        file_path = Path(directory) / f"article_{i+1}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

def save_articles_combined(articles, directory="data"):
    """Sauvegarde tous les articles dans un seul fichier nommé articles_YYYY-MM-DD.json"""
    Path(directory).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = Path(directory) / f"articles_{date_str}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Articles regroupés sauvegardés dans {file_path}")
