import os
import json
import argparse
import time
from collections import defaultdict
from datetime import datetime
import ollama  # 👈 nouvelle bibliothèque

def load_articles(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def group_by_topic(articles):
    clusters = defaultdict(list)
    for art in articles:
        clusters[art["title"].strip()].append(art)
    return clusters

def summarize_cluster(cluster_articles, model="gemma:2b"):
    # Résumé de test simple pour éviter blocage
    titles = "\n".join(f"- {a['source']}: {a['title']}" for a in cluster_articles)
    return f"Résumé test pour {len(cluster_articles)} articles :\n{titles}"



def main():
    parser = argparse.ArgumentParser(description="Génère une revue de presse")
    parser.add_argument("input_file", help="Fichier JSON d'articles (ex: data/articles_2025-05-21.json)")
    args = parser.parse_args()

    articles = load_articles(args.input_file)
    print(f"[INFO] {len(articles)} articles chargés")

    clusters = group_by_topic(articles)
    print(f"[INFO] {len(clusters)} groupes détectés")

    results = []
    for idx, (topic, articles_group) in enumerate(clusters.items(), 1):
        print(f"[INFO] Cluster {idx}: {topic[:60]}…")
        articles_group = sorted(articles_group, key=lambda a: a["published_at"], reverse=True)[:3]
        review = summarize_cluster(articles_group)
        results.append({
            "cluster_id": idx,
            "topic": topic,
            "sources": [a["source"] for a in articles_group],
            "review": review
        })
        time.sleep(1)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_file = f"data/press_review_{date_str}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Revue sauvegardée dans {output_file}")

if __name__ == "__main__":
    main()
