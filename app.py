# app.py
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
import random
import numpy as np

# Optional AI feature extraction
import torch
from torchvision import transforms, models
from sklearn.metrics.pairwise import cosine_similarity

# API keys from Streamlit Secrets
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

st.set_page_config(page_title="Movie Moodboard AI", layout="wide")
st.title("🎬 Movie Moodboard AI")

# -------------------------
# Load movie dataset vectors
# -------------------------
# movie_vectors.npy: shape (num_images, feature_dim)
# movie_files.npy: paths to images in movie_images/
if os.path.exists("data/movie_vectors.npy") and os.path.exists("data/movie_files.npy"):
    movie_vectors = np.load("data/movie_vectors.npy")
    movie_files = np.load("data/movie_files.npy", allow_pickle=True)
else:
    movie_vectors = None
    movie_files = None

# -------------------------
# Image Feature Extractor
# -------------------------
resnet = models.resnet50(pretrained=True)
resnet.eval()
preprocess = transforms.Compose([
    transforms.Resize(224),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

def get_feature_vector(img):
    img_t = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        features = resnet(img_t)
    return features.squeeze().numpy()

# -------------------------
# User input
# -------------------------
st.subheader("1️⃣ Upload an image (optional)")
uploaded_file = st.file_uploader("Upload an image:", type=["jpg","png"])

st.subheader("2️⃣ Or enter keywords (optional)")
col1, col2, col3, col4 = st.columns(4)
with col1:
    character = st.text_input("Character")
with col2:
    genre = st.text_input("Genre")
with col3:
    setting = st.text_input("Setting")
with col4:
    dialogue = st.text_input("Dialogue")

mood = st.selectbox("Choose mood (affects music):", ["Happy","Sad","Suspenseful","Romantic"])

# -------------------------
# Step 1: Find Movie Images
# -------------------------
st.subheader("🎨 Movie Image Suggestions")

found_images = []

# If user uploaded an image
if uploaded_file and movie_vectors is not None:
    user_image = Image.open(uploaded_file)
    st.image(user_image, caption="Uploaded Image", use_column_width=True)
    
    # Extract feature vector
    user_vector = get_feature_vector(user_image)
    similarities = cosine_similarity([user_vector], movie_vectors)[0]
    top_idx = similarities.argsort()[-5:][::-1]
    for idx in top_idx:
        img_path = movie_files[idx]
        if os.path.exists(img_path):
            found_images.append(img_path)
            st.image(Image.open(img_path), caption=f"Similar: {os.path.basename(img_path)}", width=200)

# If no upload or no dataset, fallback to keyword search
if not found_images:
    st.info("No uploaded image or dataset missing. Using keyword search / placeholder images.")
    
    # Simple local placeholder logic
    mood_images = {
        "Happy":["assets/happy1.jpg","assets/happy2.jpg"],
        "Sad":["assets/sad1.jpg","assets/sad2.jpg"],
        "Romantic":["assets/romantic1.jpg"],
        "Suspenseful":["assets/suspense1.jpg"]
    }
    if mood in mood_images and mood_images[mood]:
        selected_image = random.choice(mood_images[mood])
        if os.path.exists(selected_image):
            st.image(Image.open(selected_image), caption=f"{mood} Placeholder", use_column_width=True)

# -------------------------
# Step 2: Music Suggestion
# -------------------------
st.subheader("🎵 Suggested Music Playlist")
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    spotify_auth = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    spotify = spotipy.Spotify(auth_manager=spotify_auth)
    
    results = spotify.search(q=mood, type='playlist', limit=1)
    if results['playlists']['items']:
        playlist = results['playlists']['items'][0]
        st.markdown(f"[{playlist['name']}]({playlist['external_urls']['spotify']})")
    else:
        st.info("No playlist found for this mood.")
except Exception as e:
    st.info("Spotify API error or placeholder used.")

# -------------------------
# Step 3: Movie Suggestion (TMDb API)
# -------------------------
st.subheader("🎬 Suggested Movies")
try:
    import requests
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={genre or character or setting or dialogue}"
    response = requests.get(tmdb_url)
    data = response.json()
    if data.get("results"):
        for m in data["results"][:5]:
            title = m.get("title")
            poster_path = m.get("poster_path")
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}"
                st.image(poster_url, caption=title)
            else:
                st.write(title)
    else:
        st.info("No movie found for the given keywords.")
except Exception as e:
    st.info("TMDb API error or placeholder used.")

# -------------------------
# Step 4: Scene Summary
# -------------------------
st.subheader("📝 Scene Summary")
st.write(f"Character: {character}")
st.write(f"Genre: {genre}")
st.write(f"Setting: {setting}")
st.write(f"Dialogue: {dialogue}")
st.write(f"Mood: {mood}")
if uploaded_file:
    st.write("Image uploaded by user.")
