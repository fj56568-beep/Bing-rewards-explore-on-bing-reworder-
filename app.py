import streamlit as st
import random
import threading
import socketio
from flask import Flask
from transformers import pipeline

# 1. AI MODEL SETUP (Using t5-small for memory efficiency)
@st.cache_resource
def load_ai_brain():
    # t5-small is the best balance of speed and size for Streamlit Cloud
    return pipeline("text2text-generation", model="t5-small")

rewriter = load_ai_brain()

# 2. SOCKET.IO SERVER SETUP
sio = socketio.Server(cors_allowed_origins="*")
flask_app = Flask(__name__)
flask_app.wsgi_app = socketio.WSGIApp(sio, flask_app.wsgi_app)

def run_socket_server():
    import eventlet
    # Streamlit uses 8501, we use 5001 for the Chrome Extensions
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5001)), flask_app)

if 'socket_started' not in st.session_state:
    threading.Thread(target=run_socket_server, daemon=True).start()
    st.session_state['socket_started'] = True

# 3. THE "HUMANIZER" LOGIC
def generate_natural_query(robotic_text):
    # STEP A: Strip the robotic shell
    clean = robotic_text.lower()
    fillers = ["search on bing to find", "search on bing for", "search on bing to"]
    for f in fillers:
        clean = clean.replace(f, "")
    clean = clean.strip()
    
    # STEP B: AI Rewrite
    # T5 expects "paraphrase: " as a prefix
    prompt = f"paraphrase: {clean}"
    results = rewriter(
        prompt, 
        max_length=50, 
        do_sample=True, 
        top_p=0.9, 
        temperature=0.7 # Higher = more "creative" variations
    )
    return results[0]['generated_text']

# 4. STREAMLIT UI
st.set_page_config(page_title="Natural Query Broadcaster", page_icon="🌿")
st.title("🌿 Natural AI Broadcaster")

pasted_list = st.text_area("Paste your 16 robotic queries here:", height=300)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        for line in lines:
            natural_query = generate_natural_query(line)
            
            # Send to Freddy, Zaky, and the other 5+ profiles
            sio.emit('new_search', {'query': natural_query})
            
            st.success(f"**Broadcasted:** {natural_query}")
    else:
        st.warning("Please paste a list first.")
