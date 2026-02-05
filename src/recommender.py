import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def fetch_poster(movie_id, api_key):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    data = requests.get(url).json()

    poster_path = data.get("poster_path")
    if poster_path:
        return "https://image.tmdb.org/t/p/w500" + poster_path
    return None


class MovieRecommender:
    def __init__(self, movies_df):
        self.movies = movies_df

        cv = CountVectorizer(max_features=5000, stop_words="english")
        self.vectors = cv.fit_transform(self.movies["tags"]).toarray()
        self.similarity = cosine_similarity(self.vectors)

    def recommend(self, movie, api_key):
        movie = movie.lower()
        titles = self.movies["title"].str.lower()

        if movie not in titles.values:
            return []

        movie_index = self.movies[titles == movie].index[0]

        distances = sorted(
            list(enumerate(self.similarity[movie_index])),
            reverse=True,
            key=lambda x: x[1]
        )

        recommendations = []

        for i in distances[1:6]:
            movie_id = self.movies.iloc[i[0]].movie_id
            title = self.movies.iloc[i[0]].title
            poster = fetch_poster(movie_id, api_key)

            recommendations.append({
                "title": title,
                "poster": poster
            })

        return recommendations

