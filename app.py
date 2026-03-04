import streamlit as st
import random
import socketio
import threading
from flask import Flask

# THE BRAIN: This ensures "Books" get "Book details" and "Cars" get "Car details"
NICHE_MAP = {
    "book": {
        "details": ["hardcover first edition", "signed collector's", "illustrated"],
        "context": ["with original dust jacket", "from an independent bookstore"],
        "template": "Looking for a {adj} {item} {extra} in {loc}"
    },
    "diy": {
        "details": ["advanced STEM", "eco-friendly", "woodworking"],
        "context": ["with step-by-step guides", "complete starter kit"],
        "template": "Best {adj} {item} {extra} near {loc}"
    },
    "default": {
        "details": ["top-rated", "premium quality", "2026 version"],
        "context": ["with fast shipping", "best price"],
        "template": "Sourcing {adj} {item} {extra} available in {loc}"
    }
}

# SOCKET SERVER: To talk to your "Freddy", "Zaky", and "Work" profiles
sio = socketio.Server(cors_allowed_origins="*")
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

def run_socket():
    # We use port 5001 to avoid Streamlit conflicts
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5001)), app)

if 'socket_thread' not in st.session_state:
    threading.Thread(target=run_socket, daemon=True).start()
    st.session_state['socket_thread'] = True

# UI
st.title("Profile Search Broadcaster")
location = st.text_input("Target Location", "Sydney, NSW")
pasted_data = st.text_area("Paste your list here:")

if st.button("Push to All Profiles"):
    lines = pasted_data.split('\n')
    for line in lines:
        if line.strip():
            # Logic to pick the right niche
            niche = "book" if "book" in line.lower() else ("diy" if "diy" in line.lower() else "default")
            config = NICHE_MAP[niche]
            
            # Generate the "Natural" query
            query = config["template"].format(
                adj=random.choice(config["details"]),
                item=line.strip(),
                extra=random.choice(config["context"]),
                loc=location
            )
            
            # BROADCAST to all connected profiles
            sio.emit('new_search', {'query': query})
            st.success(f"Sent: {query}")
