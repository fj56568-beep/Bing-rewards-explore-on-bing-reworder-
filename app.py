import streamlit as st
import random
import socketio
import eventlet
import threading

# 1. THE HIGH-SPECIFICITY DICTIONARY (Your "Training" Data)
# We organize fragments by niche to ensure the queries stay data-driven and natural.
NICHE_DATA = {
    "book": {
        "adjectives": ["hardcover first edition", "signed collector's", "limited print", "illustrated"],
        "specs": ["with original dust jacket", "printed on acid-free paper", "from an independent publisher"],
        "structure": "I'm looking for a {adj} copy of a {item} {spec} available near {location}."
    },
    "diy": {
        "adjectives": ["advanced STEM", "eco-friendly beginner", "professional-grade woodworking", "high-quality"],
        "specs": ["with a complete tool-kit included", "featuring step-by-step video guides", "using non-toxic materials"],
        "structure": "Where can I source {adj} {item} {spec} for a home project in {location}?"
    },
    "insurance": {
        "adjectives": ["comprehensive PPO", "high-limit liability", "low-deductible", "customizable"],
        "specs": ["with zero out-of-pocket maximums", "including 2026 wellness benefits", "with multi-policy discounts"],
        "structure": "Compare the best {adj} {item} plans {spec} specifically for residents in {location}."
    },
    "cars": {
        "adjectives": ["certified pre-owned", "fuel-efficient hybrid", "low-mileage", "fully loaded"],
        "specs": ["with a clean CARFAX report", "including a manufacturer extended warranty", "featuring the latest safety tech"],
        "structure": "Find deals on {adj} {item} models {spec} within 50 miles of {location}."
    },
    "shopping": {
        "adjectives": ["heavy-duty", "ergonomic", "highly-rated", "top-tier"],
        "specs": ["with free express shipping", "at the lowest price point for 2026", "with a lifetime satisfaction guarantee"],
        "structure": "Sourcing {adj} {item} {spec} with fast delivery to {location}."
    }
}

# 2. KEYWORD EXTRACTION & GENERATION LOGIC
def generate_specific_query(pasted_line, location):
    # Mapping words found in your list to our dictionary keys
    mapping = {
        "book": "book",
        "diy": "diy",
        "kit": "diy",
        "craft": "diy",
        "insurance": "insurance",
        "car": "cars",
        "auto": "cars",
        "item": "shopping",
        "shopping": "shopping"
    }
    
    # Identify subject
    category_key = "shopping" # Default
    for word, cat in mapping.items():
        if word in pasted_line.lower():
            category_key = cat
            break
            
    niche = NICHE_DATA.get(category_key)
    
    # Randomly assemble fragments
    return niche["structure"].format(
        adj=random.choice(niche["adjectives"]),
        item=category_key,
        spec=random.choice(niche["specs"]),
        location=location
    )

# 3. SOCKET.IO SERVER SETUP (To communicate with multiple browser profiles)
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

def run_socket_server():
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)

# Start server in a background thread so Streamlit can still run
if 'socket_started' not in st.session_state:
    threading.Thread(target=run_socket_server, daemon=True).start()
    st.session_state['socket_started'] = True

# 4. STREAMLIT UI
st.set_page_config(page_title="Smart Query Broadcaster", layout="wide")
st.title("🚀 Multi-Profile Query Broadcaster")

# Sidebar for global context injection
st.sidebar.header("Global Settings")
user_location = st.sidebar.text_input("My Location", value="Sydney, NSW")

# Input Area
pasted_list = st.text_area("Paste your Daily List here:", height=300, 
                           placeholder="Search for your next book...\nSearch for car deals...")

if st.button("Generate & Push to All Profiles"):
    lines = [line.strip() for line in pasted_list.split('\n') if line.strip()]
    
    if lines:
        results = []
        for line in lines:
            smart_query = generate_specific_query(line, user_location)
            results.append(smart_query)
            st.success(f"**Broadcasted:** {smart_query}")
        
        # BROADCAST: Sending data to all connected browser profiles
        sio.emit('new_query_batch', {'queries': results})
    else:
        st.warning("Please paste a list first.")
