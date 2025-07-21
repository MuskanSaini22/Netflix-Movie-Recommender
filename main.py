from app import fetch_poster_details
import time

movie_list = ['The Matrix', 'Apollo 18', 'The American', 'The Inhabited Island', 'Tears of the Sun']

for movie in movie_list:
    try:
        print(f"\n🎬 Fetching poster for: {movie}")
        result = fetch_poster_details(movie)
        print(f"✅ Poster URL: {result}")
        time.sleep(1)  # Add a 1-second delay to avoid hitting API limits
    except Exception as e:
        print(f"❌ Failed for {movie}: {e}")
