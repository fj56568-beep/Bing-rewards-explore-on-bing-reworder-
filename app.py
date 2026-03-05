import streamlit as st
import time
from huggingface_hub import InferenceClient

# 1. SETUP THE CLIENT SECURELY
# It looks for a secret named 'HF_TOKEN' in your Streamlit dashboard
try:
    hf_token = st.secrets["HF_TOKEN"]
    client = InferenceClient(api_key=hf_token)
except Exception:
    st.error("⚠️ HF_TOKEN not found! Please add it to Streamlit Secrets.")
    st.stop()

# 2. THE HUMANIZER LOGIC
def humanize_query(robotic_text):
    # This is the "Instruction Shell" that ensures a full answer
    prompt = (
        "Instructions: Rewrite this robotic command into a specific, natural search query. "
        "You MUST include: 1. A specific item name, 2. A specific detail, and 3. An action like 'deals' or 'how to'. "
        f"Input: {robotic_text}\n"
        "Output:"
    )
    
    try:
        # We use a smart model (Mistral or Llama-3) via the API
        response = client.text_generation(
            prompt,
            model="mistralai/Mistral-7B-Instruct-v0.2",
            max_new_tokens=60,
            temperature=0.8,
            stop_sequences=["\n"]
        )
        return response.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# 3. STREAMLIT UI
st.title("🌿 High-Intent AI Broadcaster")
st.info("Using Hugging Face API for deep, specific searches.")

pasted_list = st.text_area("Paste your 16 robotic queries here:", height=250)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        progress_bar = st.progress(0)
        for i, line in enumerate(lines):
            # Step A: Generate the full-intent query
            natural_query = humanize_query(line)
            
            # Step B: Display result
            st.success(f"**Broadcasted:** {natural_query}")
            
            # Step C: Anti-Rate-Limit Delay (Safe Timer)
            time.sleep(1.5) 
            
            # Update progress
            progress_bar.progress((i + 1) / len(lines))
    else:
        st.warning("Please paste your list first.")
