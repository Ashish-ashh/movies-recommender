import streamlit as st
import pickle
import pandas as pd
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -----------------------------
# Set Page Config
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")

# -----------------------------
# Custom Background CSS
# -----------------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?auto=format&fit=crop&w=1950&q=80");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0); /* Transparent header */
}

[data-testid="stSidebar"] {
    background-color: rgba(0,0,0,0.6); /* Dark transparent sidebar */
    color: white;
}

h1, h2, h3, h4, h5, h6, p, span, div {
    color: white !important;  /* Make all text white */
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Create a requests session with retry strategy
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# -----------------------------
# Fetch movie poster from TMDb
# -----------------------------
def fetch(id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key=3bf007867ff638d084c0f6d7eb1a1925&language=en-US"
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie ID {id}: {e}")
        return "https://via.placeholder.com/500x750?text=Error"

# -----------------------------
# Recommend function
# -----------------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]]['id']  # Fixed from .movie_id to ['id']
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_posters.append(fetch(movie_id))
        time.sleep(0.5)  # Rate limiting for TMDb API

    return recommended_movies, recommended_posters

# -----------------------------
# Streamlit UI
# -----------------------------
st.title('🍿 Movie Recommender System')

selected_movie_name = st.selectbox(
    '🎥 Choose a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True)
            st.markdown(f"**{names[idx]}**")