import pickle
import streamlit as st

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
    for i in distances[1:6]:  # Top 5 recommendations (excluding the selected movie)
        recommended_movie_names.append(movie_photo['title'][i[0]])
        recommended_movie_posters.append(movie_photo['poster_path'][i[0]])
    return recommended_movie_names, recommended_movie_posters

# Recommendation display
if st.button("🎯 Show Recommendation"):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True)
            st.caption(names[idx])
