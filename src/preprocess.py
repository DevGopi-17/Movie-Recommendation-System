import pandas as pd
import ast
import os
from nltk.stem.porter import PorterStemmer

ps = PorterStemmer()


def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "Data")

    movies_path = os.path.join(DATA_DIR, "tmdb_5000_movies.csv")
    credits_path = os.path.join(DATA_DIR, "tmdb_5000_credits.csv")

    movies = pd.read_csv(movies_path)
    credits = pd.read_csv(credits_path)

    movies = movies.merge(credits, on="title")
    return movies


def convert(text):
    return [i["name"] for i in ast.literal_eval(text)]


def get_top_cast(text):
    return [i["name"] for i in ast.literal_eval(text)[:3]]


def get_director(text):
    for i in ast.literal_eval(text):
        if i["job"] == "Director":
            return i["name"]
    return ""


def stem(text):
    return " ".join(ps.stem(word) for word in text.split())


def preprocess_data(movies):
    movies = movies[
        ["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]
    ]

    movies.dropna(inplace=True)

    movies["genres"] = movies["genres"].apply(convert)
    movies["keywords"] = movies["keywords"].apply(convert)
    movies["cast"] = movies["cast"].apply(get_top_cast)
    movies["crew"] = movies["crew"].apply(get_director)

    movies["overview"] = movies["overview"].apply(lambda x: x.split())

    movies["genres"] = movies["genres"].apply(lambda x: [i.replace(" ", "") for i in x])
    movies["keywords"] = movies["keywords"].apply(lambda x: [i.replace(" ", "") for i in x])
    movies["cast"] = movies["cast"].apply(lambda x: [i.replace(" ", "") for i in x])
    movies["crew"] = movies["crew"].apply(lambda x: x.replace(" ", ""))

    #weighed tags (improvement)
    movies["tags"] = (
        movies["overview"] * 1 +          # lowest weight
        movies["genres"] * 3 +            # highest weight
        movies["keywords"] * 3 +          # high importance
        movies["cast"] * 2 +              # medium
        movies["crew"].apply(lambda x: [x] * 2)  # director weighted
    )

    movies["tags"] = movies["tags"].apply(lambda x: " ".join(x).lower())
    movies["tags"] = movies["tags"].apply(stem)

    return movies[["movie_id", "title", "tags"]]

