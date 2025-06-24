import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def video_page():
    user = st.session_state.get("user")
    if not user:
        st.warning("Connecte-toi pour voir les vidéos.")
        return

    video_id = st.query_params.get("video_id", None)
    if isinstance(video_id, list):
        video_id = video_id[0]

    if not video_id:
        st.error("Aucune vidéo sélectionnée.")
        return

    # Récupération des données vidéo
    response = supabase.table("videos").select("*").eq("id", video_id).single().execute()
    video_data = response.data
    if not video_data:
        st.error("Vidéo introuvable.")
        return

    title = video_data["title"]
    video_url = video_data["video_url"]
    uploader_id = video_data["uploader"]
    uploaded_at = (datetime.fromisoformat(video_data["uploaded_at"]) + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M")

    # Vérifie si l'utilisateur a déjà liké la vidéo
    like_data = supabase.table("likes") \
        .select("*") \
        .eq("video_id", video_id) \
        .eq("user_id", user.id) \
        .execute().data

    has_liked = len(like_data) > 0

    # Nombre de likes
    likes_count = supabase.table("likes").select("user_id", count="exact").eq("video_id", video_id).execute().count or 0

    # Affichage
    st.title(title)

    st.markdown(f"""
        <div style="
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 10px;
            background-color: #000;">
            <video src="{video_url}" controls
                   style="
                   position: absolute;
                   top: 0;
                   left: 0;
                   width: 100%;
                   height: 100%;
                   object-fit: contain;
                   border-radius: 10px;
                   background-color: black;">
            </video>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("##")

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"👍 **{likes_count}** likes")
    col2.markdown(f"📅 Publiée le {uploaded_at}")

    uploader_data = supabase.table("users").select("username").eq("id", uploader_id).single().execute()
    uploader_username = uploader_data.data["username"] if uploader_data.data else "Inconnu"
    col3.markdown(f"🎥 Par **{uploader_username}**")

    # --- Bouton S'abonner/Se désabonner sous le nom de l'uploader ---
    if uploader_id != user.id:
        already_subscribed = supabase.table("subscriptions") \
            .select("*") \
            .eq("subscriber_id", user.id) \
            .eq("subscribed_to_id", uploader_id) \
            .execute().data

        if already_subscribed:
            if st.button(f"❌ Se désabonner de {uploader_username}"):
                supabase.table("subscriptions") \
                    .delete() \
                    .eq("subscriber_id", user.id) \
                    .eq("subscribed_to_id", uploader_id) \
                    .execute()
                st.success(f"Désabonné de {uploader_username}")
                st.rerun()
        else:
            if st.button(f"🔔 S’abonner à {uploader_username}"):
                supabase.table("subscriptions").insert({
                    "subscriber_id": user.id,
                    "subscribed_to_id": uploader_id
                }).execute()
                st.success(f"Abonné à {uploader_username}")
                st.rerun()

    # Bouton Like
    if has_liked:
        if st.button("👎 Retirer le like"):
            supabase.table("likes").delete().eq("video_id", video_id).eq("user_id", user.id).execute()
            st.success("Like retiré.")
            st.rerun()
    else:
        if st.button("👍 Liker"):
            supabase.table("likes").insert({
                "video_id": video_id,
                "user_id": user.id
            }).execute()
            st.success("Vidéo likée.")
            st.rerun()

    # Bouton vers la chaîne
    if st.button("📺 Voir la chaîne", use_container_width=True):
        st.query_params.clear()
        st.query_params["page"] = "profile"
        st.query_params["user_id"] = uploader_id
        st.rerun()

    st.markdown("---")

    # Commentaires
    st.subheader("💬 Commentaires")
    comments_response = supabase.table("comments") \
        .select("*") \
        .eq("video_id", video_id) \
        .order("created_at", desc=False) \
        .execute()

    if comments_response.data:
        for comment in comments_response.data:
            pseudo = comment.get("pseudo", "Anonyme")
            text = comment.get("comment_text", "")
            date = (datetime.fromisoformat(comment["created_at"]) + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M")
            st.markdown(f"**{pseudo}** le {date}  \n{text}")
            st.markdown("---")
    else:
        st.info("Aucun commentaire pour le moment.")

    st.markdown("### Ajouter un commentaire")
    new_comment = st.text_area("Ton commentaire", max_chars=500)
    if st.button("Envoyer le commentaire"):
        if new_comment.strip():
            supabase.table("comments").insert({
                "video_id": video_id,
                "user_id": user.id,
                "pseudo": st.session_state.get("user_username", "Anonyme"),
                "comment_text": new_comment,
            }).execute()
            st.success("Commentaire publié avec succès.")
            st.rerun()
        else:
            st.warning("Le commentaire ne peut pas être vide.")
