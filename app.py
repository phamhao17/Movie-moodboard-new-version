import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from tmdbv3api import TMDb, Movie
import openai
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- CONFIG ---
st.set_page_config(page_title="Movie Moodboard", layout="wide")
st.title("🎬 Movie Moodboard – AI Movie Assistant")

# --- API KEYS ---
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

openai.api_key = OPENAI_API_KEY

# --- TMDB ---
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
tmdb.language = "en"
movie_api = Movie()

# --- Spotify ---
spotify_auth = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
)
spotify = spotipy.Spotify(auth_manager=spotify_auth)


# --- UI ---
uploaded_image = st.file_uploader("📤 Upload an image (optional)", type=["jpg", "png"])
description = st.text_area("📝 Or describe your scene:")
mood = st.selectbox("🎭 Mood", ["Happy", "Sad", "Romantic", "Suspenseful", "Action", "Mystery"])


# --- IMAGE UPLOAD SECTION ---
if uploaded_image:
    st.subheader("📷 Uploaded Image")
    img = Image.open(uploaded_image)
    st.image(img, use_column_width=True)


# --- TMDB POSTER SEARCH ---
if description:
    st.subheader("🎞 Movie Poster (TMDb)")

    try:
        results = movie_api.search(description)
        if results:
            poster_url = f"https://image.tmdb.org/t/p/w500{results[0].poster_path}"
            poster_img = Image.open(BytesIO(requests.get(poster_url).content))
            st.image(poster_img, caption=results[0].title, use_column_width=True)
        else:
            st.info("No matching poster found on TMDb.")
    except Exception as e:
        st.error(f"TMDb Error: {e}")


# --- OPENAI DALL·E ---
if uploaded_image or description:
    st.subheader("🎨 AI Concept Art (DALL·E 3)")

    try:
        prompt = f"Generate a cinematic concept art in {mood.lower()} style. Scene: {description}"

        res = openai.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
        )

        img_url = res.data[0].url
        ai_img = Image.open(BytesIO(requests.get(img_url).content))
        st.image(ai_img, caption="AI Concept Art", use_column_width=True)

    except Exception as e:
        st.error(f"OpenAI Error: {e}")


# --- SPOTIFY PLAYLIST ---
st.subheader("🎵 Suggested Playlist (Spotify)")

try:
    playlist_results = spotify.search(q=mood, type="playlist", limit=1)
    playlist = playlist_results["playlists"]["items"][0]
    st.markdown(f"**[{playlist['name']}]({playlist['external_urls']['spotify']})**")
except:
    st.info("No playlist found.")


# --- SIMILAR MOVIES ---
if description:
    st.subheader("🎬 Similar Movies")

    try:
        results = movie_api.search(description)
        for m in results[:5]:
            st.write(f"- {m.title} ({m.release_date})")
    except:
        st.info("No similar movies found.")
