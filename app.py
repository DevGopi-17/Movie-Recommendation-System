import streamlit as st
import pandas as pd
import os
import requests
import tmdbsimple as tmdb
from src.preprocess import preprocess_data
from src.recommender import MovieRecommender


# TMDB CONFIG
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
tmdb.API_KEY = TMDB_API_KEY

if not TMDB_API_KEY:
    st.error("TMDB API key not found. Set TMDB_API_KEY environment variable.")
    st.stop()


# APP CONFIG
MOVIES_PER_PAGE = 15

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# DARK UI CSS
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #1f2937, #020617);
    color: #e5e7eb;
    font-family: Inter, sans-serif;
}
.block-container { padding-top: 2rem; }
.movie-card img { border-radius: 10px; }
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    font-size: 15px;
    font-weight: 600;
    border-radius: 12px;
    padding: 8px 18px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "category_page" not in st.session_state:
    st.session_state.category_page = 1
if "last_category" not in st.session_state:
    st.session_state.last_category = None

# HEADER
st.markdown(
    "<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

# LOAD + PREPROCESS DATA
@st.cache_data(show_spinner="📦 Loading movie dataset...")
def load_and_process_movies():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    movies_file = os.path.join(BASE_DIR, "Data", "tmdb_5000_movies.csv")
    credits_file = os.path.join(BASE_DIR, "Data", "tmdb_5000_credits.csv")

    movies = pd.read_csv(movies_file)
    credits = pd.read_csv(credits_file)

    merged = movies.merge(credits, on="title")
    return preprocess_data(merged)

processed_movies = load_and_process_movies()
movie_list = processed_movies["title"].values


# LOAD RECOMMENDER
@st.cache_resource(show_spinner="Building recommendation model...")
def load_recommender(df):
    return MovieRecommender(df)

recommender = load_recommender(processed_movies)

# TMDB HELPERS
@st.cache_data(ttl=3600)
def get_trailer(movie_id, api_key):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    data = requests.get(url, params={"api_key": api_key}, timeout=10).json()
    for v in data.get("results", []):
        if v["site"] == "YouTube" and v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None


@st.cache_data(ttl=3600)
def get_trending_movies(api_key, count=5):
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}"
    data = requests.get(url, timeout=10).json()
    return [
        {
            "id": m["id"],
            "title": m["title"],
            "poster": "https://image.tmdb.org/t/p/w500" + m["poster_path"]
            if m.get("poster_path") else None
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
        "Bollywood": {"with_original_language": "hi"},
        "K-Drama": {"with_original_language": "ko"},
        "Action": {"with_genres": "28"},
        "Comedy": {"with_genres": "35"},
        "Romance": {"with_genres": "10749"},
        "Horror": {"with_genres": "27"},
        "Thriller": {"with_genres": "53"},
        "Sci-Fi": {"with_genres": "878"},
        "Animation": {"with_genres": "16"},
        "Drama": {"with_genres": "18"},
        "Crime": {"with_genres": "80"},
        "Fantasy": {"with_genres": "14"},
        "Adventure": {"with_genres": "12"},
        "Family": {"with_genres": "10751"},
        "Mystery": {"with_genres": "9648"},
        "War": {"with_genres": "10752"},
        "Music": {"with_genres": "10402"},
        "Western": {"with_genres": "37"},
    }

    params.update(category_map.get(category, {}))
    data = requests.get(url, params=params, timeout=10).json()

    return [
        {
            "id": m["id"],
            "title": m["title"],
            "poster": "https://image.tmdb.org/t/p/w500" + m["poster_path"]
            if m.get("poster_path") else None
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

        with st.expander("▶️ Watch Trailer"):
            trailer = get_trailer(movie["id"], TMDB_API_KEY)
            if trailer:
                st.video(trailer)
            else:
                st.caption("Trailer not available")

# SEARCH & RECOMMEND
st.markdown("## 🔍 Find a Movie")

selected_movie = st.selectbox(
    "",
    movie_list,
    index=list(movie_list).index("Avatar") if "Avatar" in movie_list else 0,
    label_visibility="collapsed"
)

if st.button("🎯 Recommend", use_container_width=True):
    with st.spinner("Finding similar movies..."):
        recommendations = recommender.recommend(selected_movie, TMDB_API_KEY)

    st.markdown("## 🍿 Recommended Movies")
    cols = st.columns(5)

    for i, movie in enumerate(recommendations):
        with cols[i % 5]:
            if movie["poster"]:
                st.image(movie["poster"], use_container_width=True)
            st.caption(movie["title"])

            with st.expander("▶️ Watch Trailer"):
                trailer = get_trailer(movie["id"], TMDB_API_KEY)
                if trailer:
                    st.video(trailer)
                else:
                    st.caption("Trailer not available")

# CATEGORY BROWSING
st.markdown("## 🎞 Browse by Category")

category = st.selectbox(
    "",
    ["Hollywood", "Bollywood", "K-Drama", "Action", "Comedy", "Romance", "Horror",
     "Thriller", "Sci-Fi", "Animation", "Drama", "Crime", "Fantasy", "Adventure",
     "Family", "Mystery", "War", "Music", "Western"],
    index=None,
    placeholder="Choose category"
)

if category != st.session_state.last_category:
    st.session_state.category_page = 1
    st.session_state.last_category = category

movies = fetch_category_movies(
    TMDB_API_KEY,
    category,
    st.session_state.category_page
)

cols = st.columns(5)
for idx, movie in enumerate(movies):
    with cols[idx % 5]:
        if movie["poster"]:
            st.image(movie["poster"], use_container_width=True)
        st.caption(movie["title"])

        with st.expander("▶️ Watch Trailer"):
            trailer = get_trailer(movie["id"], TMDB_API_KEY)
            if trailer:
                st.video(trailer)
            else:
                st.caption("Trailer not available")

# PAGINATION
col1, _, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅ Previous", disabled=st.session_state.category_page == 1):
        st.session_state.category_page -= 1
        st.rerun()

with col3:
    if st.button("Next ➡"):
        st.session_state.category_page += 1
        st.rerun()
