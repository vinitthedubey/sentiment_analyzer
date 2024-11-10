# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from sentiment_analysis import analyze_sentiment
from config import MONGO_URI, DATABASE_NAME, SECRET_KEY
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY
bcrypt = Bcrypt(app)

# MongoDB client setup
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]

# Function to fetch Google Trends data
def fetch_google_trends(brand_name):
    pytrends = TrendReq()
    pytrends.build_payload([brand_name], timeframe='now 7-d')  # Last 7 days
    trends = pytrends.interest_over_time()

    if not trends.empty:
        # Plot the trend data
        plt.figure(figsize=(10, 6))
        plt.plot(trends.index, trends[brand_name], label=brand_name, color='blue', linewidth=2)
        plt.title(f'Search Interest for {brand_name} (Last 7 Days)')
        plt.xlabel('Date')
        plt.ylabel('Search Interest')
        plt.legend()
        
        # Save the plot as an image
        image_path = os.path.join('static', 'trend.png')
        plt.savefig(image_path)
        plt.close()
        
        return image_path
    else:
        return None



# Home page with login
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users_collection.find_one({"username": username})
        
        if user and bcrypt.check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("main"))
        return render_template("home.html", error="Invalid credentials")
    
    return render_template("home.html")

# Route for handling the trend search
@app.route('/search', methods=['POST'])
def search():
    brand_name = request.form['brand_name']
    image_path = fetch_google_trends(brand_name)
    if image_path:
        return render_template('trend.html', brand_name=brand_name, image_path=image_path)
    else:
        return "No trend data found for this brand name."

# Registration route
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
    users_collection.insert_one({"username": username, "password": password})
    return redirect(url_for("home"))

# Main sentiment analysis page
@app.route("/main", methods=["GET", "POST"])
def main():
    if "username" not in session:
        return redirect(url_for("home"))
    
    results = None
    if request.method == "POST":
        brand_name = request.form["brand_name"]
        results = analyze_sentiment(brand_name)
    
    return render_template("main.html", results=results)

# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
