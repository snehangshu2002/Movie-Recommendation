# Movie Recommendation System

![Movie Recommendation](https://img.shields.io/badge/Python-3.8+-blue.svg)


A content-based movie recommendation system built using The Movie Database (TMDB) API, Python, and NLP techniques. This project fetches top-rated movie data, processes it with lemmatization and vectorization, and recommends similar movies based on cosine similarity, complete with poster URLs for a visual experience.

**Last Updated:** June 17, 2025, at 07:13 PM IST

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [Dependencies](#dependencies)
- [Sample Output](#sample-output)
- [License](#license)
- [Contributing](#contributing)

## Overview
This project leverages the TMDB API to collect data on top-rated movies, including titles, overviews, genres, and poster paths. It preprocesses the data by combining movie overviews and genres into a "tags" feature, applies lemmatization using NLTK, and converts the text into numerical vectors using `CountVectorizer`. Cosine similarity is computed to identify similar movies, and a recommendation function outputs the top 5 similar movies with their poster URLs. The processed data and similarity matrix are saved as pickle files for reuse.

## Features
- Fetches movie data from TMDB API across 500 pages.
- Preprocesses text data with lemmatization and vectorization.
- Computes content-based recommendations using cosine similarity.
- Outputs movie titles and poster URLs for a visual recommendation experience.
- Saves processed data and similarity matrix for efficient reuse.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/snehangshu2002/Movie-Recommendation.git
   cd Movie-Recommendation
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Obtain a TMDB API key:
   - Sign up at [TMDB](https://www.themoviedb.org/) and generate an API key.
   - Replace the `Bearer` token in the code (e.g., `eyJhbGciOiJIUzI1NiJ9...`) with your API key.
4. Download NLTK’s WordNet resource:
   ```python
   import nltk
   nltk.download('wordnet')
   ```

## Usage
1. Run the main script to fetch data, preprocess it, and generate recommendations:
   ```bash
   python movie recommendation.py
   ```
2. Use the `recommend()` function to get recommendations for a movie title:
   ```python
   recommend('A Passage to India')
   ```
   This will output the top 5 similar movies and their poster URLs.
3. The script saves the following files:
   - `movie_list.pkl`: Processed DataFrame with movie titles and tags.
   - `similarity.pkl`: Cosine similarity matrix.
   - `photo.pkl`: Original DataFrame with poster paths.

## Code Structure
The project follows these key steps, implemented in the main script:

1. **Importing Libraries**:
   This section imports all necessary libraries for data handling, API requests, text processing, and similarity computation.
   ```python
   import pandas as pd
   import numpy as np
   from tqdm.notebook import tqdm
   import requests
   import nltk
   from nltk.stem import WordNetLemmatizer
   from sklearn.feature_extraction.text import CountVectorizer
   from sklearn.metrics.pairwise import cosine_similarity
   import pickle
   ```

2. **Data Collection**:
   This section fetches movie data from the TMDB API across 500 pages and stores it in a DataFrame with fields like `id`, `title`, `overview`, `genre_ids`, and `poster_path`.
   ```python
   for i in tqdm(range(1,501)):
       url = f"https://api.themoviedb.org/3/movie/top_rated?language=en-US&page={i}"
       headers = {
           "accept": "application/json",
           "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiNDZkYjZjZDQ4ZGI5YzExMDQ1MDE2Y2YwM2U4ODc5MiIsIm5iZiI6MTc0OTk5ODgyOC44NjksInN1YiI6IjY4NGVkY2VjOGIwYzNkMWMwM2IwZTg0NyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OmF4cjOsvnDoJ5tAfYD54-2Kp_9GwwmdAuPRDlpJ9LI"
       }
       response = requests.get(url, headers=headers)
       temp_df = pd.DataFrame(response.json()["results"])[["id","title","overview","genre_ids","poster_path"]]
       df = pd.concat([df, temp_df], ignore_index=True)
   ```

3. **Data Preprocessing**:
   This section maps genre IDs to names, combines overviews and genres into a `tags` column, and applies lemmatization to normalize text.
   ```python
   genre_mapping = {
       28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
       99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
       27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance",
       878: "Science Fiction", 10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
   }
   new_df['genre_ids'] = new_df['genre_ids'].apply(lambda ids: [genre_mapping.get(id) for id in ids])
   new_df["overview"] = new_df["overview"].apply(lambda x: x.split())
   new_df["tags"] = new_df['overview'] + new_df['genre_ids']
   new_df.drop(columns=["overview","genre_ids"], inplace=True)
   new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
   lemmatizer = WordNetLemmatizer()
   def lemma(text):
       y = []
       for i in text.split():
           y.append(lemmatizer.lemmatize(i))
       return " ".join(y)
   new_df['tags'] = new_df['tags'].apply(lemma)
   ```

4. **Feature Extraction**:
   This section converts the `tags` column into numerical vectors using `CountVectorizer`.
   ```python
   cv = CountVectorizer(max_features=10000, stop_words="english")
   vectors = cv.fit_transform(new_df["tags"]).toarray()
   ```

5. **Similarity Computation**:
   This section computes the cosine similarity between movie vectors to enable recommendations.
   ```python
   similarity = cosine_similarity(vectors)
   ```

6. **Recommendation Function**:
   This section defines a function to recommend the top 5 similar movies, outputting their titles and poster URLs.
   ```python
   def recommend(movie):
       index = new_df[new_df['title'] == movie].index[0]
       distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
       for i in distances[1:6]:
           print(new_df.iloc[i[0]].title)
           print(df['poster_path'][i[0]])
   ```

7. **Data Persistence**:
   This section saves the processed DataFrame, similarity matrix, and original DataFrame with poster paths as pickle files.
   ```python
   pickle.dump(new_df, open('movie_list.pkl', 'wb'))
   pickle.dump(similarity, open('similarity.pkl', 'wb'))
   pickle.dump(df, open('photo.pkl', 'wb'))
   ```

8. **Poster Path Update**:
   This section updates the `poster_path` column with full TMDB URLs for direct image access.
   ```python
   df['poster_path'] = df['poster_path'].apply(lambda x: "https://image.tmdb.org/t/p/original" + str(x))
   ```

## Dependencies
Create a `requirements.txt` file with:
```
streamlit
pandas
numpy
requests

```
Install them using:
```bash
pip install -r requirements.txt
```

## Sample Output
Running `recommend('A Passage to India')` produces:
```
Life of Pi
https://image.tmdb.org/t/p/original/iLgRu4hhSr6V1uManX6ukDriiSc.jpg
Gandhi
https://image.tmdb.org/t/p/original/rOXftt7SluxskrFrvU7qFJa5zeN.jpg
Lagaan: Once Upon a Time in India
https://image.tmdb.org/t/p/original/yNX9lFRAFeNLNRIXdqZK9gYrYKa.jpg
Victoria & Abdul
https://image.tmdb.org/t/p/original/uIzQ8zZ0rqjqqJUIpeeovtTryAa.jpg
Dilwale Dulhania Le Jayenge
https://image.tmdb.org/t/p/original/2CAL2433ZeIihfX1Hb2139CX0pW.jpg
```

## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Feel free to raise issues for bugs or feature requests. Let’s make this project better together!

