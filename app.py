import streamlit as st
import random
import threading
import socketio
from flask import Flask
from transformers import pipeline

# 1. AI MODEL SETUP
@st.cache_resource
def load_ai_brain():
    # Using t5-small as it fits within Streamlit's 1GB RAM limit
    return pipeline("text-generation", model="t5-small")

rewriter = load_ai_brain()

# 2. SOCKET.IO SERVER SETUP
sio = socketio.Server(cors_allowed_origins="*")
flask_app = Flask(__name__)
flask_app.wsgi_app = socketio.WSGIApp(sio, flask_app.wsgi_app)

def run_socket_server():
    import eventlet
    # Extensions connect to 5001; Streamlit UI is on 8501
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5001)), flask_app)

if 'socket_started' not in st.session_state:
    threading.Thread(target=run_socket_server, daemon=True).start()
    st.session_state['socket_started'] = True

# 3. ADVANCED HUMANIZER LOGIC
def generate_natural_query(robotic_text):
    # Step A: Aggressive cleaning of robotic instructions
    clean = robotic_text.lower()
    fillers = [
        "search on bing to find", "search on bing for", "search on bing to",
        "items on your shopping list", "deals and reviews for your next",
        "for your needs", "in your area", "near you", "explore deals on", "compare"
    ]
    for f in fillers:
        clean = clean.replace(f, "")
    subject = clean.strip()

    # Step B: AI Generation with Anti-Looping parameters
    prompt = f"rewrite: {subject}"
    
    results = rewriter(
        prompt, 
        max_new_tokens=40, 
        do_sample=True, 
        temperature=0.8,      # Adds human-like variety
        top_p=0.95,
        repetition_penalty=2.5, # PREVENTS "rates and rates and rates"
        no_repeat_ngram_size=2  # Prevents any 2-word phrase from repeating
    )
    
    generated = results[0]['generated_text'].strip()
    
    # Step C: Cleanup and Fallback
    # Remove the prompt if the model echoed it back
    if prompt in generated:
        generated = generated.replace(prompt, "").strip()
    
    # If the output is too short or just repeated the input, use a Natural Template
    if len(generated) < 5 or generated.lower() == subject:
        templates = [
            f"Where can I buy {subject} online?",
            f"Best rated {subject} for 2026",
            f"Reviews and prices for {subject}",
            f"Top 10 {subject} recommendations"
        ]
        return random.choice(templates)
        
    return generated

# 4. STREAMLIT UI
st.set_page_config(page_title="AI Search Broadcaster", page_icon="🌿")
st.title("🌿 AI Natural Broadcaster (Anti-Loop)")
st.info("This version prevents repetitive 'hallucinations' and strips robotic instructions.")

pasted_list = st.text_area("Paste your robotic 16 queries here:", height=300)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        for line in lines:
            natural_query = generate_natural_query(line)
            
            # Broadcast to Freddy, Zaky, and others
            sio.emit('new_search', {'query': natural_query})
            
            st.success(f"**Broadcasted:** {natural_query}")
    else:
        st.warning("Please paste your list first.")
