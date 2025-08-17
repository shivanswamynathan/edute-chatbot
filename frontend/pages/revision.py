import streamlit as st
import requests

def revision_page():
    st.title("📝 Revision & Study Guides")
    
    st.write("""
    Generate comprehensive revision materials from your uploaded content.
    Perfect for exam preparation and quick reviews.
    """)
    
    # Topic input
    topic = st.text_input(
        "Enter the topic you want to revise:",
        placeholder="e.g., Photosynthesis, Machine Learning Algorithms, World War II..."
    )
    
    # Revision type
    revision_type = st.selectbox(
        "Select revision format:",
        [
            "comprehensive",
            "quick_summary", 
            "key_points",
            "study_checklist",
            "practice_questions"
        ],
        format_func=lambda x: {
            "comprehensive": "📖 Comprehensive Study Guide",
            "quick_summary": "⚡ Quick Summary", 
            "key_points": "🎯 Key Points Only",
            "study_checklist": "✅ Study Checklist",
            "practice_questions": "❓ Practice Questions"
        }[x]
    )
    
    # Generate button
    if st.button("📚 Generate Revision Material", type="primary") and topic:
        generate_revision_guide(topic, revision_type)
    
    # Sample revision guides
    st.header("📋 Recent Revision Guides")
    
    if "revision_guides" not in st.session_state:
        st.session_state.revision_guides = []
    
    if st.session_state.revision_guides:
        for i, guide in enumerate(st.session_state.revision_guides):
            with st.expander(f"📄 {guide['topic']} - {guide['type']}"):
                st.write(guide['content'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📥 Download", key=f"download_{i}"):
                        st.download_button(
                            label="Download as Text",
                            data=guide['content'],
                            file_name=f"{guide['topic']}_revision.txt",
                            mime="text/plain"
                        )
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                        st.session_state.revision_guides.pop(i)
                        st.rerun()
    else:
        st.info("No revision guides generated yet. Create your first one above!")

def generate_revision_guide(topic: str, revision_type: str):
    """Generate revision guide for the given topic"""
    
    try:
        with st.spinner("Generating revision guide..."):
            
            # Customize query based on revision type
            query_map = {
                "comprehensive": f"Create a comprehensive study guide for {topic}",
                "quick_summary": f"Provide a quick summary of key concepts for {topic}",
                "key_points": f"List the most important points about {topic}",
                "study_checklist": f"Create a study checklist for {topic}",
                "practice_questions": f"Generate practice questions for {topic}"
            }
            
            data = {
                "query": query_map[revision_type],
                "student_id": "student_001",
                "mode": "revision",
                "file_ids": []
            }
            
            response = requests.post("http://localhost:8000/api/chat", json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Save to session state
                guide = {
                    "topic": topic,
                    "type": revision_type,
                    "content": result["response"],
                    "sources": result.get("sources", []),
                    "timestamp": st.session_state.get("timestamp", "")
                }
                
                if "revision_guides" not in st.session_state:
                    st.session_state.revision_guides = []
                
                st.session_state.revision_guides.insert(0, guide)
                
                # Display the generated guide
                st.success("✅ Revision guide generated successfully!")
                
                with st.container():
                    st.subheader(f"📖 {topic} - {revision_type.replace('_', ' ').title()}")
                    st.write(result["response"])
                    
                    # Show sources if available
                    if result.get("sources"):
                        with st.expander("📚 Sources Used"):
                            for source in result["sources"]:
                                st.write(f"• {source}")
            else:
                st.error(f"Failed to generate revision guide: {response.json().get('detail', 'Unknown error')}")
                
    except Exception as e:
        st.error(f"Error generating revision guide: {str(e)}")