import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="Finance Assistant (Voice)",
    page_icon="💬",
    layout="centered"
)

# Sidebar instructions
st.sidebar.header("How to use")
st.sidebar.markdown(
    """
    - **Upload** a WAV file containing your finance question.
    - **Wait** for the assistant to transcribe and answer.
    - **Try** queries like "What is the current stock price of Apple?" or "Show me the latest SEC filings for Netflix."
    """
)

# Main title
st.markdown("<h1 style='text-align: center;'>💬 Finance Assistant (Voice)</h1>", unsafe_allow_html=True)

# File uploader
audio_file = st.file_uploader(
    "Upload your voice query (WAV)",
    type=["wav"],
    help="Max size 200MB"
)

if audio_file:
    # Play back uploaded audio
    st.audio(audio_file, format='audio/wav')

    # Show spinner during API call
    with st.spinner("Processing your query..."):
        try:
            # Send to backend
            response = requests.post(
                "http://localhost:8000/query",
                files={"file": audio_file},
                timeout=30
            )
            data = response.json()

            # Display assistant response
            if "response" in data:
                st.success("**Assistant Response:**")
                st.markdown(f"> {data['response']}" )
            elif "error" in data:
                st.error(f"⚠️ Error from backend: {data['error']}")
            else:
                st.warning("⚠️ Unexpected response structure.")

            # Raw JSON in expander
            with st.expander("Show raw response"):
                st.code(response.text, language='json')

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request failed: {e}")
