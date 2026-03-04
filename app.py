import streamlit as st
import random
import threading
import socketio
from flask import Flask
from transformers import pipeline

# 1. AI MODEL SETUP (Cached so it only loads once)
@st.cache_resource
def load_ai_brain():
    # This model is specifically trained to paraphrase robotic text into natural speech
    return pipeline("text2text-generation", model="Vamsi/T5_Paraphrase_Puzzler")

rewriter = load_ai_brain()

# 2. SOCKET.IO SERVER SETUP
sio = socketio.Server(cors_allowed_origins="*")
flask_app = Flask(__name__)
flask_app.wsgi_app = socketio.WSGIApp(sio, flask_app.wsgi_app)

def run_socket_server():
    import eventlet
    # Port 5001 is used to avoid conflict with Streamlit's port 8501
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5001)), flask_app)

if 'socket_started' not in st.session_state:
    threading.Thread(target=run_socket_server, daemon=True).start()
    st.session_state['socket_started'] = True

# 3. THE "HUMANIZER" LOGIC
def generate_natural_query(robotic_text):
    # Strip the "Search on Bing" noise before feeding to AI
    clean = robotic_text.lower().replace("search on bing to", "").replace("search on bing for", "").strip()
    
    # AI Inference
    results = rewriter(
        f"paraphrase: {clean}", 
        max_length=50, 
        do_sample=True, 
        top_p=0.95
    )
    return results[0]['generated_text']

# 4. STREAMLIT UI
st.set_page_config(page_title="AI Natural Broadcaster", page_icon="🌿")
st.title("🌿 AI Natural Search Broadcaster")
st.markdown("Automates your daily task list into human-like search queries across all profiles.")

pasted_list = st.text_area("Paste your robotic 16 queries here:", height=300)

if st.button("🚀 Humanize & Broadcast to Profiles"):
    lines = pasted_list.split('\n')
    valid_lines = [l.strip() for l in lines if l.strip()]
    
    if valid_lines:
        progress_bar = st.progress(0)
        for i, line in enumerate(valid_lines):
            # Generate the natural version
            natural_query = generate_natural_query(line)
            
            # Broadcast to all connected Chrome Profiles (Freddy, Zaky, etc.)
            sio.emit('new_search', {'query': natural_query})
            
            # Show success in UI
            st.success(f"**Sent:** {natural_query}")
            progress_bar.progress((i + 1) / len(valid_lines))
    else:
        st.warning("Please paste a list first.")
