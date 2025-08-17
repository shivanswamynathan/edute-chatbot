import streamlit as st
import requests
from datetime import datetime

def chat_page():
    st.title("💬 Chat with Your Materials")
    
    # Mode selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mode = st.radio(
            "Select learning mode:",
            ["learn", "quiz", "revision"],
            format_func=lambda x: {
                "learn": "🎓 Learning Mode - Get explanations and understand concepts",
                "quiz": "🧠 Quiz Mode - Generate practice questions and tests", 
                "revision": "📝 Revision Mode - Get summaries and study guides"
            }[x],
            horizontal=False
        )
    
    with col2:
        st.info(
            "💡 **Tips:**\n"
            "- Be specific in your questions\n"
            "- Ask for examples or clarifications\n" 
            "- Request different difficulty levels\n"
            "- Ask follow-up questions"
        )
    
    # Chat interface
    chat_container = st.container()
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                if message["role"] == "assistant" and "metadata" in message:
                    metadata = message["metadata"]
                    
                    # Show confidence and sources
                    col1, col2 = st.columns(2)
                    with col1:
                        confidence = metadata.get("confidence", 0) * 100
                        st.metric("Confidence", f"{confidence:.0f}%")
                    with col2:
                        st.metric("Sources", len(metadata.get("sources", [])))
                    
                    # Expandable sources
                    if metadata.get("sources"):
                        with st.expander("📚 View Sources"):
                            for source in metadata["sources"]:
                                st.write(f"• {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your study materials..."):
        # Add user message
        user_message = {"role": "user", "content": prompt}
        st.session_state.chat_history.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chat_response(prompt, mode)
                
                if response:
                    st.write(response["content"])
                    
                    # Show metadata
                    col1, col2 = st.columns(2)
                    with col1:
                        confidence = response.get("confidence", 0) * 100
                        st.metric("Confidence", f"{confidence:.0f}%")
                    with col2:
                        st.metric("Sources", len(response.get("sources", [])))
                    
                    # Sources
                    if response.get("sources"):
                        with st.expander("📚 View Sources"):
                            for source in response["sources"]:
                                st.write(f"• {source}")
                    
                    # Add to chat history
                    assistant_message = {
                        "role": "assistant",
                        "content": response["content"],
                        "metadata": {
                            "confidence": response.get("confidence", 0),
                            "sources": response.get("sources", []),
                            "mode": mode,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    st.session_state.chat_history.append(assistant_message)
                else:
                    error_msg = "Sorry, I encountered an error. Please try again."
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def get_chat_response(query: str, mode: str):
    """Get response from chat API"""
    try:
        data = {
            "query": query,
            "student_id": "student_001",  # Would come from authentication
            "mode": mode,
            "file_ids": []  # Would track uploaded file IDs
        }
        
        response = requests.post("http://localhost:8000/api/chat", json=data)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "content": result["response"],
                "sources": [source["source"] for source in result.get("sources", [])],
                "confidence": 0.85,  # Would come from actual response
                "mode": mode
            }
        else:
            st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None