import os
import torch
import streamlit as st
import random
import io
import time

# Patch to stop the Streamlit/Torch conflict warning
torch.classes.__path__ = [] 

from rag_pipeline import rag_chain, speech_to_text, text_to_speech
from personas import BOARD_PERSONAS
from st_audiorec import st_audiorec

# embedded models, LLM connection rag chain are loaded only once. 

@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

@st.cache_resource
def load_llm():
    return ChatOllama(model="llama3.1", temperature=0.7)

@st.cache_resource
def get_rag_chain():
    embeddings = load_embeddings()
    llm = load_llm()
    return create_rag_chain(embeddings, llm)

# Replace the global rag_chain assignment
rag_chain = get_rag_chain()

# Keep your existing speech functions (they're lightweight)
from rag_pipeline import speech_to_text, text_to_speech




# --- CONFIGURATION ---
st.set_page_config(page_title="PharmD Interview AI", page_icon="🩺", layout="wide")

def init_session():
    """Initialize metrics, state, and trigger the opening question."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Defaults for metrics and flags
    defaults = {
        "clarity": "0/10",
        "depth": "0/10",
        "star": "0/10",
        "show_report": False,
        "current_persona": random.choice(list(BOARD_PERSONAS.keys())),
        "start_time": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Trigger first question if chat is empty
    if not st.session_state.messages:
        persona_name = st.session_state.current_persona
        persona_style = BOARD_PERSONAS[persona_name]
        
        first_q_prompt = (
            f"Persona: {persona_name}. Style: {persona_style}. "
            "Action: Introduce yourself and ask an introductory PharmD residency "
            "behavioral question based on the provided residency documents."
        )
        
        with st.spinner(f"{persona_name} is entering..."):
            try:
                first_question = rag_chain.invoke(first_q_prompt)
                audio_data = text_to_speech(first_question)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "persona": persona_name,
                    "content": first_question,
                    "audio": audio_data
                })
            except Exception as e:
                st.error(f"Initialization Error: {e}")

def process_response(user_input: str):
    """Processes user input, extracts scores, and generates follow-up."""
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    persona_name = st.session_state.current_persona
    persona_instructions = BOARD_PERSONAS[persona_name]
    
    full_query = f"""
    System Instructions: {persona_instructions}
    User Response: {user_input}

    Task:
    1. Critique the response using ASHP standards (STAR method).
    2. Ask the next logical interview question.
    3. DATA BLOCK: At the end, provide scores in this format:
       SCORE_CLARITY: X/10
       SCORE_DEPTH: X/10
       SCORE_STAR: X/10
    """
    
    with st.spinner(f"{persona_name} is evaluating..."):
        try:
            response_text = rag_chain.invoke(full_query)
            
            # Update metrics from AI response
            for line in response_text.split('\n'):
                if "SCORE_CLARITY" in line: st.session_state.clarity = line.split(':')[-1].strip()
                if "SCORE_DEPTH" in line: st.session_state.depth = line.split(':')[-1].strip()
                if "SCORE_STAR" in line: st.session_state.star = line.split(':')[-1].strip()

            # Clean output for display
            display_text = response_text.split("SCORE_CLARITY")[0].strip()
            audio_bytes = text_to_speech(display_text)
            
            st.session_state.messages.append({
                "role": "assistant", "persona": persona_name,
                "content": display_text, "audio": audio_bytes
            })
            
            # Persona rotation logic
            if random.random() < 0.3:
                st.session_state.current_persona = random.choice(list(BOARD_PERSONAS.keys()))
                
        except Exception as e:
            st.error(f"Processing Error: {e}")

# --- START APP ---
init_session()

# 1. Header Metrics
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Communication Clarity", st.session_state.clarity)
m_col2.metric("Clinical Depth", st.session_state.depth)
m_col3.metric("STAR Compliance", st.session_state.star)

st.title("🩺 PharmD Residency Interview Simulator")
st.info(f"Interviewer: **{st.session_state.current_persona}**")

# 2. Sidebar Dashboard
with st.sidebar:
    st.header("📊 Dashboard")
    
    q_count = len([m for m in st.session_state.messages if m['role'] == 'user'])
    st.progress(min(q_count / 6, 1.0), text=f"Interview Progress: {q_count}/6")
    
    st.divider()
    st.subheader("⏱️ Answer Pacing")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.start_time = time.time()
            st.toast("Timer Started!", icon="⏱️")
    with t_col2:
        if st.button("⏹️ Reset", use_container_width=True):
            st.session_state.start_time = None
    
    if st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        st.write(f"Elapsed Time: **{elapsed}s**")
    
    st.divider()
    with st.expander("📚 STAR Method Guide"):
        st.markdown("**(S)** Situation\n**(T)** Task\n**(A)** Clinical Action\n**(R)** Result")
        

    st.divider()
    if st.button("🏁 Finish & Grade", use_container_width=True):
        st.session_state.show_report = True
    if st.button("🔄 Reset Session", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.rerun()

# 3. Chat Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.caption(f"Interviewer: {msg.get('persona')}")
        st.write(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/wav")

# 4. Input Handling
if not st.session_state.show_report:
    st.divider()
    input_col, audio_col = st.columns([3, 1])
    with audio_col:
        wav_audio_data = st_audiorec()
    with input_col:
        text_input = st.chat_input("Enter your response...")

    if wav_audio_data:
        audio_buffer = io.BytesIO(wav_audio_data)
        with st.spinner("Transcribing..."):
            transcript = speech_to_text(audio_buffer)
            if transcript:
                process_response(transcript)
                st.rerun()
    elif text_input:
        process_response(text_input)
        st.rerun()

# 5. Report Generation
if st.session_state.show_report:
    st.divider()
    st.header("📝 Final Evaluation")
    transcript = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    with st.spinner("Compiling RPD Report..."):
        report = rag_chain.invoke(f"Based on ASHP standards, evaluate this interview:\n\n{transcript}")
        st.markdown(report)
        st.download_button("Download Feedback", report, file_name="Feedback.txt")


# At the very bottom of app.py (after defining everything)
# Force cache initialization on first load
_ = get_rag_chain()

with st.spinner("Warming up AI models (one-time delay)..."):
    rag_chain = get_rag_chain()