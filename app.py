import streamlit as st
import pandas as pd
import os
import requests
import tmdbsimple as tmdb
import concurrent.futures
import streamlit.components.v1 as components

from src.ui_components import render_movie_card
from src.preprocess import preprocess_data
from src.recommender import MovieRecommender
from src.cache import cached_call
from src.tmdb_api import (
    get_trailer,
    get_movie_id_by_title,
    get_trending_movies,
    fetch_category_movies,
    get_movie_details
)

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

#CSS STYLES
st.markdown("""
<style>

/*GLOBAL THEME */
.stApp {
    background: radial-gradient(circle at top, #1f2937, #020617);
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

/* MOVIE CARD CONTAINER */
.movie-card-container {
    position: relative;
    perspective: 1200px;
    display: inline-block;
    margin: 12px;
    transition: filter 0.35s ease;
}

/* Blur siblings */
.movie-card-container:hover ~ .movie-card-container {
    filter: blur(2px) brightness(0.75);
}

/* MOVIE CARD */
.movie-card {
    transform-style: preserve-3d;
    border-radius: 22px;
    overflow: hidden;
    background: linear-gradient(145deg, #1f2937, #020617);
    box-shadow:
        0 10px 20px rgba(0,0,0,0.35),
        0 0 12px rgba(37, 99, 235, 0.25);
    transition:
        transform 0.55s cubic-bezier(.03,.98,.52,.99),
        box-shadow 0.55s ease;
    will-change: transform;
    animation: fadeInUp 0.6s ease forwards;
}

/* Hover tilt (CSS-only fallback) */
.movie-card-container:hover .movie-card {
    transform: rotateX(4deg) rotateY(6deg) scale(1.08);
    box-shadow:
        0 28px 50px rgba(0,0,0,0.65),
        0 0 35px rgba(37, 99, 235, 0.6),
        inset 0 0 12px rgba(255,255,255,0.03);
}

/*POSTER */
.movie-card img {
    width: 100%;
    display: block;
    border-radius: 18px;
    transition: transform 0.45s ease, filter 0.45s ease;
}

.movie-card-container:hover img {
    transform: scale(1.06);
    filter: brightness(1.12) contrast(1.05);
}

/* GLOW AURA */
.movie-card-container::before {
    content: '';
    position: absolute;
    inset: -12%;
    background: radial-gradient(
        circle,
        rgba(255,255,255,0.06),
        transparent 70%
    );
    border-radius: 24px;
    opacity: 0;
    transition: opacity 0.45s ease;
    pointer-events: none;
}

.movie-card-container:hover::before {
    opacity: 1;
}

/* TITLE */
.caption {
    text-align: center;
    margin-top: 6px;
    font-size: 14px;
    font-weight: 600;
    color: #f3f4f6;
    text-shadow: 0 1px 2px rgba(0,0,0,0.7);
}

/* BUTTONS  */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: white;
    font-weight: 600;
    border-radius: 14px;
    padding: 10px 22px;
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.45);
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.06);
    box-shadow: 0 14px 30px rgba(37, 99, 235, 0.7);
}

/*EXPANDER */
.stExpander {
    background-color: #111827;
    border-radius: 16px;
    padding: 14px;
    transition: all 0.3s ease;
}

.stExpander:hover {
    background-color: #1f2937;
    transform: translateY(-2px);
    box-shadow: 0 12px 26px rgba(37, 99, 235, 0.45);
}

/*VIDEO*/
.stVideo iframe {
    width: 100% !important;
    border-radius: 16px;
    box-shadow: 0 14px 34px rgba(0,0,0,0.65);
}

/* ANIMATIONS */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(22px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
            

</style>
""", unsafe_allow_html=True)

#TMDB CONFIG 
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
tmdb.API_KEY = TMDB_API_KEY


if not TMDB_API_KEY:
    st.error("TMDB API key not found. Set TMDB_API_KEY environment variable.")
    st.stop()

    
MOVIES_PER_PAGE = 15

#APP CONFIG 
st.set_page_config(page_title="Movie Recommendation System", layout="wide")


#SESSION STATE 
if "category_page" not in st.session_state:
    st.session_state.category_page = 1
if "last_category" not in st.session_state:
    st.session_state.last_category = None

# Add recommendation and sidebar state
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "sidebar_movie_id" not in st.session_state:
    st.session_state.sidebar_movie_id = None

#HEADER
st.markdown("<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>", unsafe_allow_html=True)

#LOAD + PREPROCESS DATA 
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

#LOAD RECOMMENDER 
@st.cache_resource(show_spinner="Building recommendation model...")
def load_recommender(df):
    return MovieRecommender(df)

recommender = load_recommender(processed_movies)

#TRENDING MOVIES
st.markdown("## 🔥 Trending Now")
trending_movies = get_trending_movies(TMDB_API_KEY)
num_cols = 5

def fetch_trailer(movie):
    movie_id = movie.get("id") or get_movie_id_by_title(movie.get("title",""), TMDB_API_KEY)
    return get_trailer(movie_id, TMDB_API_KEY) if movie_id else None

