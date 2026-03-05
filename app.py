import streamlit as st
import time
from huggingface_hub import InferenceClient

# 1. CLIENT SETUP
try:
    hf_token = st.secrets["HF_TOKEN"]
    client = InferenceClient(api_key=hf_token)
except Exception:
    st.error("⚠️ HF_TOKEN not found in Streamlit Secrets!")
    st.stop()

# 2. THE BATCH HUMANIZER
def process_batch(robotic_lines):
    # This prompt tells the AI to process the WHOLE list at once
    combined_input = "\n".join([f"- {line}" for line in robotic_lines])
    
    system_instructions = (
        "You are a human search assistant. I will give you a list of robotic topics. "
        "For EACH topic, write one highly specific, natural search query. "
        "Include technical details, brands, and clear actions (like 'compare' or 'deals'). "
        "Provide ONLY the list of new queries, one per line. No extra text."
    )
    
    try:
        response = client.chat_completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"Topics:\n{combined_input}"}
            ],
            max_tokens=500, # Increased to handle 16+ queries
            temperature=0.8
        )
        return response.choices[0].message.content.strip().split('\n')
    except Exception as e:
        return [f"API Error: {str(e)}"]

# 3. STREAMLIT UI
st.title("🌿 High-Volume AI Broadcaster")

pasted_list = st.text_area("Paste your 16+ robotic queries here:", height=300)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        with st.spinner("Processing large batch..."):
            # We process the whole list in one API call to save your 'Rate Limit'
            results = process_batch(lines)
            
            for query in results:
                clean_query = query.strip("- ").strip()
                if clean_query:
                    # Your Socket.io code to send to Freddy/Zaky goes here
                    st.success(f"**Broadcasted:** {clean_query}")
    else:
        st.warning("Please paste your list first.")
