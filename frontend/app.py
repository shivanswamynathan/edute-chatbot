import streamlit as st
import requests
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="EduBot - Your Learning Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "student_id" not in st.session_state:
    st.session_state.student_id = "student_001"  # Would be from authentication
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

def main():
    st.title("📚 EduBot - Your Personal Learning Assistant")
    
    # Sidebar
    with st.sidebar:
        st.header("📖 Learning Mode")
        mode = st.selectbox(
            "Choose your learning mode:",
            ["learn", "quiz", "revision"],
            format_func=lambda x: {
                "learn": "🎓 Learn & Explain",
                "quiz": "🧠 Quiz & Test",
                "revision": "📝 Review & Summarize"
            }[x]
        )
        
        st.header("📁 Upload Materials")
        uploaded_file = st.file_uploader(
            "Upload your study materials (PDF)",
            type=["pdf"],
            help="Upload textbooks, notes, or any study material"
        )
        
        if uploaded_file and uploaded_file not in st.session_state.uploaded_files:
            if upload_file(uploaded_file):
                st.session_state.uploaded_files.append(uploaded_file)
                st.success("✅ File uploaded successfully!")
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.header("📚 Your Materials")
            for file in st.session_state.uploaded_files:
                st.write(f"📄 {file.name}")
        
        # Mode descriptions
        st.header("ℹ️ Mode Guide")
        if mode == "learn":
            st.info("💡 Ask questions and get detailed explanations about your study materials.")
        elif mode == "quiz":
            st.info("🎯 Generate practice questions and test your knowledge.")
        elif mode == "revision":
            st.info("📋 Get summaries and revision guides for quick review.")
    
    # Main chat interface
    st.header(f"💬 Chat - {mode.title()} Mode")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.write(f"• {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your study materials..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chat_response(prompt, mode)
                
                if response:
                    st.write(response["content"])
                    
                    # Store assistant message with sources
                    assistant_message = {
                        "role": "assistant", 
                        "content": response["content"],
                        "sources": response.get("sources", [])
                    }
                    st.session_state.messages.append(assistant_message)
                    
                    # Show sources
                    if response.get("sources"):
                        with st.expander("📚 Sources"):
                            for source in response["sources"]:
                                st.write(f"• {source}")
                else:
                    error_msg = "Sorry, I encountered an error. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def upload_file(uploaded_file):
    """Upload file to backend"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return False

def get_chat_response(query, mode):
    """Get response from chat API"""
    try:
        # Get file IDs (simplified - would track actual file IDs)
        file_ids = [f"file_{i}" for i in range(len(st.session_state.uploaded_files))]
        
        data = {
            "query": query,
            "student_id": st.session_state.student_id,
            "mode": mode,
            "file_ids": file_ids
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=data)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "content": result["response"],
                "sources": [source["source"] for source in result.get("sources", [])]
            }
        else:
            st.error(f"Chat error: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

if __name__ == "__main__":
    main()