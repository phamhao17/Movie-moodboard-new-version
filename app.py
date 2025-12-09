import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
import random

# ====== API keys from Streamlit secrets ======
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# ====== Initialize TMDb ======
from tmdbv3api import TMDb, Movie
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
tmdb.language = 'en'
movie = Movie()

# ====== Initialize Spotify ======
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
spotify_auth = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = spotipy.Spotify(auth_manager=spotify_auth)

# ====== Streamlit Config ======
st.set_page_config(page_title="Movie Moodboard", layout="wide")
st.title("🎬 Movie Moodboard (Python 3.13 Ready)")

# ====== User Inputs ======
scene_description = st.text_area("Describe your movie scene:", "")
uploaded_file = st.file_uploader("Or upload an image:", type=['jpg','png'])
mood = st.selectbox("Choose a mood:", ["Happy", "Sad", "Suspenseful", "Romantic"])

# ====== Helper: placeholder fallback ======
def get_placeholder(mood):
    path = os.path.join("assets", f"{mood.lower()}1.jpg")
    if os.path.exists(path):
        return Image.open(path)
    return None

# ====== TMDb Poster ======
if scene_description:
    st.subheader("🎨 Movie Poster (TMDb)")
    try:
        results = movie.search(scene_description)
        if results and results[0].poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{results[0].poster_path}"
            poster_img = Image.open(BytesIO(requests.get(poster_url).content))
            st.image(poster_img, caption=results[0].title, use_column_width=True)
        else:
            st.info("No poster found. Using placeholder.")
            placeholder_img = get_placeholder(mood)
            if placeholder_img:
                st.image(placeholder_img, caption="Placeholder", use_column_width=True)
    except Exception as e:
        st.error(f"TMDb error: {e}")

# ====== AI Concept Art ======
if scene_description:
    st.subheader("🖌️ AI Concept Art (OpenAI DALL·E)")
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        prompt = f"Concept art for a {mood.lower()} movie scene: {scene_description}"
        response = openai.Image.create(prompt=prompt, n=1, size="512x512")
        image_url = response['data'][0]['url']
        ai_img = Image.open(BytesIO(requests.get(image_url).content))
        st.image(ai_img, caption="AI Concept Art", use_column_width=True)
    except:
        st.info("OpenAI API error. Using placeholder.")
        placeholder_img = get_placeholder(mood)
        if placeholder_img:
            st.image(placeholder_img, caption="Placeholder", use_column_width=True)

# ====== Music Suggestion ======
st.subheader("🎵 Suggested Music Playlist")
try:
    results = spotify.search(q=mood, type='playlist', limit=1)
    if results['playlists']['items']:
        playlist = results['playlists']['items'][0]
        st.markdown(f"[{playlist['name']}]({playlist['external_urls']['spotify']})")
    else:
        st.info("No playlist found. Using example link.")
except:
    st.info("Spotify API error. Using example link.")
    st.write("🎵 Example playlist link")

# ====== Scene Summary ======
st.subheader("📝 Scene Summary")
st.write(f"Scene: {scene_description}")
st.write(f"Mood: {mood}")

# ====== Uploaded Image Display ======
if uploaded_file:
    try:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)
    except:
        st.info("Uploaded image cannot be displayed. Using placeholder.")
        placeholder_img = get_placeholder(mood)
        if placeholder_img:
            st.image(placeholder_img, caption="Placeholder", use_column_width=True)
