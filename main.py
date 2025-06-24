import streamlit as st
import os
import json
from dotenv import load_dotenv
from supabase import create_client
from auth import login_page, register_page, logout
from home import home
from video_page import video_page
from upload import upload_video
from profile_page import profile_page


# --- Configuration Streamlit
st.set_page_config(page_title="Youpy Web", layout="wide")

# --- Connexion Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Session state init
if "user" not in st.session_state:
    st.session_state["user"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "user_username" not in st.session_state:
    st.session_state["user_username"] = ""
if "selected_video_id" not in st.session_state:
    st.session_state["selected_video_id"] = None

# --- Session restore
def try_restore_session():
    if os.path.exists("session.json"):
        try:
            with open("session.json", "r") as f:
                token = json.load(f)["refresh_token"]
            session = supabase.auth.refresh_session(token)
            if session.user:
                st.session_state["user"] = session.user
                user_data = supabase.table("users") \
                    .select("username") \
                    .eq("id", session.user.id) \
                    .single().execute().data
                st.session_state["user_username"] = user_data["username"]
                return True
        except Exception as e:
            print(f"[Session] Erreur de restauration : {e}")
    return False

# 🧠 Tentative de restauration si déconnecté
if st.session_state["user"] is None:
    try_restore_session()

# --- Récupération des paramètres de l’URL
params = st.query_params
if "page" in params and st.session_state["user"]:
    st.session_state["page"] = params["page"]
if "video_id" in params:
    st.session_state["selected_video_id"] = params["video_id"]

# --- Barre latérale
st.sidebar.title("YouPy 🎬")
if st.session_state["user"]:
    st.sidebar.success(f"Connecté : {st.session_state['user_username']}")

    if st.sidebar.button("🏠 Accueil"):
        st.session_state["page"] = "home"
        st.query_params.clear()

    if st.sidebar.button("📤 Upload vidéo"):
        st.session_state["page"] = "upload"
        st.query_params.clear()

    if st.sidebar.button("👤 Profil"):
        st.query_params.clear()
        st.query_params["page"] = "profile"
        st.query_params["user_id"] = st.session_state["user"].id
        st.rerun()



    if st.sidebar.button("🚪 Déconnexion"):
        logout()
        st.query_params.clear()
else:
    if st.sidebar.button("🔐 Connexion"):
        st.session_state["page"] = "login"
    if st.sidebar.button("📝 Inscription"):
        st.session_state["page"] = "register"

# --- Navigation
if st.session_state["user"]:
    page = st.session_state["page"]
    if page == "home":
        home()
    elif page == "upload":
        upload_video()
    elif st.session_state["page"] == "profile":
        profile_page()

    elif page == "video":
        video_page()
    else:
        st.warning("Page inconnue.")
else:
    if st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "register":
        register_page()
