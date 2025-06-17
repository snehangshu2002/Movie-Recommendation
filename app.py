import pickle
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Movie Recommender", layout="wide")

# App header
st.title("🎬 Movie Recommender System")

try:
    # Load data
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    movie_photo = pickle.load(open('photo.pkl', 'rb'))

    # Movie list for dropdown
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "📽️ Type or select a movie from the dropdown:",
        movie_list
    )

    # Recommendation function
    def recommend(movie):
        try:
            index = movies[movies['title'] == movie].index[0]
            distances = sorted(
                list(enumerate(similarity[index])),
                reverse=True,
                key=lambda x: x[1]
            )

            recommended_movie_names = []
            recommended_movie_posters = []
            recommended_movie_trailers = []

            for i in distances[1:6]:  # Top 5 recommendations
                # Get the movie title
                movie_title = movies.iloc[i[0]]['title']

                # Get trailer info from TMDb API using title search first
                search_url = "https://api.themoviedb.org/3/search/movie"
                headers = {
                    "accept": "application/json",
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiNDZkYjZjZDQ4ZGI5YzExMDQ1MDE2Y2YwM2U4ODc5MiIsIm5iZiI6MTc0OTk5ODgyOC44NjksInN1YiI6IjY4NGVkY2VjOGIwYzNkMWMwM2IwZTg0NyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OmF4cjOsvnDoJ5tAfYD54-2Kp_9GwwmdAuPRDlpJ9LI"
                }
                
                try:
                    # First, search for the movie to get its TMDb ID
                    search_response = requests.get(
                        search_url,
                        headers=headers,
                        params={"query": movie_title}
                    )
                    search_response.raise_for_status()
                    search_results = search_response.json().get("results", [])
                    
                    if search_results:
                        tmdb_id = search_results[0]["id"]
                        
                        # Now get the videos using the TMDb ID
                        videos_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
                        videos_response = requests.get(videos_url, headers=headers)
                        videos_response.raise_for_status()
                        
                        results = videos_response.json().get("results", [])
                        if results:
                            # Create DataFrame with key and add current timestamp for published_at
                            df = pd.DataFrame(results)
                            if "key" not in df.columns:
                                trailer_url = "Trailer not available"
                            else:
                                # Add current timestamp as published_at if it doesn't exist
                                if "published_at" not in df.columns:
                                    df["published_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                                df["youtube_url"] = "https://www.youtube.com/watch?v=" + df["key"]
                                # Sort by published_at if available, otherwise use first result
                                if "published_at" in df.columns:
                                    df = df.sort_values("published_at", ascending=False)
                                trailer_url = df["youtube_url"].iloc[0]
                        else:
                            trailer_url = "Trailer not available"
                    else:
                        trailer_url = "Trailer not available"
                        
                except Exception as e:
                    st.warning(f"Could not fetch trailer for {movie_title}: {str(e)}")
                    trailer_url = "Trailer not available"

                # Append movie data
                recommended_movie_names.append(movies.iloc[i[0]]['title'])
                recommended_movie_posters.append(movie_photo['poster_path'].iloc[i[0]])
                recommended_movie_trailers.append(trailer_url)

            return recommended_movie_names, recommended_movie_posters, recommended_movie_trailers
        except Exception as e:
            st.error(f"Error in recommendation function: {str(e)}")
            return [], [], []

    # Recommendation display
    if st.button("🎯 Show Recommendation"):
        with st.spinner("Getting recommendations..."):
            names, posters, trailers = recommend(selected_movie)
            if names:
                cols = st.columns(5)
                for idx, col in enumerate(cols):
                    with col:
                        if posters[idx].startswith('http'):
                            st.image(posters[idx], use_container_width=True)
                        else:
                            st.image(f"https://image.tmdb.org/t/p/w500/{posters[idx]}", use_container_width=True)
                        st.caption(names[idx])
                        if trailers[idx] != "Trailer not available":
                            st.markdown(f"[▶ Watch Trailer]({trailers[idx]})", unsafe_allow_html=True)
                        else:
                            st.markdown("*Trailer not available*")

except FileNotFoundError as e:
    st.error(f"Error loading required files: {str(e)}")
except Exception as e:
    st.error(f"An unexpected error occurred: {str(e)}")
