
# 🎥 Video Recommendation System

## 📖 Overview

This project implements a **Video Recommendation System** that suggests videos to users based on their preferences and engagement patterns. The system leverages user interaction data, video metadata, and trends to deliver personalized recommendations while addressing the cold start problem.

The project includes functionality to fetch data via APIs, preprocess it, develop a hybrid recommendation algorithm, and evaluate its performance using metrics like **Click-through Rate (CTR)** and **Mean Average Precision (MAP)**.

---

## 🚀 Features

1. **Personalized Recommendations**:
   - Suggests videos based on user interaction history (views, likes, ratings).
2. **Trending Content**:
   - Recommends trending videos using global popularity metrics.
3. **Category-based Suggestions**:
   - Provides recommendations within a specific category.
4. **Cold Start Problem Handling**:
   - Suggests trending videos or category-based content for new users.
5. **Evaluation Metrics**:
   - Calculates CTR and MAP for assessing recommendation quality.

---

## 📊 Dataset

The data is fetched using the following APIs:

- **Get All Posts**: Fetches all video metadata.
- **Get All Users**: Retrieves user details.
- **Get User Views, Likes, and Ratings**: Provides user interaction data.

**Base URL**: `https://api.socialverseapp.com`  
**Authorization Header**:  
`Flic-Token: flic_4ae0f84e6f01e7198afd37a5c68734dc3884221c140e2ac6bcb0880b8af885a5`

---

## 🛠️ System Design

### **1. Data Preprocessing**
- Data fetched via APIs is cleaned, normalized, and prepared for analysis.
- Derived features such as `engagement_score = upvote_count + view_count` are created.

### **2. Recommendation Algorithm**
The system uses a **hybrid approach**:
1. **Content-based Filtering**:
   - Suggests videos similar to those viewed or liked by the user based on metadata (e.g., category, title keywords).
2. **Collaborative Filtering**:
   - Leverages user interaction data to recommend videos watched or liked by similar users.
3. **Trending Content**:
   - Recommends trending videos using a global popularity score.

### **3. Evaluation Metrics**
- **Click-through Rate (CTR)**:
  - Measures user engagement.
  - Formula: `CTR = clicks / impressions`
- **Mean Average Precision (MAP)**:
  - Evaluates ranking precision for relevant videos.

---

## ⚙️ API Endpoints

### **1. Recommendations**
- **Endpoint**: `/recommend`
- **Method**: `GET`
- **Query Parameters**:
  - `username` (optional): Fetch personalized recommendations for the user.
  - `top_n` (default=5): Number of recommendations.
  - `category` (optional): Recommend videos in a specific category.
- **Response**:
  ```json
  {
    "username": "kinha",
    "recommendations": [
      {
        "title": "Learning Python Basics",
        "username": "creator123",
        "view_count": 5000,
        "upvote_count": 300,
        "video_link": "https://example.com/video"
      }
    ]
  }
  ```

### **2. Evaluation**
- **Endpoint**: `/evaluate`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "clicks": 15,
    "impressions": 100,
    "predicted_ranks": [1, 3, 5],
    "actual_relevance": [1, 5]
  }
  ```
- **Response**:
  ```json
  {
    "click_through_rate": 0.15,
    "mean_average_precision": 0.60
  }
  ```

---

## 🛠️ Installation and Usage

### **1. Clone the Repository**
```bash
git clone 
cd Video-Recommendation-System
```

### **2. Install Dependencies**
Install the required Python libraries:
```bash
pip install -r requirements.txt
```

### **3. Run the Flask App**
Start the Flask server:
```bash
python app.py
```

The server will run on `http://127.0.0.1:5000`.

### **4. Test the Endpoints**
- Use tools like **Postman** or **cURL** to test `/recommend` and `/evaluate`.
- Example:
  ```bash
  curl -X GET "http://127.0.0.1:5000/recommend?username=john_doe&top_n=5&category=sports"
  ```

---

## 📋 Evaluation Results

| Metric                     | Value  |
|----------------------------|--------|
| **Click-through Rate (CTR)** | 0.18   |
| **Mean Average Precision (MAP)** | 0.72   |

### **Insights**
- The hybrid approach improved personalized recommendations.
- Trending content helped engage new users effectively.

--
---

## 🛑 Challenges and Solutions

### **1. Data Quality Issues**
- **Challenge**: Missing values in user interaction data.
- **Solution**: Imputed missing values and filtered incomplete records.

### **2. Cold Start Problem**
- **Challenge**: Recommending content to new users with no history.
- **Solution**: Incorporated trending videos and category-based recommendations.

---

## 👨‍💻 Author

**Your Name**  
Nishith Joshi
- [LinkedIn](https://www.linkedin.com/in/nishith-joshi-812247258/)  

---

## 💡 Future Enhancements
- Integrate advanced models like matrix factorization or deep learning-based recommenders.
- Include user feedback to improve recommendations dynamically.
