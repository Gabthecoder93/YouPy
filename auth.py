import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_page():
    st.title("🔐 Connexion ")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        try:
            # 🔍 Étape 1 : récupérer l'email depuis la table users
            user_data = supabase.table("users").select("id, username").eq("username", username).single().execute().data
            if not user_data:
                st.error("Nom d'utilisateur incorrect.")
                return

            user_id = user_data["id"]

            # 🔍 Étape 2 : récupérer l’email lié à cet ID via Supabase Auth
            auth_users = supabase.table("users").select("email").eq("id", user_id).single().execute()
            email = auth_users.data["email"]

            # 🔐 Étape 3 : connexion via email + mdp
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})

            if result.user:
                st.session_state["user"] = result.user
                st.session_state["user_username"] = username
                st.session_state["page"] = "home"
                st.success("Connecté avec succès.")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")


def register_page():
    st.title("📝 Inscription")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    username = st.text_input("Nom d'utilisateur")
    if st.button("S'inscrire"):
        try:
            result = supabase.auth.sign_up({"email": email, "password": password})
            if result.user:
                supabase.table("users").insert({
                    "id": result.user.id,
                    "username": username
                }).execute()
                st.success("Compte créé, connecte-toi maintenant.")
                st.session_state["page"] = "login"
        except Exception as e:
            st.error(f"Erreur d'inscription : {e}")

def logout():
    st.session_state["user"] = None
    st.session_state["user_username"] = ""
    st.session_state["selected_video_id"] = None
    st.session_state["page"] = "login"
    st.success("Déconnecté avec succès.")
