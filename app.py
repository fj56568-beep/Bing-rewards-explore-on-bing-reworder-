import streamlit as st
import random

# 1. MULTI-PART INTENT CONFIG
# We map each category to a structure that addresses ALL parts of the prompt.
MULTI_INTENT_CONFIG = {
    "charity": {
        "subjects": ["local animal shelters", "children's hospitals", "food banks"],
        "actions": ["online donation portals", "volunteer opportunities", "tax-deductible gifting"]
    },
    "glass": {
        "subjects": ["prescription eyeglasses and daily contacts", "blue-light glasses and lens kits"],
        "deals": ["buy one get one free offers", "20% off bundles", "student discounts"]
    },
    "internet": {
        "subjects": ["NBN fiber and 5G home internet"],
        "actions": ["compare speed tiers", "check connection deals", "view contract-free plans"]
    },
    "phone": {
        "subjects": ["latest 5G smartphones and mobile data plans"],
        "actions": ["compare trade-in deals", "find unlimited data bundles"]
    }
}

def generate_natural_query(robotic_text):
    text = robotic_text.lower()
    
    # CASE 1: Charities and Ways to Donate
    if "charity" in text or "donate" in text:
        config = MULTI_INTENT_CONFIG["charity"]
        return f"How to support {random.choice(config['subjects'])} and {random.choice(config['actions'])}."

    # CASE 2: Eyeglasses, Contacts, and Deals
    if "eyeglasses" in text or "contacts" in text:
        config = MULTI_INTENT_CONFIG["glass"]
        return f"Where to find {random.choice(config['subjects'])} with {random.choice(config['deals'])}."

    # CASE 3: Cell Phones, Plans, and Deals
    if "cell phone" in text or "plan" in text:
        config = MULTI_INTENT_CONFIG["phone"]
        return f"Best {random.choice(config['subjects'])} and {random.choice(config['actions'])}."

    # DEFAULT FALLBACK (for other categories)
    clean_subject = text.replace("search on bing to find", "").replace("search on bing for", "").strip()
    return f"Looking for {clean_subject} with reviews and current deals."

# --- UI Logic ---
st.title("🌿 Full-Intent Natural Broadcaster")
pasted_list = st.text_area("Paste your 16 robotic queries here:")

if st.button("🚀 Humanize & Broadcast"):
    for line in pasted_list.split('\n'):
        if line.strip():
            query = generate_natural_query(line)
            st.success(f"**Broadcasted:** {query}")
