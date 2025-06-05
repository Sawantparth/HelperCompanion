import streamlit as st
import os
from pathlib import Path
from utils.file_processor import FileProcessor
from utils.ai_models import get_ai_client

def render_file_upload():
    """Render the file upload interface."""
    st.header("📤 Upload Study Materials")
    st.markdown("Upload your study materials (PDFs, text files, documents) to get AI-powered insights.")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose your study materials",
        type=['pdf', 'txt', 'docx', 'md'],
        accept_multiple_files=True,
        help="Supported formats: PDF, TXT, DOCX, MD"
    )
    
    if uploaded_files:
        # Display uploaded files
        st.subheader("📋 Uploaded Files")
        for i, file in enumerate(uploaded_files):
            with st.expander(f"📄 {file.name} ({file.size} bytes)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"Process File", key=f"process_{i}"):
                        process_file(file, i)
                
                with col2:
                    if st.button(f"Preview", key=f"preview_{i}"):
                        preview_file(file)
                
                with col3:
                    if st.button(f"Remove", key=f"remove_{i}"):
                        # Remove from session state
                        if 'uploaded_files' in st.session_state:
                            st.session_state.uploaded_files = [
                                f for j, f in enumerate(st.session_state.uploaded_files) 
                                if j != i
                            ]
                        st.rerun()
        
        # Process all files button
        if st.button("🚀 Process All Files", type="primary"):
            process_all_files(uploaded_files)

def process_file(file, index):
    """Process a single uploaded file."""
    try:
        with st.spinner(f"Processing {file.name}..."):
            # Initialize file processor
            processor = FileProcessor()
            
            # Extract text from file
            text_content = processor.extract_text(file)
            
            if text_content:
                # Get AI client
                ai_client = get_ai_client()
                
                # Analyze the content
                analysis = ai_client.analyze_study_material(text_content, file.name)
                
                # Store in session state
                if 'uploaded_files' not in st.session_state:
                    st.session_state.uploaded_files = []
                
                file_data = {
                    'name': file.name,
                    'content': text_content,
                    'analysis': analysis,
                    'size': file.size,
                    'type': file.type
                }
                
                # Update or add file data
                existing_file = next((f for f in st.session_state.uploaded_files if f['name'] == file.name), None)
                if existing_file:
                    existing_file.update(file_data)
                else:
                    st.session_state.uploaded_files.append(file_data)
                
                # Update analyzed data for visualization
                if 'analyzed_data' not in st.session_state or st.session_state.analyzed_data is None:
                    st.session_state.analyzed_data = []
                
                st.session_state.analyzed_data.append({
                    'file_name': file.name,
                    'analysis': analysis,
                    'content_length': len(text_content),
                    'timestamp': st.session_state.get('current_time', 'unknown')
                })
                
                st.success(f"✅ Successfully processed {file.name}")
                
                # Show quick insights
                if analysis:
                    st.info("📊 Quick Insights Generated - Check the Analysis tab for detailed results!")
                
            else:
                st.error(f"❌ Could not extract text from {file.name}")
                
    except Exception as e:
        st.error(f"❌ Error processing {file.name}: {str(e)}")

def process_all_files(uploaded_files):
    """Process all uploaded files."""
    if not uploaded_files:
        st.warning("No files to process.")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file in enumerate(uploaded_files):
        status_text.text(f"Processing {file.name}...")
        process_file(file, i)
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    status_text.text("✅ All files processed successfully!")
    st.balloons()

def preview_file(file):
    """Preview file content."""
    try:
        processor = FileProcessor()
        text_content = processor.extract_text(file)
        
        if text_content:
            st.subheader(f"📖 Preview: {file.name}")
            # Show first 1000 characters
            preview_text = text_content[:1000]
            if len(text_content) > 1000:
                preview_text += "..."
            
            st.text_area(
                "Content Preview",
                preview_text,
                height=300,
                disabled=True
            )
            
            # Show file stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Characters", len(text_content))
            with col2:
                st.metric("Words", len(text_content.split()))
            with col3:
                st.metric("Lines", len(text_content.split('\n')))
        else:
            st.error("Could not extract text from this file.")
            
    except Exception as e:
        st.error(f"Error previewing file: {str(e)}")
