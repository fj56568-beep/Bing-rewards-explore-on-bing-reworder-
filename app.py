import streamlit as st
import random
import socketio
import threading
from flask import Flask

# 1. SETUP FILLER CLEANER
FILLER_PHRASES = ["search on bing to find", "search on bing for", "deals and reviews for your next", "search for", "find deals and reviews", "to find", "looking for"]

def extract_core_subject(text):
    clean = text.lower()
    for phrase in FILLER_PHRASES:
        clean = clean.replace(phrase, "")
    clean = clean.replace("your next", "").replace("the best", "").strip()
    words = clean.split()
    return " ".join(words[-2:]) if len(words) > 4 else clean

# 2. NICHE CONFIG
NICHE_MAP = {
    "book": {
        "templates": ["I'm trying to find a {adj} copy of {item} {extra} in {loc}.", "Where can I buy a {adj} {item} {extra} near {loc}?"],
        "details": ["hardcover first edition", "signed collector's"],
        "context": ["with the original dust jacket", "from a local seller"]
    },
    "default": {
        "templates": ["Where is the best place to find {item} in {loc}?", "Looking for {adj} {item} {extra} near {loc}."],
        "details": ["top-rated", "reliable"],
        "context": ["at a good price", "with local delivery"]
    }
}

# 3. SOCKET SERVER
sio = socketio.Server(cors_allowed_origins="*")
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

def run_socket():
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5001)), app)

if 'socket_thread' not in st.session_state:
    threading.Thread(target=run_socket, daemon=True).start()
    st.session_state['socket_thread'] = True

# 4. UI AND LOGIC
st.title("🚀 Multi-Profile Natural Broadcaster")
location = st.sidebar.text_input("My Location", "Sydney, NSW")
pasted_data = st.text_area("Paste your search list here:", height=300)

if st.button("Generate & Push to All Profiles"):
    lines = pasted_data.split('\n')
    for line in lines:
        if line.strip():
            subject = extract_core_subject(line)
            niche = "book" if "book" in subject else "default"
            config = NICHE_MAP[niche]
            query = random.choice(config["templates"]).format(
                adj=random.choice(config["details"]),
                item=subject,
                extra=random.choice(config["context"]),
                loc=location
            )
            sio.emit('new_search', {'query': query})
            st.success(f"Broadcasted: {query}")
