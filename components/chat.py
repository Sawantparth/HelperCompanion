import streamlit as st
from utils.ai_models import get_ai_client
from utils.progress_tracker import ProgressTracker
import time

def render_chat_interface():
    """Render the chat interface for study assistance."""
    st.header("💬 Study Assistant Chat")
    st.markdown("Ask questions about your uploaded materials or get study guidance.")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display current context
    if st.session_state.uploaded_files:
        with st.expander("📚 Available Study Materials"):
            for file_data in st.session_state.uploaded_files:
                st.write(f"• {file_data['name']} ({len(file_data['content'])} characters)")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
    
    # Chat input
    user_input = st.chat_input("Ask a question about your study materials or request study guidance...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': time.time()
        })
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    ai_client = get_ai_client()
                    
                    # Prepare context from uploaded files
                    context = prepare_study_context()
                    
                    # Generate response
                    response = ai_client.generate_study_response(
                        user_input, 
                        context, 
                        st.session_state.chat_history
                    )
                    
                    st.write(response)
                    
                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response,
                        'timestamp': time.time()
                    })
                    
                    # Update progress tracker
                    if 'progress_tracker' in st.session_state:
                        st.session_state.progress_tracker.add_chat_interaction(user_input, response)
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': error_msg,
                        'timestamp': time.time()
                    })
    
    # Chat controls
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📥 Export Chat"):
            export_chat_history()
    
    with col3:
        if st.button("💡 Study Tips"):
            show_study_tips()

def prepare_study_context():
    """Prepare context from uploaded study materials."""
    context = {
        'materials': [],
        'total_content': "",
        'file_count': 0
    }
    
    if 'uploaded_files' in st.session_state and st.session_state.uploaded_files:
        for file_data in st.session_state.uploaded_files:
            material = {
                'name': file_data['name'],
                'content_preview': file_data['content'][:2000],  # Limit context size
                'analysis': file_data.get('analysis', {})
            }
            context['materials'].append(material)
            context['total_content'] += file_data['content'][:1000] + "\n\n"
        
        context['file_count'] = len(st.session_state.uploaded_files)
    
    return context

def export_chat_history():
    """Export chat history as a downloadable file."""
    if not st.session_state.chat_history:
        st.warning("No chat history to export.")
        return
    
    # Format chat history
    chat_text = "# Study Assistant Chat History\n\n"
    for message in st.session_state.chat_history:
        role = "**You:**" if message['role'] == 'user' else "**Assistant:**"
        chat_text += f"{role} {message['content']}\n\n"
    
    # Create download button
    st.download_button(
        label="📥 Download Chat History",
        data=chat_text,
        file_name=f"study_chat_{int(time.time())}.md",
        mime="text/markdown"
    )

def show_study_tips():
    """Display general study tips."""
    tips = [
        "🎯 **Active Recall**: Test yourself regularly instead of just re-reading",
        "📅 **Spaced Repetition**: Review material at increasing intervals",
        "🧩 **Break Down Complex Topics**: Divide difficult subjects into smaller chunks",
        "📝 **Summarize in Your Own Words**: Explain concepts as if teaching someone else",
        "🔗 **Make Connections**: Link new information to what you already know",
        "⏰ **Use the Pomodoro Technique**: Study in focused 25-minute sessions",
        "🎨 **Use Multiple Formats**: Combine reading, visual aids, and practice problems",
        "😴 **Get Adequate Sleep**: Memory consolidation happens during rest"
    ]
    
    st.info("💡 **Study Tips for Better Learning:**")
    for tip in tips:
        st.markdown(tip)
