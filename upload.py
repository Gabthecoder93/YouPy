import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import uuid
import tempfile

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_video():
    user = st.session_state.get("user")
    user_id = user.id if user else None
    username = st.session_state.get("user_username", "inconnu")

    if not user:
        st.warning("Connecte-toi pour uploader une vidéo.")
        return

    st.title("📤 Uploader une vidéo")

    title = st.text_input("Titre de la vidéo")
    uploaded_file = st.file_uploader("Choisis une vidéo", type=["mp4", "mov", "avi"])

    if st.button("📤 Uploader"):
        if not uploaded_file or not title:
            st.warning("Remplis tous les champs.")
            return

        try:
            st.info("📦 Préparation de l’upload...")

            # Chemin dans le bucket
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}.mp4"
            path_in_bucket = f"videos/{filename}"

            # Sauvegarde temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            st.info("🚀 Envoi de la vidéo...")

            # Upload vers Supabase
            supabase.storage.from_("videos").upload(path_in_bucket, tmp_path)

            # Supprimer fichier local
            os.remove(tmp_path)

            # Génération URL publique
            public_url = supabase.storage.from_("videos").get_public_url(path_in_bucket)

            # Insertion dans table
            supabase.table("videos").insert({
                "id": unique_id,
                "title": title,
                "video_url": public_url,
                "uploader": user_id,
                "uploaded_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            st.success("✅ Vidéo uploadée avec succès !")

        except Exception as e:
            st.error(f"Erreur pendant l'upload : {e}")
