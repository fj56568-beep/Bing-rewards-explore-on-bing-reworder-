import streamlit as st
import random
import threading
import socketio
from flask import Flask
from transformers import pipeline

# 1. AI MODEL SETUP
@st.cache_resource
def load_ai_brain():
    return pipeline("text-generation", model="t5-small")

rewriter = load_ai_brain()

# 2. NICHE KNOWLEDGE BASE (This makes it specific!)
NICHE_DATA = {
    "book": {"items": ["science fiction novels", "hardcover memoirs", "biographies"], "jargon": ["first edition", "signed copy", "top-rated"]},
    "insurance": {"items": ["health coverage", "life insurance", "car insurance"], "jargon": ["low deductible", "PPO plans", "comprehensive"]},
    "car": {"items": ["electric vehicles", "SUV models", "used sedans"], "jargon": ["low mileage", "certified pre-owned", "fuel efficient"]},
    "movie": {"items": ["Inception", "The Matrix", "Interstellar", "Dune"], "jargon": ["4K HDR", "Director's cut", "streaming online"]},
    "internet": {"items": ["fiber optic plans", "5G home internet", "broadband"], "jargon": ["no contract", "unlimited data", "high speed"]},
    "credit": {"items": ["cashback cards", "travel reward cards"], "jargon": ["0% APR", "no annual fee", "sign-up bonus"]},
    "phone": {"items": ["unlocked smartphones", "5G mobile plans"], "jargon": ["trade-in deals", "latest models", "unlimited talk and text"]},
    "clothing": {"items": ["sustainable fashion", "winter jackets", "designer sneakers"], "jargon": ["clearance sale", "free returns", "new arrivals"]},
    "home": {"items": ["smart home kits", "kitchen renovation tools"], "jargon": ["DIY friendly", "contractor grade", "energy efficient"]}
}

# 3. ADVANCED HYBRID LOGIC
def generate_natural_query(robotic_text):
    text = robotic_text.lower()
    
    # Step A: Identify the Niche and Inject Specifics
    subject = "items"
    for niche, data in NICHE_DATA.items():
        if niche in text:
            item = random.choice(data["items"])
            detail = random.choice(data["jargon"])
            subject = f"{detail} {item}"
            break
    
    # If no niche matches, we just strip the "Search on Bing" part
    if subject == "items":
        subject = text.replace("search on bing to find", "").replace("search on bing for", "").strip()

    # Step B: AI Rewrite for Natural Flow
    prompt = f"rewrite: {subject}"
    results = rewriter(
        prompt, 
        max_new_tokens=30, 
        do_sample=True, 
        temperature=0.9, 
        repetition_penalty=2.5
    )
    
    generated = results[0]['generated_text'].strip().replace(prompt, "").strip()
    
    # Step C: Final Human Formatting
    starters = ["Looking for", "Where is the best place to find", "I need to compare", "Show me reviews for"]
    return f"{random.choice(starters)} {generated if len(generated) > 3 else subject}."

# 4. SERVER & UI (Keep your existing Socket.io logic here)
# ... [Same Socket.io/Flask code as previous version] ...

st.title("🌿 Hybrid Intent Broadcaster")
pasted_list = st.text_area("Paste your 16 robotic queries here:", height=300)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    for line in lines:
        natural_query = generate_natural_query(line)
        # sio.emit('new_search', {'query': natural_query})
        st.success(f"**Broadcasted:** {natural_query}")
