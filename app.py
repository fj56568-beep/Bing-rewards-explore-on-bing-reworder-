import streamlit as st
import random
import threading
import socketio
from flask import Flask

# 1. THE BRAIN: NICHE KNOWLEDGE BASE
# We define exactly what each robotic category should become.
INTENT_CONFIG = {
    "shopping": ["bulk pantry staples", "eco-friendly cleaning supplies", "organic kitchen essentials"],
    "book": ["signed first edition biographies", "hardcover science fiction bestsellers", "collectible leather-bound classics"],
    "diy": ["beginner-friendly resin art kits", "advanced woodworking tool sets", "premium tie-dye craft supplies"],
    "insurance": ["comprehensive PPO health plans", "low-deductible car insurance", "term life insurance quotes"],
    "car": ["certified pre-owned electric SUVs", "low-mileage luxury sedans", "fuel-efficient hybrid hatchbacks"],
    "credit": ["0% APR balance transfer cards", "travel rewards cards with no annual fee", "high-cashback credit cards"],
    "internet": ["high-speed NBN fiber plans", "unlimited 5G home broadband", "no-contract internet bundles"],
    "home": ["contractor-grade power tools", "smart home security camera systems", "energy-efficient kitchen appliances"],
    "flower": ["fresh peony bouquets with same-day delivery", "luxury long-stem roses", "seasonal native flower arrangements"],
    "concert": ["VIP floor tickets for upcoming tours", "last-minute concert seat deals", "indie music festival passes"],
    "cruise": ["all-inclusive Mediterranean cruise deals", "luxury Caribbean balcony suites", "last-minute river cruise packages"],
    "cloth": ["sustainable organic cotton hoodies", "designer winter trench coats", "premium athletic activewear"],
    "charity": ["top-rated local animal shelters", "reputable children's hospitals", "vetted environmental conservation funds"],
    "glass": ["blue-light blocking prescription glasses", "daily disposable contact lenses", "designer sunglasses with UV protection"],
    "phone": ["unlocked 5G smartphones", "prepaid mobile plans with unlimited data", "latest iPhone trade-in deals"],
    "movie": ["The Matrix 4K Blu-ray collection", "Interstellar IMAX streaming", "Dune Part Two director's cut"]
}

# 2. THE HUMANIZER ENGINE (Pure Python for Speed)
def generate_natural_query(robotic_text):
    text = robotic_text.lower()
    final_subject = None

    # Step A: Find the match and pick a specific human item
    for key, options in INTENT_CONFIG.items():
        if key in text:
            final_subject = random.choice(options)
            break
    
    # Step B: Fallback if no keyword is found
    if not final_subject:
        # Clean the robotic instruction shell
        final_subject = text.replace("search on bing to find", "").replace("search on bing for", "").strip()

    # Step C: Add a natural Human Starter
    starters = [
        "Where can I find {item}?",
        "Looking for {item} with good reviews.",
        "Compare the best {item} available now.",
        "I need to buy {item}.",
        "Show me deals for {item}."
    ]
    
    return random.choice(starters).format(item=final_subject)

# 3. UI AND BROADCASTER
st.title("🌿 High-Intent Natural Broadcaster")
st.markdown("This version uses a **Niche Intent Engine** to ensure 100% specificity without AI errors.")

pasted_list = st.text_area("Paste your 16 robotic queries here:", height=300)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    if lines:
        for line in lines:
            natural_query = generate_natural_query(line)
            # sio.emit('new_search', {'query': natural_query}) # Send to Freddy, Zaky, etc.
            st.success(f"**Broadcasted:** {natural_query}")
