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

#DARK UI CSS
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #1f2937, #020617);
    color: #e5e7eb;
    font-family: Inter, sans-serif;
}

.block-container {
    padding-top: 2rem;
}

.app-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 30px;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    margin: 30px 0 18px;
}

.movie-card {
    background: #111827;
    border-radius: 14px;
    padding: 8px;
    box-shadow: 0 10px 35px rgba(0,0,0,.45);
    transition: transform .25s ease;
}

.movie-card:hover {
    transform: scale(1.06);
}

.movie-card img {
    border-radius: 10px;
}

.page-indicator {
    text-align: center;
    font-size: 18px;
    font-weight: 600;
    color: #ef4444;
    margin: 10px 0 20px;
}

.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    font-size: 16px;
    font-weight: 600;
    border-radius: 12px;
    padding: 10px 22px;
    border: none;
}

.stButton > button:hover {
    filter: brightness(1.1);
}

input, .stSelectbox {
    background: #020617 !important;
    color: #e5e7eb !important;
    border-radius: 10px !important;
}

.skeleton {
    height: 260px;
    border-radius: 14px;
    background: linear-gradient(
        90deg,
        #1f2937 25%,
        #374151 37%,
        #1f2937 63%
    );
    background-size: 400% 100%;
    animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
    0% { background-position: 100% 0 }
    100% { background-position: -100% 0 }
}
</style>
""", unsafe_allow_html=True)


# SESSION STATE
if "category_page" not in st.session_state:
    st.session_state.category_page = 1

if "last_category" not in st.session_state:
    st.session_state.last_category = None

# TMDB API KEY
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    st.error("TMDB API key not found. Set TMDB_API_KEY environment variable.")
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
@st.cache_resource(show_spinner="Building recommendation model...")
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

# SEARCH & RECOMMENDATION
st.markdown("## 🔍 Find a Movie")

st.markdown("<div class='find-container'>", unsafe_allow_html=True)

st.markdown("<div class='find-title'></div>", unsafe_allow_html=True)

# DEFAULT MOVIE SHOWN LIKE: Avatar ▼
selected_movie = st.selectbox(
    "",
    movie_list,
    index=list(movie_list).index("Avatar") if "Avatar" in movie_list else 0,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    recommend = st.button("🎯 Recommend", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

if recommend:
    with st.spinner("Finding similar movies..."):
        recommendations = recommender.recommend(
            selected_movie,
            TMDB_API_KEY
        )

    st.markdown("## 🍿 Recommended Movies")
    cols = st.columns(5)
    for i, movie in enumerate(recommendations):
        with cols[i % 5]:
            if movie["poster"]:
                st.image(movie["poster"], use_container_width=True)
            st.caption(movie["title"])



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
