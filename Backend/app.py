from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import requests
import logging
import numpy as np

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow cross-origin requests

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# SocialVerse API Base URL and Headers
base_url = "https://api.socialverseapp.com"
headers = {
    "Flic-Token": "flic_4ae0f84e6f01e7198afd37a5c68734dc3884221c140e2ac6bcb0880b8af885a5"
}

# Helper function to fetch paginated data from API
def fetch_paginated_data(endpoint, page_size=1000):
    """
    Fetch paginated data from a given API endpoint.
    :param endpoint: API endpoint (relative to base_url)
    :param page_size: Number of records per page
    :return: List of all fetched records
    """
    page = 1
    results = []
    while True:
        url = f"{base_url}{endpoint}?page={page}&page_size={page_size}"
        logger.debug(f"Fetching data from: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("posts", [])
            if not data:  # Break loop if no more data
                break
            results.extend(data)
            page += 1
        else:
            logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")
            break
    return results

# Function to calculate trending videos based on global popularity
def get_trending_videos(df_posts, top_n=5):
    """
    Get top trending videos based on global popularity (upvotes + views).
    :param df_posts: DataFrame containing video data
    :param top_n: Number of top trending videos to return
    :return: DataFrame with trending videos
    """
    try:
        df_posts["global_popularity"] = df_posts["upvote_count"] + df_posts["view_count"]
        trending_videos = df_posts.sort_values("global_popularity", ascending=False).head(top_n)
        return trending_videos
    except Exception as e:
        logger.error(f"Error calculating trending videos: {e}")
        return pd.DataFrame()

# Function to recommend videos by category
def get_category_recommendations(df_posts, category, top_n=5):
    """
    Recommend videos based on a specific category.
    :param df_posts: DataFrame containing video data
    :param category: Target category for recommendations
    :param top_n: Number of recommendations to return
    :return: DataFrame with recommended videos
    """
    try:
        category_videos = df_posts[df_posts["category"] == category]
        category_videos["category_popularity"] = category_videos["upvote_count"] + category_videos["view_count"]
        recommendations = category_videos.sort_values("category_popularity", ascending=False).head(top_n)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting category recommendations: {e}")
        return pd.DataFrame()

# Function to calculate Click-through Rate (CTR)
def calculate_ctr(clicks, impressions):
    """
    Calculate Click-through Rate (CTR).
    :param clicks: Total number of clicks
    :param impressions: Total number of impressions
    :return: CTR value
    """
    try:
        if impressions == 0:
            return 0.0
        return clicks / impressions
    except Exception as e:
        logger.error(f"Error calculating CTR: {e}")
        return 0.0

# Function to calculate Mean Average Precision (MAP)
def calculate_map(predicted_ranks, actual_relevance):
    """
    Calculate Mean Average Precision (MAP).
    :param predicted_ranks: List of predicted video ranks
    :param actual_relevance: List of actual relevant video indices
    :return: MAP value
    """
    try:
        if len(predicted_ranks) == 0 or len(actual_relevance) == 0:
            return 0.0
        
        precision_at_k = []
        relevant_count = 0
        
        for k, pred in enumerate(predicted_ranks, start=1):
            if pred in actual_relevance:
                relevant_count += 1
                precision_at_k.append(relevant_count / k)
        
        if not precision_at_k:
            return 0.0
        return np.mean(precision_at_k)
    except Exception as e:
        logger.error(f"Error calculating MAP: {e}")
        return 0.0

# API route to fetch recommendations
@app.route('/recommend', methods=['GET'])
def recommend():
    """
    Generate video recommendations for a user.
    Query params:
    - username: User's username
    - top_n: Number of recommendations to fetch (default 5)
    - category: Specific category for recommendations (optional)
    """
    username = request.args.get('username')
    top_n = int(request.args.get('top_n', 5))
    category = request.args.get('category')

    # Fetch all posts
    all_posts = fetch_paginated_data("/posts/summary/get")
    if not all_posts:
        return jsonify({"error": "No posts available for recommendations"}), 500

    # Create a DataFrame
    df_posts = pd.DataFrame(all_posts)
    logger.debug(f"Columns in df_posts: {df_posts.columns.tolist()}")

    # Check for required columns
    required_columns = ['upvote_count', 'view_count', 'category', 'username']
    missing_columns = [col for col in required_columns if col not in df_posts.columns]
    if missing_columns:
        logger.error(f"Missing columns in the data: {missing_columns}")
        return jsonify({"error": f"Missing columns in the data: {missing_columns}"}), 500

    # Filter posts by username
    user_posts = df_posts[df_posts['username'] == username]

    if user_posts.empty:
        # Recommend trending videos for new users
        trending_videos = get_trending_videos(df_posts, top_n)
        if trending_videos.empty:
            return jsonify({"error": "No trending videos available"}), 500

        # Optionally, recommend videos by category
        if category:
            category_recommendations = get_category_recommendations(df_posts, category, top_n)
            if not category_recommendations.empty:
                return jsonify({
                    "username": username,
                    "category_recommendations": category_recommendations.to_dict(orient="records")
                })

        return jsonify({
            "username": username,
            "trending_videos": trending_videos.to_dict(orient="records")
        })

    # Generate recommendations for existing users
    try:
        user_posts["popularity"] = user_posts["upvote_count"] + user_posts["view_count"]
        recommendations = user_posts.sort_values("popularity", ascending=False).head(top_n)
        return jsonify({
            "username": username,
            "recommendations": recommendations.to_dict(orient="records")
        })
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return jsonify({"error": "Failed to generate recommendations"}), 500

# API route for evaluation metrics
@app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    Evaluate the recommendations using CTR and MAP metrics.
    Request body:
    - clicks: Total clicks
    - impressions: Total impressions
    - predicted_ranks: List of predicted video ranks
    - actual_relevance: List of actual relevant video indices
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        clicks = data.get("clicks", 0)
        impressions = data.get("impressions", 0)
        predicted_ranks = data.get("predicted_ranks", [])
        actual_relevance = data.get("actual_relevance", [])

        # Calculate metrics
        ctr = calculate_ctr(clicks, impressions)
        map_score = calculate_map(predicted_ranks, actual_relevance)

        return jsonify({
            "click_through_rate": ctr,
            "mean_average_precision": map_score
        })
    except Exception as e:
        logger.error(f"Error in evaluation endpoint: {e}")
        return jsonify({"error": "Failed to calculate metrics"}), 500

# Main route
@app.route('/')
def index():
    """Main route to verify API is running."""
    return "Video Recommendation API is running! Use /recommend and /evaluate to interact."

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
