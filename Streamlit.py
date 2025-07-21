import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import time

st.title("🎥 Movie Recommender")
st.markdown("### 🍿 Netflix-style Movie Recommender App")
st.markdown("""
Welcome! This app suggests movies similar to the one you choose using Natural Language Processing (TF-IDF and Cosine Similarity).  
We use the movie's overview to understand its theme and recommend similar ones.

👉 Built with **Python, Streamlit, and TMDB dataset**  
👉 Powered by **TF-IDF Vectorizer + Cosine Similarity**
""") 

# Load data
movies = pd.read_csv("tmdb_5000_movies.csv")

# Fill missing overviews
movies['overview'] = movies['overview'].fillna('')

# Vectorize the overview column
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['overview'])

# Compute similarity matrix
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Reset index so we can use title to locate rows
movies = movies.reset_index()
indices = pd.Series(movies.index, index=movies['title'])

# Poster fetcher


import os
from dotenv import load_dotenv
import requests
from time import sleep

load_dotenv()
API_KEY = os.getenv("API_KEY")

def fetch_poster_details(movie_title):
    if not API_KEY:
        print("❌ API_KEY not found in environment variables.")
        return None

    try:
        # Step 1: Get Movie ID
        search_url = f"https://api.themoviedb.org/3/search/movie"
        params = {"api_key": API_KEY, "query": movie_title}
        response = requests.get(search_url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            print(f"❌ Movie '{movie_title}' not found.")
            return None

        movie_id = data["results"][0].get("id")
        if not movie_id:
            print(f"❌ No movie ID found for '{movie_title}'")
            return None

        # Step 2: Get Poster from Movie ID
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": API_KEY, "language": "en-US"}
        response = requests.get(details_url, params=params, timeout=8)
        response.raise_for_status()
        details = response.json()

        poster_path = details.get("poster_path")
        if not poster_path:
            print(f"❌ No poster found for '{movie_title}' (ID: {movie_id})")
            return None

        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        print(f"✅ {movie_title} → {poster_url}")
        return poster_url

    except requests.exceptions.Timeout:
        print(f"❌ Timeout error for '{movie_title}'")
    except requests.exceptions.HTTPError as err:
        print(f"❌ HTTP error for '{movie_title}': {err}")
    except requests.exceptions.ConnectionError as err:
        print(f"❌ Connection error for '{movie_title}': {err}")
    except Exception as e:
        print(f"❌ Unexpected error for '{movie_title}': {e}")

    return None



# Recommend function
def recommend(movie_title, top_n=5):
    idx = indices.get(movie_title)
    if idx is None:
        return [], [], [], []

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    movie_indices = [i[0] for i in sim_scores]

    recommended_titles = movies['title'].iloc[movie_indices].tolist()
    poster_links, overviews, ratings = [], [], []

    recommended_titles = movies['title'].iloc[movie_indices].tolist()
    overviews = movies['overview'].iloc[movie_indices].tolist()
    ratings = movies['vote_average'].iloc[movie_indices].tolist()
    posters = [fetch_poster_details(title) for title in recommended_titles]


    return recommended_titles, posters, ratings, overviews

# 🎬 Streamlit Frontend
st.title("🎥 Movie Recommender")
st.write("Select a movie and get similar movie suggestions!")

selected_movie = st.selectbox("Choose a movie:", movies['title'].values)

if st.button("Recommend"):
    with st.spinner("🔍 Fetching top recommendations..."):
        recommended_titles, posters, ratings, overviews = recommend(selected_movie)

    if recommended_titles:
        st.markdown("---")
        st.markdown("## 🎯 Top Movie Recommendations")
        st.write("")  # Small spacing

        for i in range(len(recommended_titles)):
            col1, col2 = st.columns([1, 3], gap="large")

            with col1:
                try:
                    st.image(
                        posters[i] if posters[i] else "https://via.placeholder.com/300x450.png?text=No+Image",
                        use_container_width=True,
                    )
                except:
                    st.image("https://via.placeholder.com/300x450.png?text=No+Image", use_container_width=True)

            with col2:
                st.markdown(f"### 🎬 {recommended_titles[i]}")
                st.markdown(f"**⭐ IMDb Rating:** {ratings[i] if ratings[i] else 'N/A'}`")
                st.markdown("**📝 Overview:**")
                st.markdown(f"> {overviews[i] if overviews[i] else 'No overview available.'}")
            
            st.markdown("---")  # divider between recommendations

    else:
        st.warning("🚫 Movie not found or no similar movies available.")
