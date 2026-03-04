import streamlit as st
import random
import threading
import socketio
from flask import Flask
from transformers import pipeline

# 1. AI MODEL SETUP (Updated for Transformers v5 compatibility)
@st.cache_resource
def load_ai_brain():
    # In Transformers v5, use "text-generation" instead of "text2text-generation"
    return pipeline("text-generation", model="t5-small")

rewriter = load_ai_brain()

# 2. SOCKET.IO SERVER SETUP
sio = socketio.Server(cors_allowed_origins="*")
flask_app = Flask(__name__)
flask_app.wsgi_app = socketio.WSGIApp(sio, flask_app.wsgi_app)

def run_socket_server():
    import eventlet
    # Streamlit Cloud uses port 8501, we use 5001 for the extension
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5001)), flask_app)

if 'socket_started' not in st.session_state:
    threading.Thread(target=run_socket_server, daemon=True).start()
    st.session_state['socket_started'] = True

# 3. THE "HUMANIZER" LOGIC
def generate_natural_query(robotic_text):
    # Strip the "Search on Bing" noise
    clean = robotic_text.lower()
    fillers = ["search on bing to find", "search on bing for", "search on bing to"]
    for f in fillers:
        clean = clean.replace(f, "")
    clean = clean.strip()
    
    # T5 still expects the "paraphrase: " prefix to know what to do
    prompt = f"paraphrase: {clean}"
    
    # Generate the result
    results = rewriter(
        prompt, 
        max_new_tokens=50, 
        do_sample=True, 
        temperature=0.7
    )
    
    # Extract the text (v5 pipelines often return a list with a dictionary)
    generated = results[0]['generated_text']
    
    # If the model repeats the prompt, we strip it out
    if prompt in generated:
        generated = generated.replace(prompt, "").strip()
        
    return generated

# 4. STREAMLIT UI
st.set_page_config(page_title="v5 Natural Broadcaster", page_icon="🌿")
st.title("🌿 v5 AI Natural Broadcaster")

pasted_list = st.text_area("Paste your robotic queries here:", height=300)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        for line in lines:
            natural_query = generate_natural_query(line)
            
            # Broadcast to your 7+ profiles
            sio.emit('new_search', {'query': natural_query})
            
            st.success(f"**Broadcasted:** {natural_query}")
    else:
        st.warning("Please paste a list first.")
