import pickle
import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(page_title="Movie Recommender", layout="wide")

# App header
st.title("🎬 Movie Recommender System")

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
        movie_id = movies.iloc[i[0]].title

        # Get trailer info from TMDb API
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiNDZkYjZjZDQ4ZGI5YzExMDQ1MDE2Y2YwM2U4ODc5MiIsIm5iZiI6MTc0OTk5ODgyOC44NjksInN1YiI6IjY4NGVkY2VjOGIwYzNkMWMwM2IwZTg0NyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OmF4cjOsvnDoJ5tAfYD54-2Kp_9GwwmdAuPRDlpJ9LI"
        }

        response = requests.get(url, headers=headers)

        # Process trailer data
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                df = pd.DataFrame(results)[["key", "published_at"]]
                df["youtube_url"] = "https://www.youtube.com/watch?v=" + df["key"]
                trailer_url = df.sort_values("published_at", ascending=False)["youtube_url"].iloc[0]
            else:
                trailer_url = "Trailer not available"
        else:
            trailer_url = "Trailer not available"

        # Append movie data
        recommended_movie_names.append(movie_photo['title'][i[0]])
        recommended_movie_posters.append(movie_photo['poster_path'][i[0]])
        recommended_movie_trailers.append(trailer_url)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_trailers

# Recommendation display
if st.button("🎯 Show Recommendation"):
    names, posters, trailers = recommend(selected_movie)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True)
            st.caption(names[idx])
            if trailers[idx] != "Trailer not available":
                st.markdown(f"[▶ Watch Trailer]({trailers[idx]})", unsafe_allow_html=True)
            else:
                st.markdown("*Trailer not available*")
