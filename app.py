import streamlit as st
import time
from huggingface_hub import InferenceClient

# 1. SETUP THE CLIENT
try:
    hf_token = st.secrets["HF_TOKEN"]
    client = InferenceClient(api_key=hf_token)
except Exception:
    st.error("⚠️ HF_TOKEN not found in Streamlit Secrets!")
    st.stop()

# 2. THE HUMANIZER (Simplified for reliability)
def humanize_query(robotic_text):
    # This prompt forces the AI to be specific without needing a 'Chat' structure
    prompt = (
        "Instructions: Rewrite this robotic search into a specific, natural query. "
        "Include brands, technical specs, and specific actions. "
        f"Rewrite this: {robotic_text}"
    )
    
    try:
        # Using a reliable Google model that works with standard text-generation
        response = client.text_generation(
            prompt,
            model="google/flan-t5-large",
            max_new_tokens=100,
            temperature=0.7
        )
        return response.strip()
    except Exception as e:
        # If it fails, we provide a clean, useful fallback instead of an error
        clean = robotic_text.lower().replace("search on bing to", "").strip()
        return f"Looking for specific deals and expert reviews on {clean}"

# 3. UI
st.title("🌿 Reliable AI Broadcaster")

pasted_list = st.text_area("Paste your robotic queries here:", height=300)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        for line in lines:
            # Get the result
            natural_query = humanize_query(line)
            
            # Display result
            st.success(f"**Broadcasted:** {natural_query}")
            
            # Wait 1.5 seconds so Hugging Face doesn't think you're a spam bot
            time.sleep(1.5) 
    else:
        st.warning("Please paste your list first.")
