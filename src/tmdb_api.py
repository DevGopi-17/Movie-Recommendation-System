import requests

IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
BASE_URL = "https://api.themoviedb.org/3"


# GLOBAL IN-MEMORY CACHES
_movie_cache = {}
_trailer_cache = {}
_category_cache = {}
_search_cache = {}

# INTERNAL REQUEST HELPER
def _tmdb_get(endpoint, api_key, params=None):
    params = params or {}
    params["api_key"] = api_key
    url = f"{BASE_URL}{endpoint}"
    return requests.get(url, params=params, timeout=10).json()


# MOVIE DETAILS (CACHED)
def get_movie_details(movie_id, api_key):
    if not movie_id:
        return None

    if movie_id in _movie_cache:
        return _movie_cache[movie_id]

    data = _tmdb_get(f"/movie/{movie_id}", api_key)
    _movie_cache[movie_id] = data
    return data


# TRAILER (CACHED)
def get_trailer(movie_id, api_key):
    if not movie_id:
        return None

    if movie_id in _trailer_cache:
        return _trailer_cache[movie_id]

    data = _tmdb_get(f"/movie/{movie_id}/videos", api_key)

    trailer_url = None
    for v in data.get("results", []):
        if v.get("site") == "YouTube" and v.get("type") == "Trailer":
            trailer_url = f"https://www.youtube.com/watch?v={v['key']}"
            break

    _trailer_cache[movie_id] = trailer_url
    return trailer_url


# SEARCH MOVIE (CACHED)
def get_movie_id_by_title(title, api_key):
    if not title:
        return None

    if title in _search_cache:
        return _search_cache[title]

    data = _tmdb_get("/search/movie", api_key, {"query": title})
    results = data.get("results")

    movie_id = results[0]["id"] if results else None
    _search_cache[title] = movie_id
    return movie_id

# TRENDING MOVIES
def get_trending_movies(api_key, count=5):
    cache_key = f"trending_{count}"
    if cache_key in _category_cache:
        return _category_cache[cache_key]

    data = _tmdb_get("/trending/movie/week", api_key)

    movies = [
        {
            "id": m["id"],
            "title": m["title"],
            "poster": f"{IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None
        }
        for m in data.get("results", [])[:count]
    ]

    _category_cache[cache_key] = movies
    return movies


# CATEGORY MOVIES (BIGGEST WIN)
def fetch_category_movies(api_key, category, page, per_page=15):
    cache_key = f"{category}_{page}_{per_page}"
    if cache_key in _category_cache:
        return _category_cache[cache_key]

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

    params = {
        "sort_by": "popularity.desc",
        "page": page,
    }
    params.update(category_map.get(category, {}))

    data = _tmdb_get("/discover/movie", api_key, params)

    movies = [
        {
            "id": m["id"],
            "title": m["title"],
            "poster": f"{IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None
        }
        for m in data.get("results", [])[:per_page]
    ]

    _category_cache[cache_key] = movies
    return movies


from concurrent.futures import ThreadPoolExecutor

def preload_trailers(movie_ids, api_key):
    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(lambda m: get_trailer(m, api_key), movie_ids)
