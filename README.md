![Movie Recommendation System Banner](screenshots/Logo.png)

# 🎬 Movie Recommendation System

A **Netflix / IMDb–style Movie Recommendation Web App** built with **Python & Streamlit**, powered by the **TMDB API** and a **content-based recommendation engine**.


🔗 **Live Demo:**  
https://movie-recommendation-system--gopiprajapati20.replit.app

[![Streamlit App](https://img.shields.io/badge/Live%20Demo-Streamlit-red)](https://movie-recommendation-system--gopiprajapati20.replit.app)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---
## 👤 What Users Can Do

- Discover trending movies
- Select a movie and get similar recommendations
- Browse movies by category and genre
- Navigate smoothly using page-based pagination

---

## 🚀 Features

- 🔥 **Trending Movies**
  - Weekly trending movies from TMDB
- 🎯 **Content-Based Recommendations**
  - Based on genres, overview, cast, and crew
- 🎬 **Movie Selection via Dropdown**
  - Clean UI (no search clutter)
- 🎞 **Browse by Category & Genre**
  - Hollywood, Bollywood, K-Drama  
  - Action, Comedy, Romance  
  - Horror, Thriller, Sci-Fi  
  - Drama, Animation
- 📄 **Production-Correct Pagination**
  - Fixed movies per page
  - Next / Previous navigation
  - No duplicates
- 🖼 **High-Quality Posters**
  - Fetched directly from TMDB
- ⚡ **Fast & Interactive UI**
  - Cached API calls & data processing
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
│   ├── recommender.py
│   ├── cache.py
│   ├── tmdb_api.py
│   └── ui_components.py
│
└── screenshots/
    ├── Trending_now.png
    ├── recommendation.png
    ├── browse_by_category1.png
    └── browse_by_category2.png
```
---

## 🏗️ System Architecture

```mermaid
C4Container
    title Movie Recommendation System – Architecture

    %% --- Users ---
    Person(user, "User", "Browses movies and gets recommendations")

    %% --- Frontend / UI ---
    Container(ui, "Streamlit UI (app.py)", "Streamlit", "Handles layout, user input, navigation, pagination")

    Container(components, "UI Components", "Python", "Reusable movie cards, buttons, trailers (ui_components.py)")

    %% --- Application Layer ---
    Container(logic, "Application Logic", "Python", "Coordinates recommendation flow, category browsing, session state")

    Container(cache, "Caching Layer", "Streamlit Cache", "Caches API calls and heavy computations (cache.py)")

    %% --- Recommendation Engine ---
    Container(engine, "Recommendation Engine", "Scikit-learn", "Content-based filtering using cosine similarity")

    %% --- Data & External Services ---
    ContainerDb(csv, "Local Movie Dataset", "CSV", "TMDB 5000 Movies & Credits dataset")

    System_Ext(tmdb, "TMDB API", "Provides posters, trending movies, trailers, metadata")

    %% --- Relationships ---
    Rel(user, ui, "Interacts with")
    Rel(ui, components, "Renders UI using")
    Rel(ui, logic, "Triggers actions")
    Rel(logic, cache, "Uses cached results")
    Rel(logic, engine, "Requests recommendations")
    Rel(engine, csv, "Loads & processes")
    Rel(logic, tmdb, "Fetches movies, posters, trailers")
    Rel(cache, tmdb, "Caches API responses")

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

---

## 📜 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this project with attribution.

See the [LICENSE](LICENSE) file for details.

