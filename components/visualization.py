import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def render_analysis_results():
    """Render analysis and visualization of study materials."""
    st.header("📊 Study Material Analysis")
    
    if not st.session_state.analyzed_data:
        st.info("No analysis data available. Please upload and process your study materials first.")
        return
    
    # Create tabs for different visualizations
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
        "📈 Overview",
        "📚 Content Analysis", 
        "🎯 Study Insights",
        "📋 Detailed Reports"
    ])
    
    with viz_tab1:
        render_overview_dashboard()
    
    with viz_tab2:
        render_content_analysis()
    
    with viz_tab3:
        render_study_insights()
    
    with viz_tab4:
        render_detailed_reports()

def render_overview_dashboard():
    """Render main topics identified section."""
    st.subheader("📚 Main Topics Identified")
    
    if not st.session_state.uploaded_files:
        st.info("Upload your study materials to see identified topics.")
        return
    
    # Collect all topics from analyzed files
    all_topics = []
    for file in st.session_state.uploaded_files:
        analysis = file.get('analysis', {})
        if 'key_topics' in analysis:
            for i, topic in enumerate(analysis['key_topics'][:8]):  # Limit to 8 topics
                # Calculate importance score based on position and frequency
                importance_score = max(3, 10 - i)  # Topics earlier in list get higher scores
                
                # Calculate exam probability based on topic analysis
                exam_probability = min(95, 60 + (importance_score * 3))
                
                # Estimate study hours based on topic complexity and content length
                content_length = len(file.get('content', ''))
                study_hours = max(1, min(8, (content_length // 2000) + (importance_score // 3)))
                
                all_topics.append({
                    'topic': topic,
                    'importance_score': importance_score,
                    'exam_probability': exam_probability,
                    'study_hours': study_hours,
                    'source_file': file['name']
                })
    
    if not all_topics:
        st.info("No topics identified yet. Process your files to see topic analysis.")
        return
    
    # Group similar topics and sort by importance
    topic_groups = {}
    for topic_data in all_topics:
        topic_name = topic_data['topic']
        if topic_name not in topic_groups:
            topic_groups[topic_name] = topic_data
        else:
            # Update with higher importance score if found
            if topic_data['importance_score'] > topic_groups[topic_name]['importance_score']:
                topic_groups[topic_name] = topic_data
    
    # Sort topics by importance score
    sorted_topics = sorted(topic_groups.values(), key=lambda x: x['importance_score'], reverse=True)
    
    # Display topics in expandable cards
    for topic_data in sorted_topics[:6]:  # Show top 6 topics
        with st.expander(f"📖 {topic_data['topic']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Importance Score**")
                st.markdown(f"## {topic_data['importance_score']}/10")
            
            with col2:
                st.markdown("**Exam Probability**")
                st.markdown(f"## {topic_data['exam_probability']}%")
            
            with col3:
                st.markdown("**Study Hours**")
                st.markdown(f"## {topic_data['study_hours']}h")
            
            st.markdown(f"**Source:** {topic_data['source_file']}")
            
            # Add progress bar for importance
            st.progress(topic_data['importance_score'] / 10)

def render_content_analysis():
    """Render content analysis visualizations."""
    st.subheader("📚 Content Analysis")
    
    if not st.session_state.uploaded_files:
        st.info("No files available for analysis.")
        return
    
    # Create comprehensive analysis data
    analysis_data = []
    topic_importance_data = []
    study_metrics_data = []
    
    for file in st.session_state.uploaded_files:
        analysis = file.get('analysis', {})
        content_length = len(file.get('content', ''))
        word_count = len(file.get('content', '').split())
        
        # File-level metrics
        analysis_data.append({
            'File': file['name'][:20] + '...' if len(file['name']) > 20 else file['name'],
            'Full_Name': file['name'],
            'Difficulty': analysis.get('difficulty', 5),
            'Study_Time': analysis.get('study_time_estimate', 20),
            'Content_Length': content_length,
            'Word_Count': word_count,
            'Reading_Time': word_count / 200,  # 200 words per minute
            'Complexity_Score': (analysis.get('difficulty', 5) * word_count) / 1000
        })
        
        # Topic importance analysis
        if 'key_topics' in analysis:
            for i, topic in enumerate(analysis['key_topics'][:5]):
                importance = max(1, 10 - (i * 1.5))
                topic_importance_data.append({
                    'Topic': topic,
                    'Importance': importance,
                    'Source_File': file['name'],
                    'Est_Study_Hours': max(0.5, importance / 3)
                })
        
        # Study metrics
        study_metrics_data.append({
            'File': file['name'][:15] + '...' if len(file['name']) > 15 else file['name'],
            'Estimated_Study_Time': analysis.get('study_time_estimate', 20),
            'Difficulty_Level': analysis.get('difficulty', 5),
            'Priority_Score': analysis.get('difficulty', 5) * (content_length / 1000),
            'Content_Density': word_count / max(1, content_length / 1000)
        })
    
    if analysis_data:
        # Multi-dimensional file analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 File Complexity & Study Time")
            df_analysis = pd.DataFrame(analysis_data)
            
            fig_bubble = px.scatter(
                df_analysis,
                x='Word_Count',
                y='Difficulty',
                size='Study_Time',
                color='Complexity_Score',
                hover_name='Full_Name',
                hover_data={
                    'Reading_Time': ':.1f',
                    'Study_Time': True,
                    'Word_Count': ':,',
                    'Complexity_Score': ':.2f'
                },
                title="Content Complexity Analysis",
                labels={
                    'Word_Count': 'Word Count',
                    'Difficulty': 'Difficulty Level (1-10)',
                    'Study_Time': 'Study Time (min)',
                    'Complexity_Score': 'Complexity Score'
                },
                color_continuous_scale='Viridis'
            )
            fig_bubble.update_layout(height=400)
            st.plotly_chart(fig_bubble, use_container_width=True)
        
        with col2:
            st.subheader("⏱️ Study Time vs Reading Time")
            
            fig_time = px.bar(
                df_analysis,
                x='File',
                y=['Reading_Time', 'Study_Time'],
                title="Reading vs Study Time Comparison",
                labels={
                    'value': 'Time (minutes)',
                    'variable': 'Time Type',
                    'File': 'File Name'
                },
                color_discrete_map={
                    'Reading_Time': '#3498db',
                    'Study_Time': '#e74c3c'
                }
            )
            fig_time.update_layout(
                height=400,
                xaxis_tickangle=-45,
                legend_title="Time Type"
            )
            st.plotly_chart(fig_time, use_container_width=True)
    
    # Topic importance heatmap
    if topic_importance_data:
        st.subheader("🎯 Topic Importance Heatmap")
        df_topics = pd.DataFrame(topic_importance_data)
        
        # Create pivot table for heatmap
        topic_matrix = df_topics.pivot_table(
            values='Importance',
            index='Topic',
            columns='Source_File',
            fill_value=0
        )
        
        fig_heatmap = px.imshow(
            topic_matrix.values,
            x=topic_matrix.columns,
            y=topic_matrix.index,
            color_continuous_scale='RdYlBu_r',
            title="Topic Importance Across Files",
            labels={'color': 'Importance Score'}
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Study priority analysis
    if study_metrics_data:
        st.subheader("📈 Study Priority Analysis")
        df_priority = pd.DataFrame(study_metrics_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_priority = px.scatter(
                df_priority,
                x='Difficulty_Level',
                y='Estimated_Study_Time',
                size='Priority_Score',
                color='Content_Density',
                hover_name='File',
                title="Study Priority Matrix",
                labels={
                    'Difficulty_Level': 'Difficulty Level',
                    'Estimated_Study_Time': 'Study Time (min)',
                    'Priority_Score': 'Priority Score',
                    'Content_Density': 'Content Density'
                },
                color_continuous_scale='Plasma'
            )
            st.plotly_chart(fig_priority, use_container_width=True)
        
        with col2:
            # Priority ranking
            df_priority_sorted = df_priority.sort_values('Priority_Score', ascending=False)
            
            fig_ranking = px.bar(
                df_priority_sorted,
                x='Priority_Score',
                y='File',
                orientation='h',
                title="Study Priority Ranking",
                labels={
                    'Priority_Score': 'Priority Score',
                    'File': 'File Name'
                },
                color='Priority_Score',
                color_continuous_scale='Reds'
            )
            fig_ranking.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_ranking, use_container_width=True)
    
    # Enhanced word frequency analysis
    st.subheader("📝 Advanced Text Analysis")
    render_word_frequency()

def render_word_frequency():
    """Render simplified and more meaningful text analysis."""
    # Combine all content
    all_text = ""
    for file in st.session_state.uploaded_files:
        all_text += file['content'] + " "
    
    if all_text.strip():
        # Enhanced stop words list for better filtering
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 
            'these', 'those', 'it', 'its', 'they', 'them', 'their', 'we', 'our', 'you', 'your', 
            'he', 'she', 'his', 'her', 'him', 'i', 'me', 'my', 'mine', 'from', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over',
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
        }
        
        # Clean and filter words more effectively
        words = all_text.lower().split()
        filtered_words = []
        
        for word in words:
            # Remove punctuation and clean word
            clean_word = word.strip('.,!?;:"()[]{}+-=*/_\\|`~@#$%^&<>')
            
            # Keep only meaningful words (technical terms, concepts, etc.)
            if (clean_word not in stop_words and 
                len(clean_word) > 3 and 
                clean_word.isalpha() and
                not clean_word.isdigit()):
                filtered_words.append(clean_word)
        
        # Count frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 10 key terms (reduced from 20 for clarity)
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if top_words:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔑 Key Terms")
                words_df = pd.DataFrame(top_words, columns=['Term', 'Frequency'])
                
                fig_words = px.bar(
                    words_df,
                    x='Frequency',
                    y='Term',
                    orientation='h',
                    title="Most Important Study Terms",
                    color='Frequency',
                    color_continuous_scale='Blues'
                )
                fig_words.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    height=400
                )
                st.plotly_chart(fig_words, use_container_width=True)
            
            with col2:
                st.subheader("📈 Term Relevance")
                
                # Calculate relevance scores
                max_freq = max([freq for _, freq in top_words])
                relevance_data = []
                
                for term, freq in top_words:
                    relevance_score = (freq / max_freq) * 100
                    category = "High Priority" if relevance_score > 70 else "Medium Priority" if relevance_score > 40 else "Low Priority"
                    
                    relevance_data.append({
                        'Term': term,
                        'Relevance': relevance_score,
                        'Category': category,
                        'Frequency': freq
                    })
                
                relevance_df = pd.DataFrame(relevance_data)
                
                fig_relevance = px.scatter(
                    relevance_df,
                    x='Frequency',
                    y='Relevance',
                    size='Frequency',
                    color='Category',
                    hover_name='Term',
                    title="Term Relevance Analysis",
                    labels={'Relevance': 'Relevance Score (%)', 'Frequency': 'Frequency Count'},
                    color_discrete_map={
                        'High Priority': '#e74c3c',
                        'Medium Priority': '#f39c12',
                        'Low Priority': '#3498db'
                    }
                )
                fig_relevance.update_layout(height=400)
                st.plotly_chart(fig_relevance, use_container_width=True)
                
                # Show term categories
                st.markdown("**Focus Areas:**")
                for category in ['High Priority', 'Medium Priority', 'Low Priority']:
                    terms = relevance_df[relevance_df['Category'] == category]['Term'].tolist()
                    if terms:
                        color = "🔴" if category == "High Priority" else "🟡" if category == "Medium Priority" else "🔵"
                        st.markdown(f"{color} **{category}:** {', '.join(terms[:3])}")
        else:
            st.info("No significant terms found. Try uploading more detailed study materials.")

def render_study_insights():
    """Render study insights and recommendations."""
    st.subheader("🎯 Study Insights & Recommendations")
    
    # Generate insights based on analysis
    insights = generate_study_insights()
    
    for insight in insights:
        with st.expander(f"💡 {insight['title']}"):
            st.write(insight['description'])
            if 'recommendations' in insight:
                st.markdown("**Recommendations:**")
                for rec in insight['recommendations']:
                    st.markdown(f"• {rec}")

def generate_study_insights():
    """Generate study insights from analyzed data."""
    insights = []
    
    if not st.session_state.uploaded_files:
        return insights
    
    # Content length insights
    total_content = sum(len(file['content']) for file in st.session_state.uploaded_files)
    avg_reading_time = total_content / 200  # Assuming 200 words per minute
    
    insights.append({
        'title': 'Reading Time Estimation',
        'description': f'Based on your uploaded materials ({total_content:,} characters), the estimated reading time is approximately {avg_reading_time:.1f} minutes.',
        'recommendations': [
            'Break down reading into manageable sessions',
            'Use active reading techniques like note-taking',
            'Schedule regular review sessions'
        ]
    })
    
    # File diversity insights
    file_types = set(file.get('type', 'Unknown') for file in st.session_state.uploaded_files)
    insights.append({
        'title': 'Material Diversity',
        'description': f'You have {len(file_types)} different types of materials, which is great for varied learning.',
        'recommendations': [
            'Cross-reference information between different materials',
            'Create connections between concepts from different sources',
            'Use multimedia approach for better retention'
        ]
    })
    
    # Progress insights
    if 'progress_tracker' in st.session_state:
        tracker = st.session_state.progress_tracker
        if hasattr(tracker, 'get_total_study_time'):
            total_time = tracker.get_total_study_time()
            insights.append({
                'title': 'Study Progress',
                'description': f'You\'ve spent approximately {total_time:.1f} minutes studying.',
                'recommendations': [
                    'Maintain consistent study schedule',
                    'Track your progress regularly',
                    'Set achievable daily goals'
                ]
            })
    
    return insights

def render_detailed_reports():
    """Render detailed reports for each file."""
    st.subheader("📋 Detailed File Reports")
    
    for file in st.session_state.uploaded_files:
        with st.expander(f"📄 {file['name']} - Detailed Report"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**File Statistics:**")
                st.write(f"• **Size:** {file.get('size', 'Unknown')} bytes")
                st.write(f"• **Type:** {file.get('type', 'Unknown')}")
                st.write(f"• **Characters:** {len(file['content']):,}")
                st.write(f"• **Words:** {len(file['content'].split()):,}")
                newline_char = '\n'
                st.write(f"• **Lines:** {len(file['content'].split(newline_char)):,}")
            
            with col2:
                analysis = file.get('analysis', {})
                if analysis:
                    st.markdown("**AI Analysis:**")
                    
                    # Display analysis results
                    if 'summary' in analysis:
                        st.write(f"**Summary:** {analysis['summary']}")
                    
                    if 'key_topics' in analysis:
                        st.write("**Key Topics:**")
                        for topic in analysis['key_topics'][:5]:
                            st.write(f"• {topic}")
                    
                    if 'difficulty' in analysis:
                        st.write(f"**Difficulty Level:** {analysis['difficulty']}/10")
                    
                    if 'study_time_estimate' in analysis:
                        st.write(f"**Estimated Study Time:** {analysis['study_time_estimate']} minutes")
                else:
                    st.info("No AI analysis available for this file.")
            
            # Content preview
            st.markdown("**Content Preview:**")
            preview_text = file['content'][:500]
            if len(file['content']) > 500:
                preview_text += "..."
            st.text_area(
                "Content",
                preview_text,
                height=150,
                disabled=True,
                key=f"preview_{file['name']}"
            )
