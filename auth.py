import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_page():
    st.title("🔐 Connexion")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if not username or not password:
            st.warning("Remplis tous les champs.")
            return

        # Étape 1 : récupérer l’email via la table `users`
        try:
            user_lookup = supabase.table("users") \
                .select("email") \
                .eq("username", username) \
                .single() \
                .execute()
            
            if not user_lookup.data:
                st.error("Nom d'utilisateur inconnu.")
                return

            email = user_lookup.data["email"]

        except Exception as e:
            st.error(f"Erreur lors de la recherche du compte : {e}")
            return

        # Étape 2 : connexion via Supabase
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if response.user:
                st.session_state["user"] = response.user
                st.session_state["user_username"] = username
                st.success("Connexion réussie.")
                st.session_state["page"] = "home"
                st.rerun()
            else:
                st.error("Connexion échouée.")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")



def register_page():
    st.title("📝 Inscription")

    username = st.text_input("Nom d'utilisateur")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("S'inscrire"):
        if not username or not email or not password:
            st.warning("Tous les champs sont obligatoires.")
            return

        try:
            # Étape 1 : créer compte dans Supabase Auth
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            user = response.user
            if not user:
                st.error("Erreur lors de l’inscription.")
                return

            user_id = user.id

            # Étape 2 : insérer l’utilisateur dans la table `users`
            supabase.table("users").insert({
                "id": user_id,
                "username": username,
                "email": email,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            st.success("Inscription réussie. Tu peux te connecter.")
            st.session_state["page"] = "login"

        except Exception as e:
            st.error(f"Erreur lors de l’inscription : {e}")


def logout():
    st.session_state["user"] = None
    st.session_state["user_username"] = ""
    st.session_state["selected_video_id"] = None
    st.session_state["page"] = "login"
    st.success("Déconnecté avec succès.")
