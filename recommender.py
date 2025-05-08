import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

@st.cache_data
def load_and_prepare_data(movies_path='tmdb_5000_movies.csv', credits_path='tmdb_5000_credits.csv'):
    credits = pd.read_csv(credits_path)
    movies = pd.read_csv(movies_path)
    movies_credits = movies.merge(credits, on='title')
    movies_credits = movies_credits[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
    
    for feature in ['genres', 'keywords', 'cast', 'crew']:
        movies_credits[feature] = movies_credits[feature].apply(lambda x: [i['name'] for i in ast.literal_eval(x)] if pd.notna(x) else [])
    
    movies_credits['overview'] = movies_credits['overview'].fillna('')
    movies_credits['tags'] = movies_credits['overview'] + ' ' +                               movies_credits['genres'].apply(lambda x: ' '.join(x)) + ' ' +                               movies_credits['keywords'].apply(lambda x: ' '.join(x)) + ' ' +                               movies_credits['cast'].apply(lambda x: ' '.join(x[:3])) + ' ' +                               movies_credits['crew'].apply(lambda x: ' '.join(x[:1]))  # Only director
    
    new_df = movies_credits[['movie_id', 'title', 'tags']].copy()
    new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())
    return new_df

@st.cache_data
def compute_similarity_matrix(df):
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
    vectors = tfidf.fit_transform(df['tags'])
    similarity = cosine_similarity(vectors)
    return similarity

def get_recommendations(movie_title, df, similarity, top_n=5):
    # Partial match support
    matches = df[df['title'].str.lower().str.contains(movie_title.lower())]

    if matches.empty:
        return pd.DataFrame()

    idx = matches.index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    return df.iloc[[i[0] for i in sim_scores]][['title']]


