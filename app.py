# AI News Agent - Kenya & Global Real-Time News
# Requirements: requests, openai, feedparser, newspaper3k, Flask (for API)

import os
import feedparser
import requests
from newspaper import Article
from flask import Flask, jsonify, request

# === CONFIGURATION === #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Set your key as env var
NEWS_FEEDS = [
    "https://www.standardmedia.co.ke/rss/headlines.php",
    "https://www.nation.africa/kenya/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
]
HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

# === FETCH LATEST ARTICLES === #
def get_articles():
    articles = []
    for url in NEWS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # Limit for demo
            try:
                article = Article(entry.link)
                article.download()
                article.parse()
                articles.append({
                    "title": article.title,
                    "url": entry.link,
                    "text": article.text
                })
            except Exception as e:
                print(f"Failed to fetch: {entry.link}", e)
    return articles

# === AI REWRITE === #
def rewrite_article(original_text):
    prompt = f"""
    Rewrite this news article in a simple, natural, human tone. Make it SEO-friendly for Kenyan readers.
    Use short sentences, clear subheadings, and a summary. Include keywords like 'Kenya news', 'latest updates'.

    Article:
    {original_text}
    """
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=HEADERS,
        json={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )
    return response.json()['choices'][0]['message']['content']

# === FLASK API FOR TRIGGERING === #
app = Flask(__name__)

@app.route("/generate-news", methods=["GET"])
def generate_news():
    results = []
    for article in get_articles():
        rewritten = rewrite_article(article["text"])
        results.append({
            "original_title": article["title"],
            "url": article["url"],
            "generated": rewritten
        })
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
