# sentiment_analysis.py
from textblob import TextBlob
from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME

# MongoDB client setup
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def analyze_sentiment(brand_name):
    # Placeholder for simulated tweets and analysis
    tweets = [f"{brand_name} is great!", f"{brand_name} is disappointing.", "I love using " + brand_name]
    results = []

    for tweet in tweets:
        sentiment = TextBlob(tweet).sentiment.polarity
        sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
        results.append({"tweet": tweet, "sentiment": sentiment_label})
    
    collection.insert_one({"brand": brand_name, "results": results})
    return results
