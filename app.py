import streamlit as st
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download required NLTK resources
@st.cache_resource
def download_nltk_resources():
    try:
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
    except Exception as e:
        pass

download_nltk_resources()

# Page Configuration
st.set_page_config(
    page_title="Veritas - Student News Verifier",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for Student-Friendly UI
st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 16px; text-align: center; color: #4B5563; margin-bottom: 30px; }
    .metric-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-title">🔍 Veritas: AI Fake News Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Empowering students to critically analyze information, spot clickbait, and read summaries.</div>', unsafe_allow_html=True)

# Main layout split into two columns
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📰 Paste News Content")
    title = st.text_input("Article Title", placeholder="Enter the headline here...")
    content = st.text_area("Article Body Text", placeholder="Paste the full article content here...", height=250)
    
    analyze_btn = st.button("Analyze & Summarize ✨", type="primary")

# Simple Extractive Summarizer Implementation
def generate_summary(text, num_sentences=3):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if not sentences:
        return "Not enough content to generate a summary."
    # Grab the initial contextual framework sentences as a quick summary proxy
    return " ".join(sentences[:num_sentences])

# Misinformation & Structural Signal Analysis Engine
def evaluate_credibility(title, body):
    score = 100
    flags = []
    
    combined_text = f"{title} {body}".lower()
    
    # 1. Clickbait / Sensationalism Flags
    clickbait_words = ['shocking', 'unbelievable', 'you won\'t believe', 'secret they hid', 'magic cure', 'totally organic truth', 'miracle']
    found_clickbait = [w for w in clickbait_words if w in combined_text]
    if found_clickbait:
        score -= len(found_clickbait) * 8
        flags.append(f"Contains sensationalist/clickbait phrases: {', '.join(found_clickbait)}")
        
    # 2. Capitalization Analysis (Yelling Headlines)
    capital_ratio = sum(1 for c in title if c.isupper()) / (len(title) + 1)
    if capital_ratio > 0.35 and len(title) > 10:
        score -= 15
        flags.append("High percentage of capitalization in title (often used in sensationalism).")
        
    # 3. Excessive Punctuation
    if '!!' in title or '??' in title or '!!!' in body:
        score -= 10
        flags.append("Excessive use of exclamation or question marks matches standard tabloid patterns.")
        
    # 4. Sentiment Bias Analysis
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(body)
        if abs(sentiment['compound']) > 0.85:
            score -= 12
            flags.append("Highly emotional polarization detected. Objective reporting usually maintains neutrality.")
    except:
        pass
        
    # 5. Length Constraint
    if len(body.split()) < 60:
        score -= 15
        flags.append("Article context is extremely brief. Lack of depth is common in quickly generated rumors.")

    return max(min(score, 100), 0), flags

# UI Processing Logic
if analyze_btn:
    if not content.strip():
        st.warning("Please provide the article text to analyze.")
    else:
        with col2:
            st.subheader("📊 Analysis Results")
            
            # Run the heuristic engine
            trust_score, red_flags = evaluate_credibility(title, content)
            
            # Display Score Progress Bar
            if trust_score >= 75:
                st.success(f"**Credibility Score: {trust_score}/100** (Likely Reliable)")
            elif trust_score >= 45:
                st.warning(f"**Credibility Score: {trust_score}/100** (Proceed with Caution)")
            else:
                st.error(f"**Credibility Score: {trust_score}/100** (High Risk / Suspicious)")
                
            st.progress(trust_score / 100)
            
            # Display Summarization
            st.markdown("### 📝 Quick Summary")
            summary_text = generate_summary(content)
            st.info(summary_text)
            
            # Display Flags
            st.markdown("### 🔍 Risk Breakdown")
            if red_flags:
                for flag in red_flags:
                    st.write(f"⚠️ {flag}")
            else:
                st.write("✅ No blatant formatting or emotional red flags detected in the text structure.")

# Sidebar Educational Corner
with st.sidebar:
    st.image("https://img.icons8.com/illustrations/opacity/100/000000/reading.png", width=80)
    st.title("🎓 Student Fact-Check Guide")
    st.write("""
    Don't let fake news slide! Always run through the **S.I.F.T.** methodology:
    
    * **S**top and double-check.
    * **I**nvestigate the primary source.
    * **F**ind trusted coverage elsewhere.
    * **T**race statements back to their original context.
    """)
    st.divider()
    st.caption("Veritas v1.0 — Built safely for educational classroom workshops.")