import random
import streamlit as st

# 1. The Fragment Bank (Highly specific & technical)
QUERY_COMPONENTS = {
    "insurance": {
        "intents": ["Compare comprehensive", "Find high-limit", "Best rated", "Low-deductible"],
        "specs": ["PPO and HMO plans", "2026 wellness-focused coverage", "multi-policy bundles"],
        "qualifiers": ["with 24/7 telehealth support.", "for a family of four in {location}.", "with zero-dollar preventative care."]
    },
    "cars": {
        "intents": ["Locate certified pre-owned", "Compare financing for", "Best lease deals on", "Safety ratings for"],
        "specs": ["hybrid and electric models", "luxury sedans with under 20k miles", "AWD SUVs with towing packages"],
        "qualifiers": ["within 100 miles of {location}.", "including full CARFAX history.", "with a 5-star NHTSA safety rating."]
    },
    "default": {
        "intents": ["I'm looking for", "Where can I find", "Help me source", "Deep dive on"],
        "specs": ["professional-grade", "the highest rated", "energy-efficient", "bulk-buy"],
        "qualifiers": ["with fast delivery to {location}.", "according to 2026 consumer reports.", "with a manufacturer warranty."]
    }
}

# 2. The Logic to Detect Category & Build String
def build_natural_query(pasted_line, location):
    # Determine the category based on keywords in the line
    category = "default"
    for key in QUERY_COMPONENTS.keys():
        if key in pasted_line.lower():
            category = key
            break
            
    bank = QUERY_COMPONENTS[category]
    
    # Randomly assemble the "Smart" query
    intent = random.choice(bank["intents"])
    spec = random.choice(bank["specs"])
    qualifier = random.choice(bank["qualifiers"])
    
    # Final assembly with variable injection
    raw_query = f"{intent} {spec} {qualifier}"
    return raw_query.format(location=location)

# 3. Streamlit Interface
st.title("Smart Query Broadcaster")

# Sidebar for "Global Data" to make results look data-driven
user_location = st.sidebar.text_input("My Location", value="Sydney, NSW")

pasted_list = st.text_area("Paste your daily list here:", height=300)

if st.button("Generate & Send to Extensions"):
    lines = [line.strip() for line in pasted_list.split('\n') if line.strip()]
    
    for line in lines:
        smart_result = build_natural_query(line, user_location)
        st.info(f"Original: {line}\n\n**Generated:** {smart_result}")
        # Here is where you would call your websocket emit
        # sio.emit('broadcast_query', {'query': smart_result})
