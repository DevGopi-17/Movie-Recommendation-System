import streamlit as st
import pandas as pd
import os
import requests
import tmdbsimple as tmdb
import concurrent.futures
import streamlit.components.v1 as components
from src.preprocess import preprocess_data
from src.recommender import MovieRecommender

#TMDB CONFIG 
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
tmdb.API_KEY = TMDB_API_KEY


if not TMDB_API_KEY:
    st.error("TMDB API key not found. Set TMDB_API_KEY environment variable.")
    st.stop()

    
MOVIES_PER_PAGE = 15

#APP CONFIG 
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

#CSS 
st.markdown("""
<style>
/* ===== 3D Tilt / Parallax Next-Level ===== */
.movie-card-container {
    position: relative;
    perspective: 1200px;
    transition: filter 0.3s ease;
    display: inline-block;
    margin: 10px;
}
.movie-card-container:hover ~ .movie-card-container {
    filter: blur(2px) brightness(0.8);
}
.movie-card-container .movie-card {
    transform-style: preserve-3d;
    transition: transform 0.5s cubic-bezier(.03,.98,.52,.99),
                box-shadow 0.5s ease,
                filter 0.5s ease;
    will-change: transform, box-shadow;
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    background: linear-gradient(145deg, #1f2937, #111827);
    box-shadow: 0 10px 20px rgba(0,0,0,0.3), 0 0 10px rgba(37, 99, 235, 0.2);
}
.movie-card-container:hover .movie-card {
    transform: rotateX(4deg) rotateY(6deg) scale(1.08) translateZ(10px);
    box-shadow: 0 25px 45px rgba(0,0,0,0.6),
                0 0 30px rgba(37, 99, 235, 0.6),
                inset 0 0 10px rgba(255,255,255,0.03);
}
.movie-card img {
    border-radius: 15px;
    width: 100%;
    height: auto;
    display: block;
    transition: transform 0.5s ease, filter 0.5s ease;
}
.movie-card-container:hover img {
    transform: scale(1.05);
    filter: brightness(1.1) contrast(1.05);
}
.movie-card-container::before {
    content: '';
    position: absolute;
    top: -10%; left: -10%;
    width: 120%; height: 120%;
    background: radial-gradient(circle at center, rgba(255,255,255,0.05), transparent 70%);
    border-radius: 20px;
    pointer-events: none;
    mix-blend-mode: lighten;
    opacity: 0;
    transition: all 0.5s ease;
}
.movie-card-container:hover::before { opacity: 1; }
.stApp {
    background: radial-gradient(circle at top, #1f2937, #020617);
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}
.movie-card:hover {
    transform: scale(1.07) translateY(-5px) rotateZ(0.5deg);
    box-shadow: 0 20px 40px rgba(0,0,0,0.6),
                0 0 25px rgba(37, 99, 235, 0.5);
}
.movie-card .overlay {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: linear-gradient(to top, rgba(0,0,0,0.7), rgba(0,0,0,0));
    opacity: 0;
    border-radius: 20px;
    transition: opacity 0.3s ease;
}
.movie-card:hover .overlay { opacity: 1; }
.movie-card .hover-title {
    position: absolute;
    bottom: 10px;
    left: 0; right: 0;
    text-align: center;
    font-size: 16px;
    font-weight: 700;
    color: #2563eb;
    opacity: 0;
    text-shadow: 0px 2px 5px rgba(0,0,0,0.7);
    transition: opacity 0.3s ease, transform 0.3s ease;
}
.movie-card:hover .hover-title {
    opacity: 1;
    transform: translateY(-5px);
}
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: white;
    font-size: 16px;
    font-weight: 600;
    border-radius: 14px;
    padding: 10px 22px;
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.6);
}
.stExpander {
    background-color: #111827;
    border-radius: 15px;
    padding: 12px;
    transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
}
.stExpander:hover {
    background-color: #1f2937;
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
}
.stVideo iframe {
    width: 100% !important;
    max-width: 100%;
    border-radius: 15px;
    display: block;
    margin: auto;
    height: auto !important;
    box-shadow: 0 12px 30px rgba(0,0,0,0.6);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.stVideo iframe:hover {
    transform: scale(1.03);
    box-shadow: 0 18px 40px rgba(37, 99, 235, 0.8);
}
.caption {
    text-align: center;
    margin-top: 5px;
    font-weight: 600;
    font-size: 14px;
    color: #f3f4f6;
    text-shadow: 0px 1px 2px rgba(0,0,0,0.7);
}
@keyframes fadeInUp {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}
.movie-card { animation: fadeInUp 0.6s ease forwards; }
.trending-title {
    text-align: center;
    font-weight: 700;
    font-size: 16px;
    color: #2563eb;
    text-shadow: 0px 2px 5px rgba(0,0,0,0.7);
    margin-top: 5px;
}
</style>

<script>
document.addEventListener('mousemove', e => {
    document.querySelectorAll('.movie-card-container').forEach(card => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width/2;
        const y = e.clientY - rect.top - rect.height/2;
        const rotateX = (-y / (rect.height/2)) * 8; 
        const rotateY = (x / (rect.width/2)) * 8;
        card.querySelector('.movie-card').style.transform =
            `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
    });
});
</script>
""", unsafe_allow_html=True)

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

