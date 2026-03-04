# 1. ADD THIS AT THE TOP OF YOUR FILE
FILLER_PHRASES = [
    "search on bing to find", 
    "search on bing for", 
    "deals and reviews for your next", 
    "search for", 
    "find deals and reviews",
    "to find",
    "looking for"
]

def extract_core_subject(text):
    """Surgically removes fluff to find the actual item (e.g., 'book' or 'car')"""
    clean = text.lower()
    for phrase in FILLER_PHRASES:
        clean = clean.replace(phrase, "")
    
    # Remove common extra words that clutter the 'item'
    clean = clean.replace("your next", "").replace("the best", "").strip()
    
    # If it's still too long, we take the last 2-3 words (usually the actual item)
    words = clean.split()
    if len(words) > 4:
        clean = " ".join(words[-2:]) 
    
    return clean

# 2. UPDATE THE BROADCAST LOOP
if st.button("Generate & Push to All Profiles"):
    lines = pasted_data.split('\n')
    
    for line in lines:
        if not line.strip(): continue
        
        # This is where the magic happens
        subject = extract_core_subject(line)
        
        # Categorize based on the CLEAN subject
        if "book" in subject:
            niche = "book"
        elif any(w in subject for w in ["insurance", "policy"]):
            niche = "insurance"
        else:
            niche = "default"
            
        config = NICHE_MAP[niche]
        template = random.choice(config["templates"])
        
        # Now {item} will just be "book" instead of the whole long sentence
        query = template.format(
            adj=random.choice(config["details"]),
            item=subject, 
            extra=random.choice(config["context"]),
            loc=location
        )
        
        sio.emit('new_search', {'query': query})
        st.success(f"**Natural Query:** {query}")
