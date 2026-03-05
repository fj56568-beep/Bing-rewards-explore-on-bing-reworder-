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

# 2. THE SMART HUMANIZER (With your requested System Prompt)
def humanize_query(robotic_text):
    try:
        # We use chat.completions to satisfy the 'conversational' requirement
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "I have a list of topics below. For each one, generate a highly specific, "
                        "natural-sounding search query. Imagine a person who knows exactly what they want "
                        "(including details like brands, locations, or technical specs) and is asking a "
                        "smart assistant for help. Make sure each query feels conversational but data-driven. "
                        "Do not include any introductory text, just the search query itself."
                    )
                },
                {
                    "role": "user", 
                    "content": f"Topic: {robotic_text}"
                }
            ],
            max_tokens=80,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # If the API fails again, this tells us exactly why instead of giving a generic response
        return f"Connection Error: {str(e)}"

# 3. UI LAYOUT
st.set_page_config(page_title="Zaky's AI Broadcaster", page_icon="🌿")
st.title("🌿 High-Intent Data Broadcaster")

pasted_list = st.text_area("Paste your 16 robotic queries here:", height=250)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        progress_bar = st.progress(0)
        for i, line in enumerate(lines):
            # Generate the specific, data-driven query
            natural_query = humanize_query(line)
            
            # Display result
            st.success(f"**Broadcasted:** {natural_query}")
            
            # 1.5 second pause to stay under Hugging Face rate limits
            time.sleep(1.5) 
            progress_bar.progress((i + 1) / len(lines))
    else:
        st.warning("Please paste your list first.")
