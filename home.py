import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def home():
    st.title("🏠 Accueil ")

    try:
        response = supabase.table("videos") \
            .select("id, title, uploaded_at") \
            .order("uploaded_at", desc=True) \
            .execute()
        videos = response.data
    except Exception as e:
        st.error(f"Erreur chargement des vidéos : {e}")
        return

    if not videos:
        st.info("Aucune vidéo disponible.")
        return

    st.markdown("""
        <style>
        .vignette-button {
            background-color: #1D9BF0;
            color: white;
            height: 180px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            overflow: hidden;
            padding: 10px;
            white-space: normal;
            word-wrap: break-word;
            text-align: center;
        }
        div[data-testid="column"] > div > button {
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for index, video in enumerate(videos):
        col = cols[index % 4]
        with col:
            if st.button(video["title"], key=video["id"]):
                st.query_params.clear()
                st.query_params["page"] = "video"
                st.query_params["video_id"] = video["id"]
                st.rerun()
