import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import pandas as pd
import random
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Streamlit secrets (set in Streamlit Cloud)
# -----------------------------
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# Optional: Initialize Spotify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

spotify_auth = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = spotipy.Spotify(auth_manager=spotify_auth)

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Movie Moodboard", layout="wide")
st.title("🎬 Movie Moodboard")

# -----------------------------
# Upload image or enter scene description
# -----------------------------
uploaded_file = st.file_uploader("Upload an image of your scene (optional):", type=["jpg","png"])
scene_description = st.text_area("Or describe your movie scene:", "")

# Select mood
mood = st.selectbox("Choose a mood:", ["Happy", "Sad", "Suspenseful", "Romantic"])

# -----------------------------
# Load placeholder movie dataset (vectors + filenames)
# -----------------------------
@st.cache_data
def load_movie_dataset():
    try:
        vectors = np.load("movie_vectors.npy")
        files = np.load("movie_files.npy", allow_pickle=True)
    except:
        vectors = np.zeros((1,512))  # dummy vector
        files = np.array(["assets/placeholder.jpg"])
    return vectors, files

movie_vectors, movie_files = load_movie_dataset()

# -----------------------------
# Function to find similar images
# -----------------------------
def find_similar_image(img_vector, top_k=1):
    similarities = cosine_similarity([img_vector], movie_vectors)[0]
    indices = similarities.argsort()[::-1][:top_k]
    return [movie_files[i] for i in indices]

# -----------------------------
# Display section
# -----------------------------
st.subheader("🎨 Scene Image")

if uploaded_file:
    try:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Scene", use_column_width=True)
        
        # Here: placeholder for image vectorization
        img_vector = np.random.rand(512)  # simulate feature vector
        similar_images = find_similar_image(img_vector)
        st.subheader("Similar Movie Images")
        for sim_img_path in similar_images:
            sim_img = Image.open(sim_img_path)
            st.image(sim_img, use_column_width=True)
    except Exception as e:
        st.error(f"Error processing uploaded image: {e}")
else:
    st.info("No image uploaded. Using keywords to suggest images.")
    # Keyword-based placeholders
    keyword_images = {
        "Happy": ["assets/happy1.jpg","assets/happy2.jpg"],
        "Sad": ["assets/sad1.jpg","assets/sad2.jpg"],
        "Romantic": ["assets/romantic1.jpg"],
        "Suspenseful": ["assets/suspense1.jpg"]
    }
    selected_image = random.choice(keyword_images[mood])
    st.image(Image.open(selected_image), caption=f"{mood} mood placeholder", use_column_width=True)

# -----------------------------
# Suggest music
# -----------------------------
st.subheader("🎵 Suggested Music Playlist")
try:
    results = spotify.search(q=mood, type='playlist', limit=1)
    if results['playlists']['items']:
        playlist = results['playlists']['items'][0]
        st.markdown(f"[{playlist['name']}]({playlist['external_urls']['spotify']})")
    else:
        st.info("No playlist found for this mood.")
except Exception as e:
    st.info("Spotify API error or placeholder used.")
    st.write(f"Suggested playlist for {mood} mood: 🎵 Example Playlist Link")

# -----------------------------
# Scene summary
# -----------------------------
st.subheader("📝 Scene Summary")
st.write(f"Scene description: {scene_description}")
st.write(f"Mood: {mood}")
