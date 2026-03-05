import streamlit as st
import time
from huggingface_hub import InferenceClient

# 1. SECURE TOKEN SETUP
# Make sure you have added HF_TOKEN to your Streamlit Secrets!
try:
    hf_token = st.secrets["HF_TOKEN"]
    client = InferenceClient(api_key=hf_token)
except Exception:
    st.error("⚠️ HF_TOKEN not found in Streamlit Secrets!")
    st.stop()

# 2. THE CHAT-BASED HUMANIZER
def humanize_query(robotic_text):
    try:
        # Using chat.completions specifically to solve the 'Supported task' error
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a human search assistant. Your job is to rewrite robotic commands "
                        "into natural, high-intent search queries. You MUST include specific items, "
                        "specific details, and specific actions (like 'deals' or 'how to'). "
                        "Do not repeat words or stutter. Be concise."
                    )
                },
                {
                    "role": "user", 
                    "content": f"Rewrite this: {robotic_text}"
                }
            ],
            max_tokens=70,
            temperature=0.7 # Helps prevent repetition loops
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Fallback to ensure your broadcast never stops
        clean = robotic_text.lower().replace("search on bing to find", "").strip()
        return f"Looking for the best rated {clean} with reviews and current deals."

# 3. STREAMLIT INTERFACE
st.set_page_config(page_title="Zaky's AI Broadcaster", page_icon="🌿")
st.title("🌿 High-Intent Chat Broadcaster")
st.markdown("Fixed for Mistral-7B Chat Completion Task.")

pasted_list = st.text_area("Paste your 16 robotic queries here:", height=250)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        progress_bar = st.progress(0)
        for i, line in enumerate(lines):
            # Step A: Generate the complete, humanized query
            natural_query = humanize_query(line)
            
            # Step B: Display and Broadcast
            # (Your Socket.io emit code goes here)
            st.success(f"**Broadcasted:** {natural_query}")
            
            # Step C: Safe-Timer (Prevents 429 Rate Limit errors)
            time.sleep(1.5) 
            progress_bar.progress((i + 1) / len(lines))
    else:
        st.warning("Please paste your list first.")
