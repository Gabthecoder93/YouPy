import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def profile_page():
    user = st.session_state.get("user")
    current_user_id = user.id if user else None

    query_params = st.query_params
    profile_id = query_params.get("user_id", None)
    if isinstance(profile_id, list):
        profile_id = profile_id[0]

    if not profile_id:
        st.error("Aucun utilisateur sélectionné.")
        return

    # Infos utilisateur
    user_res = supabase.table("users").select("username").eq("id", profile_id).single().execute()
    user_data = user_res.data
    if not user_data:
        st.error("Utilisateur introuvable.")
        return

    username = user_data["username"]
    st.title(f"Chaîne de {username}")

    # Nombre d’abonnés
    sub_res = supabase.table("subscriptions").select("subscriber_id", count="exact") \
        .eq("subscribed_to_id", profile_id).execute()
    nb_abonnés = sub_res.count or 0
    st.markdown(f"👥 **{nb_abonnés} abonnés**")

    # Bouton s’abonner
    if current_user_id and current_user_id != profile_id:
        already = supabase.table("subscriptions") \
            .select("*") \
            .eq("subscriber_id", current_user_id) \
            .eq("subscribed_to_id", profile_id).execute().data

        if already:
            if st.button("❌ Se désabonner"):
                supabase.table("subscriptions") \
                    .delete().eq("subscriber_id", current_user_id) \
                    .eq("subscribed_to_id", profile_id).execute()
                st.success("Désabonné.")
                st.rerun()
        else:
            if st.button("🔔 S’abonner"):
                supabase.table("subscriptions").insert({
                    "subscriber_id": current_user_id,
                    "subscribed_to_id": profile_id
                }).execute()
                st.success("Abonné avec succès.")
                st.rerun()

    st.markdown("---")
    st.subheader("📹 Vidéos publiées")

    vids = supabase.table("videos").select("id, title, uploaded_at") \
        .eq("uploader", profile_id).order("uploaded_at", desc=True).execute().data

    if not vids:
        st.info("Aucune vidéo publiée.")
        return

    cols = st.columns(4)
    for i, video in enumerate(vids):
        with cols[i % 4]:
            if st.button(video["title"], key=video["id"]):
                st.query_params.clear()
                st.query_params["page"] = "video"
                st.query_params["video_id"] = video["id"]
                st.rerun()
