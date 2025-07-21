import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("❌ API_KEY not found in environment variables.")

def fetch_poster_details(movie_name):
    """
    Fetches the poster URL and movie details from TMDB API.
    """
    # Search for the movie by name
    search_url = f"https://api.themoviedb.org/3/search/movie"
    search_params = {
        "api_key": API_KEY,
        "query": movie_name
    }

    search_response = requests.get(search_url, params=search_params)
    if search_response.status_code != 200:
        raise Exception(f"❌ Failed to search movie: {search_response.text}")
    
    search_data = search_response.json()
    if not search_data["results"]:
        return None  # No result found

    movie = search_data["results"][0]
    movie_id = movie["id"]

    # Get movie details by ID
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    details_params = {
        "api_key": API_KEY
    }

    details_response = requests.get(details_url, params=details_params)
    if details_response.status_code != 200:
        raise Exception(f"❌ Failed to get movie details: {details_response.text}")
    
    details_data = details_response.json()

    poster_path = details_data.get("poster_path")
    if poster_path:
        full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        return full_poster_url
    else:
        return None
