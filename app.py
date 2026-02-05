import streamlit as st
import pandas as pd
import os
import requests
from src.preprocess import preprocess_data
from src.recommender import MovieRecommender

# -----------------------------
# Config
# -----------------------------
MOVIES_PER_PAGE = 15

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------
if "category_page" not in st.session_state:
    st.session_state.category_page = 1

if "last_category" not in st.session_state:
    st.session_state.last_category = None

# -----------------------------
# TMDB API Key
# -----------------------------
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    st.error("TMDB API key not found. Set TMDB_API_KEY environment variable.")
    st.stop()

# -----------------------------
# Header
# -----------------------------
st.markdown(
    "<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

# -----------------------------
# Load Data
# -----------------------------
def load_movies(movies_path, credits_path):
    movies = pd.read_csv(movies_path)
    credits = pd.read_csv(credits_path)
    return movies.merge(credits, on="title")

processed_movies = preprocess_data(
    load_movies("data/tmdb_5000_movies.csv", "data/tmdb_5000_credits.csv")
)

recommender = MovieRecommender(processed_movies)
movie_list = processed_movies["title"].values

# -----------------------------
# Trending Movies
# -----------------------------
def get_trending_movies(api_key, count=5):
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}"
    data = requests.get(url).json()

    return [
        {
            "title": m["title"],
            "poster": (
                "https://image.tmdb.org/t/p/w500" + m["poster_path"]
                if m.get("poster_path") else None
            )
        }
        for m in data.get("results", [])[:count]
    ]

st.markdown("## 🔥 Trending Now")
cols = st.columns(5)

for idx, movie in enumerate(get_trending_movies(TMDB_API_KEY)):
    with cols[idx]:
        if movie["poster"]:
            st.image(movie["poster"], use_container_width=True)
        st.caption(movie["title"])

# -----------------------------
# Search & Recommendation
# -----------------------------
st.markdown("## 🔍 Find a Movie")
search_text = st.text_input("", placeholder="Search movie (Inception, Avatar...)")

filtered_movies = (
    [m for m in movie_list if search_text.lower() in m.lower()]
    if search_text else movie_list
)

selected_movie = st.selectbox("Select movie", filtered_movies)

if st.button("🎯 Recommend"):
    recommendations = recommender.recommend(selected_movie, TMDB_API_KEY)

    st.markdown("## 🍿 Recommended Movies")
    cols = st.columns(5)

    for idx, movie in enumerate(recommendations):
        with cols[idx % 5]:
            if movie["poster"]:
                st.image(movie["poster"], use_container_width=True)
            st.caption(movie["title"])

# -----------------------------
# Fetch Category Movies
# -----------------------------
def fetch_category_movies(api_key, category, page):
    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": api_key,
        "sort_by": "popularity.desc",
        "page": page
    }

    if category == "Hollywood":
        params["with_original_language"] = "en"
    elif category == "K-Drama":
        params["with_original_language"] = "ko"
    elif category == "Bollywood":
        params["with_original_language"] = "hi"
    elif category == "Action":
        params["with_genres"] = "28"
    elif category == "Comedy":
        params["with_genres"] = "35"
    elif category == "Romance":
        params["with_genres"] = "10749"

    data = requests.get(url, params=params).json()

    return [
        {
            "title": m["title"],
            "poster": (
                "https://image.tmdb.org/t/p/w500" + m["poster_path"]
                if m.get("poster_path") else None
            )
        }
        for m in data.get("results", [])[:MOVIES_PER_PAGE]
    ]

# -----------------------------
# Category Pagination
# -----------------------------
st.markdown("## 🎞 Browse by Category")

category = st.selectbox(
    "Choose category",
    ["Hollywood", "K-Drama", "Bollywood", "Action", "Comedy", "Romance"]
)

# Reset page on category change
if category != st.session_state.last_category:
    st.session_state.category_page = 1
    st.session_state.last_category = category

movies = fetch_category_movies(
    TMDB_API_KEY,
    category,
    st.session_state.category_page
)

# Page Indicator
st.markdown(
    f"""
    <div style="text-align:center;font-size:18px;font-weight:600;color:#E50914;">
        {category} • Page {st.session_state.category_page}
    </div>
    """,
    unsafe_allow_html=True
)

# Display Movies
cols = st.columns(5)
for idx, movie in enumerate(movies):
    with cols[idx % 5]:
        if movie["poster"]:
            st.image(movie["poster"], use_container_width=True)
        st.caption(movie["title"])

# -----------------------------
# Pagination Buttons
# -----------------------------
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅ Previous", disabled=st.session_state.category_page == 1):
        st.session_state.category_page -= 1
        st.rerun()

with col3:
    if st.button("Next ➡"):
        st.session_state.category_page += 1
        st.rerun()
