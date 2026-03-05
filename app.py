import streamlit as st
import time
import re
from huggingface_hub import InferenceClient

# 1. SETUP THE CLIENT
try:
    hf_token = st.secrets["HF_TOKEN"]
    client = InferenceClient(api_key=hf_token)
except Exception:
    st.error("⚠️ HF_TOKEN not found in Streamlit Secrets!")
    st.stop()

# 2. THE DEEPSEEK HUMANIZER (Fixed for Free Tier)
def humanize_with_deepseek(robotic_text):
    # This format is required for 'text_generation' to act like a chat
    prompt = (
        f"<｜begin_of_sentence｜><｜User｜>I want you to act as a human search assistant. "
        f"Rewrite this robotic topic into a highly specific, data-driven, natural query. "
        f"Include technical details or brands. Provide your thinking inside <think> tags. "
        f"Topic: {robotic_text}<｜Assistant｜><think>"
    )
    
    try:
        # We use text_generation because it bypasses the 'Task Not Supported' error
        # DeepSeek-R1-Distill-Qwen-1.5B is the most stable free model for this.
        response = client.text_generation(
            prompt,
            model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
            max_new_tokens=500,
            temperature=0.7,
            return_full_text=False
        )
        return "<think>" + response # Adding the tag back for our logic
    except Exception as e:
        return f"Error: {str(e)}"

# 3. STREAMLIT UI
st.title("🌿 DeepSeek Reasoning Broadcaster")

pasted_list = st.text_area("Paste your 16+ robotic queries here:", height=300)

if st.button("🚀 Humanize & Broadcast"):
    lines = [l.strip() for l in pasted_list.split('\n') if l.strip()]
    
    if lines:
        for i, line in enumerate(lines):
            full_response = humanize_with_deepseek(line)
            
            # Separate Thinking from the Query
            think_match = re.search(r'<think>(.*?)</think>', full_response, re.DOTALL)
            thinking = think_match.group(1).strip() if think_match else "Thinking..."
            final_query = re.sub(r'<think>.*?</think>', '', full_response, flags=re.DOTALL).strip()

            # Display with Thinking Dropdown
            with st.expander(f"🧠 DeepSeek's Logic for: {line[:30]}..."):
                st.write(thinking)
            
            st.success(f"**Broadcasted:** {final_query}")
            
            # Wait 2 seconds to avoid rate limits
            time.sleep(2.0) 
    else:
        st.warning("Please paste your list first.")