with concurrent.futures.ThreadPoolExecutor() as executor:
    trending_trailers = list(executor.map(fetch_trailer, trending_movies))

for row_i in range(0, len(trending_movies), num_cols):
    cols = st.columns(num_cols)
    for col_j, (col, movie, trailer) in enumerate(
        zip(cols, trending_movies[row_i:row_i+num_cols], trending_trailers[row_i:row_i+num_cols])
    ):
        with col:
            render_movie_card(movie, trailer, section="trending", row_idx=row_i, col_idx=col_j)

#SEARCH & RECOMMENDATIONS
st.markdown("## 🔍 Find a Movie")

selected_movie = st.selectbox(
    "",
    movie_list,
    index=list(movie_list).index("Avatar") if "Avatar" in movie_list else 0,
    label_visibility="collapsed"
)

if st.button("🎯 Recommend", use_container_width=True):
    with st.spinner("Finding similar movies..."):
        st.session_state.recommendations = recommender.recommend(selected_movie, TMDB_API_KEY)

# Display recommendations from session_state
if st.session_state.recommendations:
    st.markdown("## 🍿 Recommended Movies")
    num_cols = 5

    def fetch_trailer_recommend(movie):
        movie_id = movie.get("id") or get_movie_id_by_title(movie.get("title",""), TMDB_API_KEY)
        return get_trailer(movie_id, TMDB_API_KEY) if movie_id else None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        trailers = list(executor.map(fetch_trailer_recommend, st.session_state.recommendations))

    for row_i in range(0, len(st.session_state.recommendations), num_cols):
        cols = st.columns(num_cols)
        for col_j, (col, movie, trailer) in enumerate(
            zip(cols, st.session_state.recommendations[row_i:row_i+num_cols], trailers[row_i:row_i+num_cols])
        ):
            with col:
                render_movie_card(movie, trailer, section="recommend", row_idx=row_i, col_idx=col_j)

# CATEGORY SECTION 
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

raw_movies = cached_call(
    fetch_category_movies,
    TMDB_API_KEY,
    category,
    st.session_state.category_page
)

movies = [m for m in raw_movies if m.get("id") and m.get("title")]

num_cols = 5

def fetch_trailer_category(movie):
    movie_id = movie.get("id")
    return get_trailer(movie_id, TMDB_API_KEY) if movie_id else None

with concurrent.futures.ThreadPoolExecutor() as executor:
    trailers = list(executor.map(fetch_trailer_category, movies))

for row_i in range(0, len(movies), num_cols):
    cols = st.columns(num_cols)
    for col_j, (col, movie, trailer) in enumerate(
        zip(cols, movies[row_i:row_i+num_cols], trailers[row_i:row_i+num_cols])
    ):
        with col:
            render_movie_card(movie, trailer, section="category", row_idx=row_i, col_idx=col_j)

#CATEGORY PAGINATION 
col1, _, col3 = st.columns([1,2,1])
with col1:
    if st.button("⬅ Previous", disabled=st.session_state.category_page == 1):
        st.session_state.category_page -= 1
        st.rerun()

with col3:
    if st.button("Next ➡"):
        st.session_state.category_page += 1
        st.rerun()

# MOUSE-RESPONSIVE 3D TILT 
components.html("""
<script>
document.querySelectorAll('.movie-card-container').forEach(container => {
    const card = container.querySelector('.movie-card');
    container.addEventListener('mousemove', e => {
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const cx = rect.width/2;
        const cy = rect.height/2;
        const dx = (x - cx) / cx;
        const dy = (y - cy) / cy;
        const rotateX = dy * 8;
        const rotateY = dx * 8;
        card.style.transform = `rotateX(${ -rotateX }deg) rotateY(${ rotateY }deg) scale(1.08)`;
    });
    container.addEventListener('mouseleave', e => {
        card.style.transform = 'rotateX(0deg) rotateY(0deg) scale(1.0)';
    });
});
</script>
""", height=0)

#SIDEBAR DETAILS 
if "sidebar_movie" in st.session_state and st.session_state.sidebar_movie:
    movie = st.session_state.sidebar_movie
    details = get_movie_details(movie.get("id"), TMDB_API_KEY)
    if details:
        st.sidebar.markdown(f"## 🎬 {details.get('title')}")
        if details.get("poster_path"):
            st.sidebar.image(f"https://image.tmdb.org/t/p/w500{details.get('poster_path')}", width=300)
        st.sidebar.markdown(f"**Release Date:** {details.get('release_date', 'N/A')}")
        st.sidebar.markdown(f"**Rating:** {details.get('vote_average', 'N/A')} / 10")
        genres = ', '.join([g['name'] for g in details.get('genres', [])])
        st.sidebar.markdown(f"**Genres:** {genres if genres else 'N/A'}")
        st.sidebar.markdown(f"**Overview:** {details.get('overview', 'No overview available.')}")
        trailer_url = get_trailer(movie.get('id'), TMDB_API_KEY)
        if trailer_url:
            st.sidebar.video(trailer_url, start_time=0)
