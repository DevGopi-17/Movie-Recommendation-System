![Movie Recommendation System Banner](screenshots/Logo.png)

# 🎬 Movie Recommendation System

A **Netflix / IMDb–style Movie Recommendation Web App** built with **Python & Streamlit**, powered by the **TMDB API** and a **content-based recommendation engine**.

Users can:
- Discover trending movies
- Select a movie from a dropdown and get similar recommendations
- Browse movies by category and genre
- Navigate smoothly using page-based pagination

---

## 🚀 Features

- 🔥 **Trending Movies**
  - Weekly trending movies from TMDB
- 🎯 **Content-Based Movie Recommendations**
  - Based on genres, overview, cast, and crew
- 🎬 **Movie Selection via Dropdown**
  - Clean UI (no search box clutter)
- 🎞 **Browse by Category & Genre**
  - Hollywood  
  - Bollywood  
  - K-Drama  
  - Action  
  - Comedy  
  - Romance  
  - Horror  
  - Thriller  
  - Sci-Fi  
  - Drama  
  - Animation  
- 📄 **Production-Correct Pagination**
  - Fixed number of movies per page
  - Next / Previous navigation
  - No duplicate results
- 🖼 **High-Quality Movie Posters**
  - Fetched directly from TMDB
- ⚡ **Fast & Interactive Streamlit UI**
  - Cached data & API calls for performance

---

## 🖼️ Screenshots

<details>
<summary>Home Page</summary>

Trending movies and main layout:

![Home Page](screenshots/Trending_now.png)

</details>

<details>
<summary>Find a Movie & Recommendations</summary>

Select a movie from the dropdown and get recommendations:

![Recommendations](screenshots/recommendation.png)

</details>

<details>
<summary>Browse by Category</summary>

Category browsing with pagination:

![Category Page 1](screenshots/browse_by_category1.png)

![Category Page 2](screenshots/browse_by_category2.png)

</details>

---

## 🧠 Recommendation Logic

This system uses **content-based filtering**:

- Movie overview
- Genres
- Cast
- Crew

All features are combined into a single representation, and  
**cosine similarity** is used to find movies most similar to the selected one.

---

## 🛠 Tech Stack

- **Python 3**
- **Streamlit**
- **Pandas**
- **Scikit-learn**
- **TMDB API**
- **Requests**

---

## 📂 Project Structure

```bash
Movie-Recommendation-System/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── tmdb_5000_movies.csv
│   └── tmdb_5000_credits.csv
│
├── src/
│   ├── preprocess.py
│   └── recommender.py
│
└── screenshots/
    ├── Trending_now.png
    ├── recommendation.png
    ├── browse_by_category1.png
    └── browse_by_category2.png
```
---


## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/movie-recommendation-system.git
cd movie-recommendation-system
```

### 2️⃣ Create virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set TMDB API Key

Create a TMDB API key from
👉 https://www.themoviedb.org/

Then set it as an environment variable:

macOS/Linux
```bash
export TMDB_API_KEY="your_api_key_here"
```

Windows
```bash
set TMDB_API_KEY=your_api_key_here
```

### ▶️ Run the App
```bash
streamlit run app.py
```
The app will open automatically in your browser 🚀

