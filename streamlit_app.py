import streamlit as st
import requests

st.set_page_config(
    page_title="Finance Assistant (Voice)",
    page_icon="💬",
    layout="centered"
)

st.sidebar.header("How to use")
st.sidebar.markdown(
    """
    - **Upload** a WAV file containing your finance question.
    - **Wait** for the assistant to transcribe and answer.
    - If the assistant asks for clarification (e.g. couldn’t parse your portfolio), **upload** a clearer/rephrased WAV.
    """
)

st.markdown("<h1 style='text-align: center;'>💬 Finance Assistant (Voice)</h1>", unsafe_allow_html=True)

# ← NEW: Example questions panel
st.markdown("**💡 Example questions you can ask:**")
st.markdown(
    """
    - “What is the current stock price of Apple?”  
    - “Show me the latest SEC filings for Netflix.”  
    - “What was Microsoft’s price-to-earnings ratio last quarter?”  
    - “How much of my portfolio is allocated to Asia tech?”  
    - “Give me a summary of Tesla’s historical performance.”  
    """
)

# --- Session State Initialization ---
if "clarify_prompt" not in st.session_state:
    st.session_state.clarify_prompt = None
if "last_file_name" not in st.session_state:
    st.session_state.last_file_name = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "ambiguous_attempts" not in st.session_state:
    st.session_state.ambiguous_attempts = 0

MAX_AMBIGUOUS_ATTEMPTS = 3  # You can adjust this

def process_upload(wav, label="Your query"):
    st.audio(wav, format="audio/wav")
    with st.spinner("Processing your query..."):
        resp = requests.post("http://orchestrator:8000/query", files={"file": wav}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    return data

def show_result(result):
    if "response" in result:
        st.success("**Assistant Response:**")
        st.markdown(f"> {result['response']}")
    elif "error" in result:
        st.error(f"⚠️ Error: {result['error']}")
    with st.expander("Show raw response"):
        st.json(result)

# --- STEP 1: Initial upload ---
if st.session_state.clarify_prompt is None:
    audio_file = st.file_uploader(
        "Upload your voice query (WAV)",
        type=["wav"],
        help="Max 200MB"
    )
    if audio_file is not None and audio_file.name != st.session_state.last_file_name:
        result = process_upload(audio_file)
        st.session_state.last_result = result
        st.session_state.last_file_name = audio_file.name
        if result.get("clarify"):
            st.session_state.clarify_prompt = result["clarify_prompt"]
            st.session_state.ambiguous_attempts = 1
            st.rerun()
        else:
            st.session_state.ambiguous_attempts = 0  # Reset on success
            show_result(result)
    elif st.session_state.last_result:
        show_result(st.session_state.last_result)

# --- STEP 2: Clarification branch ---
else:
    if st.session_state.ambiguous_attempts >= MAX_AMBIGUOUS_ATTEMPTS:
        st.error("⚠️ Too many ambiguous attempts. Please try a different or clearer question.")
        if st.button("Restart"):
            st.session_state.clarify_prompt = None
            st.session_state.last_file_name = None
            st.session_state.last_result = None
            st.session_state.ambiguous_attempts = 0
            st.rerun()
    else:
        st.warning(f"🔄 Clarification needed:\n\n> {st.session_state.clarify_prompt}")
        clar_audio = st.file_uploader(
            "Re-upload clarified audio (WAV)",
            type=["wav"],
            key="clarify"
        )
        if clar_audio is not None and clar_audio.name != st.session_state.last_file_name:
            result = process_upload(clar_audio, label="Clarification")
            st.session_state.last_result = result
            st.session_state.last_file_name = clar_audio.name
            if result.get("clarify"):
                st.session_state.clarify_prompt = result["clarify_prompt"]
                st.session_state.ambiguous_attempts += 1
                st.rerun()
            else:
                st.session_state.clarify_prompt = None
                st.session_state.ambiguous_attempts = 0
                show_result(result)
        elif st.session_state.last_result:
            show_result(st.session_state.last_result)
