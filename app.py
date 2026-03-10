import hmac

import streamlit as st

st.set_page_config(page_title="Gradium TTS", page_icon="🎙️", layout="wide")


# --- Authentication ---
def check_credentials(username: str, password: str) -> bool:
    users = st.secrets.get("users", {})
    expected = users.get(username)
    if expected is None:
        return False
    return hmac.compare_digest(password, expected)


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Connexion")
    with st.form("login_form"):
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter", type="primary")
        if submitted:
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
    st.stop()

import gradium_client

# --- Load voices (cached) ---
@st.cache_data(show_spinner="Chargement des voix...")
def load_voices():
    return gradium_client.get_voices()


voices = load_voices()

# --- Sidebar ---
with st.sidebar:
    st.caption(f"Connecté : **{st.session_state.username}**")
    if st.button("🚪 Déconnexion"):
        st.session_state.authenticated = False
        st.session_state.pop("username", None)
        st.rerun()
    st.divider()
    st.header("Crédits")
    try:
        credits = gradium_client.get_credits()
        st.json(credits)
    except Exception as e:
        st.error(f"Erreur crédits : {e}")

    st.divider()
    st.header("Paramètres")

    output_format = st.selectbox(
        "Format de sortie",
        ["wav", "pcm", "opus", "ulaw_8000", "alaw_8000", "pcm_16000", "pcm_24000"],
    )
    padding_bonus = st.slider(
        "Padding bonus (vitesse)", -4.0, 4.0, 0.0, 0.1,
        help="Négatif = plus rapide, Positif = plus lent",
    )
    temp = st.slider(
        "Température", 0.0, 1.4, 0.7, 0.05,
        help="0 = déterministe, plus haut = plus varié",
    )
    cfg_coef = st.slider(
        "CFG coef (similarité voix)", 1.0, 4.0, 2.0, 0.1,
        help="Plus haut = plus proche de la voix originale",
    )

# --- Main area ---
st.title("Gradium TTS")

# Voice filtering
col_search, col_toggle = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Rechercher une voix (nom, langue, pays)")
with col_toggle:
    st.write("")
    st.write("")
    custom_only = st.toggle("Mes voix custom uniquement")

# Filter voices
filtered_voices = voices
if custom_only:
    filtered_voices = [v for v in filtered_voices if v.get("is_custom", False)]
if search_query:
    q = search_query.lower()
    filtered_voices = [
        v for v in filtered_voices
        if q in str(v.get("name", "")).lower()
        or q in str(v.get("language", "")).lower()
        or q in str(v.get("country", "")).lower()
        or q in str(v.get("description", "")).lower()
    ]

# Display voice table
if filtered_voices:
    display_data = [
        {
            "Nom": v.get("name", "N/A"),
            "Langue": v.get("language", "N/A"),
            "Pays": v.get("country", "N/A"),
            "ID": v.get("uid", v.get("voice_id", "N/A")),
            "Custom": "✅" if v.get("is_custom", False) else "",
        }
        for v in filtered_voices
    ]
    st.dataframe(display_data, use_container_width=True, hide_index=True)
else:
    st.info("Aucune voix trouvée.")

# Voice selection
voice_options = {
    f"{v.get('name', 'N/A')} ({v.get('language', '?')}) — {v.get('uid', v.get('voice_id', ''))}": v.get("uid", v.get("voice_id", ""))
    for v in filtered_voices
}

if voice_options:
    selected_label = st.selectbox("Sélectionner une voix", list(voice_options.keys()))
    selected_voice_id = voice_options[selected_label]
else:
    selected_voice_id = None
    st.warning("Aucune voix disponible pour la sélection.")

# Text input
text_input = st.text_area("Texte à synthétiser", height=150, placeholder="Entrez votre texte ici...")

# Generate button
if st.button("🎙️ Générer", type="primary", disabled=not (selected_voice_id and text_input)):
    with st.spinner("Génération en cours..."):
        try:
            audio_bytes = gradium_client.generate_tts(
                text=text_input,
                voice_id=selected_voice_id,
                output_format=output_format,
                padding_bonus=padding_bonus,
                temp=temp,
                cfg_coef=cfg_coef,
            )
            # Store in session state
            if "audio_history" not in st.session_state:
                st.session_state.audio_history = []
            st.session_state.audio_history.append({
                "audio": audio_bytes,
                "format": output_format,
                "voice": selected_label,
                "text": text_input[:80],
            })
            st.success("Audio généré !")
        except Exception as e:
            st.error(f"Erreur : {e}")

# Display audio history
if st.session_state.get("audio_history"):
    st.divider()
    st.subheader("Audios générés")
    for i, entry in enumerate(reversed(st.session_state.audio_history)):
        fmt = entry["format"]
        mime = "audio/wav" if fmt == "wav" else f"audio/{fmt}"
        with st.expander(f"🔊 {entry['voice']} — \"{entry['text']}...\"", expanded=(i == 0)):
            st.audio(entry["audio"], format=mime)
            st.download_button(
                "⬇️ Télécharger",
                data=entry["audio"],
                file_name=f"gradium_tts_{len(st.session_state.audio_history) - i}.{fmt}",
                mime=mime,
                key=f"download_{i}_{len(st.session_state.audio_history)}",
            )
