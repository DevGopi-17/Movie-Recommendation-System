import streamlit as st
import pandas as pd
import os
import requests
from src.preprocess import preprocess_data
from src.recommender import MovieRecommender


# CONFIG
MOVIES_PER_PAGE = 15

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# SESSION STATE
if "category_page" not in st.session_state:
    st.session_state.category_page = 1

if "last_category" not in st.session_state:
    st.session_state.last_category = None

# TMDB API KEY
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    st.error("❌ TMDB API key not found. Set TMDB_API_KEY environment variable.")
    st.stop()

# HEADER
st.markdown(
    "<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>",
    unsafe_allow_html=True
)


# LOAD + PREPROCESS DATA (CACHED)
@st.cache_data(show_spinner="📦 Loading movie dataset...")
def load_and_process_movies():
    movies = pd.read_csv("data/tmdb_5000_movies.csv")
    credits = pd.read_csv("data/tmdb_5000_credits.csv")
    merged = movies.merge(credits, on="title")
    return preprocess_data(merged)

processed_movies = load_and_process_movies()
movie_list = processed_movies["title"].values


# LOAD RECOMMENDER (CACHED)
@st.cache_resource(show_spinner="🧠 Building recommendation model...")
def load_recommender(df):
    return MovieRecommender(df)

recommender = load_recommender(processed_movies)

# TMDB HELPERS (CACHED)
@st.cache_data(ttl=3600)
def get_trending_movies(api_key, count=5):
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}"
    data = requests.get(url, timeout=10).json()

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

@st.cache_data(ttl=3600)
def fetch_category_movies(api_key, category, page):
    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": api_key,
        "sort_by": "popularity.desc",
        "page": page
    }

    category_map = {
        "Hollywood": {"with_original_language": "en"},
        "K-Drama": {"with_original_language": "ko"},
        "Bollywood": {"with_original_language": "hi"},
        "Action": {"with_genres": "28"},
        "Comedy": {"with_genres": "35"},
        "Romance": {"with_genres": "10749"}
    }

    params.update(category_map.get(category, {}))
    data = requests.get(url, params=params, timeout=10).json()

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

# TRENDING MOVIES
st.markdown("## 🔥 Trending Now")
cols = st.columns(5)

for idx, movie in enumerate(get_trending_movies(TMDB_API_KEY)):
    with cols[idx]:
        if movie["poster"]:
            st.image(movie["poster"], use_container_width=True)
        st.caption(movie["title"])

# SEARCH & RECOMMEND
st.markdown("## 🔍 Find a Movie")

search_text = st.text_input("", placeholder="Search movie (Inception, Avatar...)")

filtered_movies = (
    [m for m in movie_list if search_text.lower() in m.lower()]
    if search_text else movie_list
)

selected_movie = st.selectbox("Select movie", filtered_movies)

if st.button("🎯 Recommend"):
    with st.spinner("Finding similar movies..."):
        recommendations = recommender.recommend(selected_movie, TMDB_API_KEY)

    st.markdown("## 🍿 Recommended Movies")
    cols = st.columns(5)

    for idx, movie in enumerate(recommendations):
        with cols[idx % 5]:
            if movie["poster"]:
                st.image(movie["poster"], use_container_width=True)
            st.caption(movie["title"])


# CATEGORY BROWSING
st.markdown("## 🎞 Browse by Category")

category = st.selectbox(
    "Choose category",
    ["Hollywood", "K-Drama", "Bollywood", "Action", "Comedy", "Romance"]
)

# Reset page when category changes
if category != st.session_state.last_category:
    st.session_state.category_page = 1
    st.session_state.last_category = category

movies = fetch_category_movies(
    TMDB_API_KEY,
    category,
    st.session_state.category_page
)

st.markdown(
    f"""
    <div style="text-align:center;font-size:18px;font-weight:600;color:#E50914;">
        {category} • Page {st.session_state.category_page}
    </div>
    """,
    unsafe_allow_html=True
)

# Display movies
cols = st.columns(5)
for idx, movie in enumerate(movies):
    with cols[idx % 5]:
        if movie["poster"]:
            st.image(movie["poster"], use_container_width=True)
        st.caption(movie["title"])

# PAGINATION
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
