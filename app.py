import streamlit as st
import random
import socketio
import threading
from flask import Flask

# 1. THE HUMAN-LIKE LOGIC ENGINE
# Each category has its own unique sentence structures and jargon
NICHE_MAP = {
    "book": {
        "templates": [
            "I'm trying to find a {adj} copy of {item} {extra} in {loc}.",
            "Where can I buy a {adj} {item} {extra} near {loc}?",
            "Looking for recommendations for a {adj} {item} around {loc}."
        ],
        "details": ["hardcover first edition", "signed collector's", "well-preserved vintage"],
        "context": ["with the original dust jacket", "from a local independent seller"]
    },
    "diy": {
        "templates": [
            "What are the best {adj} {item} {extra} available in {loc}?",
            "I need to source {adj} {item} {extra} near {loc} for a weekend project.",
            "Looking for high-quality {adj} {item} in {loc}."
        ],
        "details": ["woodworking", "beginner STEM", "eco-friendly craft"],
        "context": ["starter kits", "supplies with fast local pickup"]
    },
    "insurance": {
        "templates": [
            "How do I compare {adj} {item} {extra} for residents in {loc}?",
            "Looking for {adj} {item} {extra} in {loc} with good reviews.",
            "What is the most affordable {adj} {item} currently available in {loc}?"
        ],
        "details": ["comprehensive life", "private health", "low-deductible car"],
        "context": ["with instant online quotes", "that covers pre-existing conditions"]
    },
    "default": {
        "templates": [
            "Where is the best place to find {item} in {loc}?",
            "Looking for {adj} {item} {extra} near {loc}.",
            "Does anyone know where to get {item} {extra} in {loc}?"
        ],
        "details": ["top-rated", "reliable", "affordable"],
        "context": ["at a good price", "with local delivery"]
    }
}

# 2. SOCKET SERVER SETUP (To communicate with Freddy, Zaky, etc.)
sio = socketio.Server(cors_allowed_origins="*")
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

def run_socket():
    import eventlet
    # Streamlit Cloud uses port 8501, so we run our socket server on 5001
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5001)), app)

if 'socket_thread' not in st.session_state:
    threading.Thread(target=run_socket, daemon=True).start()
    st.session_state['socket_thread'] = True

# 3. STREAMLIT UI
st.set_page_config(page_title="Natural Query Broadcaster", layout="wide")
st.title("🚀 Multi-Profile Natural Broadcaster")

st.sidebar.header("Settings")
location = st.sidebar.text_input("My Location", "Sydney, NSW")

pasted_data = st.text_area("Paste your search list here (one per line):", height=300)

if st.button("Generate & Push to All Profiles"):
    lines = pasted_data.split('\n')
    
    if any(line.strip() for line in lines):
        for line in lines:
            raw_text = line.strip()
            if not raw_text:
                continue
                
            # CLEANUP: Remove "Search on Bing for" if it exists in your pasted text
            clean_item = raw_text.lower().replace("search on bing for", "").replace("search on bing", "").strip()
            
            # CATEGORIZE: Match keywords to our niche data
            if "book" in clean_item:
                niche = "book"
            elif any(word in clean_item for word in ["diy", "kit", "craft", "woodworking"]):
                niche = "diy"
            elif any(word in clean_item for word in ["insurance", "plan", "policy"]):
                niche = "insurance"
            else:
                niche = "default"
            
            config = NICHE_MAP[niche]
            
            # BUILD: Assemble the natural human-like sentence
            query = random.choice(config["templates"]).format(
                adj=random.choice(config["details"]),
                item=clean_item,
                extra=random.choice(config["context"]),
                loc=location
            )
            
            # BROADCAST: Send to your 10+ browser profiles
            sio.emit('new_search', {'query': query})
            st.success(f"**Broadcasted:** {query}")
    else:
        st.warning("Please paste a list first.")
