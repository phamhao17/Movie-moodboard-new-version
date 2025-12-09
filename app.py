import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
import random

# ====== Streamlit Secrets ======
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
SPOTIFY_CLIENT_ID = st.secrets.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = st.secrets.get("SPOTIFY_CLIENT_SECRET")

# ====== Streamlit Config ======
st.set_page_config(page_title="Movie Moodboard", layout="wide")
st.title("🎬 Movie Moodboard (Python 3.13 Compatible)")

# ====== User Input ======
scene_description = st.text_area("Describe your movie scene:", "")
uploaded_file = st.file_uploader("Or upload an image:", type=['jpg','png'])
mood = st.selectbox("Choose a mood:", ["Happy", "Sad", "Suspenseful", "Romantic"])

# ====== Placeholder helper ======
def get_placeholder(mood):
    path = os.path.join("assets", f"{mood.lower()}1.jpg")
    if os.path.exists(path):
        return Image.open(path)
    return None

# ====== TMDb Poster ======
st.subheader("🎨 Movie Poster (TMDb)")
try:
    from tmdbv3api import TMDb, Movie
    if TMDB_API_KEY:
        tmdb = TMDb()
        tmdb.api_key = TMDB_API_KEY
        tmdb.language = 'en'
        movie = Movie()
        if scene_description:
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
    else:
        st.warning("TMDb API key not set. Using placeholder.")
        placeholder_img = get_placeholder(mood)
        if placeholder_img:
            st.image(placeholder_img, caption="Placeholder", use_column_width=True)
except ModuleNotFoundError:
    st.error("tmdbv3api not installed. Check requirements.txt!")

# ====== AI Concept Art ======
st.subheader("🖌️ AI Concept Art (OpenAI DALL·E)")
try:
    import openai
    if OPENAI_API_KEY and scene_description:
        openai.api_key = OPENAI_API_KEY
        prompt = f"Concept art for a {mood.lower()} movie scene: {scene_description}"
        response = openai.Image.create(prompt=prompt, n=1, size="512x512")
        image_url = response['data'][0]['url']
        ai_img = Image.open(BytesIO(requests.get(image_url).content))
        st.image(ai_img, caption="AI Concept Art", use_column_width=True)
    else:
        st.info("OpenAI API key not set or no description. Using placeholder.")
        placeholder_img = get_placeholder(mood)
        if placeholder_img:
            st.image(placeholder_img, caption="Placeholder", use_column_width=True)
except ModuleNotFoundError:
    st.error("openai package not installed. Check requirements.txt!")

# ====== Spotify Playlist ======
st.subheader("🎵 Suggested Music Playlist")
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
        spotify_auth = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        spotify = spotipy.Spotify(auth_manager=spotify_auth)
        results = spotify.search(q=mood, type='playlist', limit=1)
        if results['playlists']['items']:
            playlist = results['playlists']['items'][0]
            st.markdown(f"[{playlist['name']}]({playlist['external_urls']['spotify']})")
        else:
            st.info("No playlist found. Using example link.")
            st.write("🎵 Example playlist link")
    else:
        st.info("Spotify API keys not set. Using example link.")
        st.write("🎵 Example playlist link")
except ModuleNotFoundError:
    st.error("spotipy not installed. Check requirements.txt!")

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