#TMDB HELPERS 
@st.cache_data(ttl=3600)
def get_trailer(movie_id, api_key):
    if not movie_id: return None
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    data = requests.get(url, params={"api_key": api_key}, timeout=10).json()
    for v in data.get("results", []):
        if v.get("site")=="YouTube" and v.get("type")=="Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

@st.cache_data(ttl=3600)
def get_movie_id_by_title(title, api_key):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api_key, "query": title}
    data = requests.get(url, params=params, timeout=10).json()
    results = data.get("results")
    if results: return results[0].get("id")
    return None

@st.cache_data(ttl=3600)
def get_trending_movies(api_key, count=5):
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}"
    data = requests.get(url, timeout=10).json()
    movies = []
    for m in data.get("results", [])[:count]:
        poster = f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get("poster_path") else None
        if m.get("id") and m.get("title"):
            movies.append({"id": m["id"], "title": m["title"], "poster": poster})
    return movies

@st.cache_data(ttl=3600)
def fetch_category_movies(api_key, category, page):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {"api_key": api_key, "sort_by":"popularity.desc", "page":page}
    category_map = {
        "Hollywood":{"with_original_language":"en"}, "Bollywood":{"with_original_language":"hi"},
        "K-Drama":{"with_original_language":"ko"}, "Action":{"with_genres":"28"},
        "Comedy":{"with_genres":"35"}, "Romance":{"with_genres":"10749"}, "Horror":{"with_genres":"27"},
        "Thriller":{"with_genres":"53"}, "Sci-Fi":{"with_genres":"878"}, "Animation":{"with_genres":"16"},
        "Drama":{"with_genres":"18"}, "Crime":{"with_genres":"80"}, "Fantasy":{"with_genres":"14"},
        "Adventure":{"with_genres":"12"}, "Family":{"with_genres":"10751"}, "Mystery":{"with_genres":"9648"},
        "War":{"with_genres":"10752"}, "Music":{"with_genres":"10402"}, "Western":{"with_genres":"37"}
    }

    params.update(category_map.get(category, {}))
    data = requests.get(url, params=params, timeout=10).json()
    movies = []
    for m in data.get("results", [])[:MOVIES_PER_PAGE]:
        poster = f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get("poster_path") else None
        if m.get("id") and m.get("title"):
            movies.append({"id": m["id"], "title": m["title"], "poster": poster})
    return movies

@st.cache_data(ttl=3600)
def get_movie_details(movie_id, api_key):
    if not movie_id: return None
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": api_key}
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None

#HELPER: RENDER MOVIE CARD
def render_movie_card(movie, trailer=None, section="general", row_idx=0, col_idx=0):
    st.markdown('<div class="movie-card-container">', unsafe_allow_html=True)
    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
    
    if movie.get("poster"):
        st.image(movie["poster"], width=300)
    st.caption(movie.get("title", "Unknown Title"))

    # UNIQUE BUTTON KEY
    movie_id = movie.get('id') or f"noid_{section}_{row_idx}_{col_idx}"
    button_key = f"details_{section}_{movie_id}_{row_idx}_{col_idx}"
    details_button = st.button(f"ℹ️ Details", key=button_key)

    if trailer:
        with st.expander("▶️ Watch Trailer"):
            st.video(trailer, start_time=0)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

    # STORE movie in session state when button clicked
    if details_button:
        st.session_state.sidebar_movie = movie


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

raw_movies = fetch_category_movies(TMDB_API_KEY, category, st.session_state.category_page)
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
