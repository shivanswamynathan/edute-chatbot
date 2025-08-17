import streamlit as st
import requests
from typing import List

def upload_page():
    st.title("📁 Upload Study Materials")
    
    st.write("""
    Upload your textbooks, lecture notes, or any study materials in PDF format. 
    The system will process and index them for intelligent Q&A.
    """)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="You can upload multiple PDF files at once"
    )
    
    if uploaded_files:
        st.write(f"📄 Selected {len(uploaded_files)} file(s):")
        
        for file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"• {file.name}")
            with col2:
                st.write(f"{file.size / 1024:.1f} KB")
            with col3:
                if st.button(f"Upload", key=f"upload_{file.name}"):
                    upload_single_file(file)
    
    # Upload all button
    if uploaded_files and st.button("📤 Upload All Files", type="primary"):
        upload_multiple_files(uploaded_files)

def upload_single_file(file):
    """Upload a single file"""
    try:
        with st.spinner(f"Uploading {file.name}..."):
            files = {"file": (file.name, file.getvalue(), "application/pdf")}
            response = requests.post("http://localhost:8000/api/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ {file.name} uploaded successfully!")
                st.info(f"Created {result['chunks_created']} text chunks for processing")
            else:
                st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ Error uploading {file.name}: {str(e)}")

def upload_multiple_files(files: List):
    """Upload multiple files"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file in enumerate(files):
        status_text.text(f"Uploading {file.name}...")
        upload_single_file(file)
        progress_bar.progress((i + 1) / len(files))
    
    status_text.text("✅ All uploads completed!")