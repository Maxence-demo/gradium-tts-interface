# Gradium TTS Interface

Interface Streamlit pour interagir avec l'API [Gradium.ai](https://gradium.ai) (Text-to-Speech).

## Fonctionnalités

- **Recherche et filtrage de voix** par nom, langue, pays (catalogue + voix custom)
- **Synthèse vocale (TTS)** avec paramètres ajustables (vitesse, température, similarité voix)
- **Formats de sortie** : WAV, PCM, Opus, ulaw, alaw
- **Lecteur audio intégré** + téléchargement des fichiers générés
- **Historique de session** des audios générés
- **Authentification** par login/mot de passe

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Créer le fichier `.streamlit/secrets.toml` :

```toml
GRADIUM_API_KEY = "gd_your_api_key_here"

[users]
admin = "your_password"
```

> Sur Streamlit Cloud, coller ce contenu dans **Settings > Secrets**.

## Lancement

```bash
streamlit run app.py
```

## Structure

```
├── app.py                # Interface Streamlit
├── gradium_client.py     # Wrapper synchrone du SDK Gradium
├── requirements.txt
├── .streamlit/
│   └── secrets.toml      # Secrets (non commité)
└── .gitignore
```
