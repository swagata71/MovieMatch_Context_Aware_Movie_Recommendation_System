import streamlit as st
from recommender import load_and_prepare_data, compute_similarity_matrix, get_recommendations

st.set_page_config(page_title="MovieMatch", layout="centered")
st.title("🎬 MovieMatch: Context-Aware Recommender")

# Load movie data and similarity matrix
df = load_and_prepare_data()
similarity = compute_similarity_matrix(df)

# Text input for fuzzy title search
input_title = st.text_input("Start typing a movie title:")

if input_title:
    # Case-insensitive partial match
    matches = df[df['title'].str.lower().str.contains(input_title.lower())]['title'].tolist()

    if matches:
        selected_title = st.selectbox("Did you mean one of these?", matches)

        if selected_title:
            results = get_recommendations(selected_title, df, similarity)

            if not results.empty:
                st.subheader(f"Recommendations based on: {selected_title}")
                for _, row in results.iterrows():
                    st.markdown(f"**{row['title']}**")
            else:
                st.warning("No similar movies found.")
    else:
        st.warning("No matching titles found.")
