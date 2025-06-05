import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time
from utils.ai_models import get_ai_client
import json

def render_progress_analytics(progress_tracker):
    """Render progress analytics dashboard."""
    st.header("📈 Progress Analytics")
    st.markdown("Track your study progress and performance over time.")
    
    # Create tabs for different analytics
    analytics_tab1, analytics_tab2, analytics_tab3, analytics_tab4, analytics_tab5 = st.tabs([
        "📊 Overview",
        "🎯 AI Task Creator",
        "⏰ Time Tracking",
        "📈 Performance",
        "📅 Calendar View"
    ])
    
    with analytics_tab1:
        render_progress_overview(progress_tracker)
    
    with analytics_tab2:
        render_ai_task_creator(progress_tracker)
    
    with analytics_tab3:
        render_time_tracking(progress_tracker)
    
    with analytics_tab4:
        render_performance_metrics(progress_tracker)
    
    with analytics_tab5:
        render_calendar_view(progress_tracker)

def render_progress_overview(progress_tracker):
    """Render progress overview with key metrics."""
    st.subheader("📊 Study Progress Overview")
    
    # Get progress data
    total_sessions = progress_tracker.get_total_sessions()
    total_time = progress_tracker.get_total_study_time()
    avg_session_time = progress_tracker.get_average_session_time()
    total_materials = len(st.session_state.get('uploaded_files', []))
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📚 Study Sessions",
            value=total_sessions,
            delta=f"+{progress_tracker.get_sessions_this_week()}" if hasattr(progress_tracker, 'get_sessions_this_week') else None
        )
    
    with col2:
        st.metric(
            label="⏱️ Total Time",
            value=f"{total_time:.1f} min",
            delta=f"+{progress_tracker.get_time_this_week():.1f} min" if hasattr(progress_tracker, 'get_time_this_week') else None
        )
    
    with col3:
        st.metric(
            label="📊 Avg Session",
            value=f"{avg_session_time:.1f} min",
            delta=None
        )
    
    with col4:
        st.metric(
            label="📁 Materials",
            value=total_materials,
            delta=None
        )
    
    # Progress chart
    if total_sessions > 0:
        st.subheader("📈 Study Progress Over Time")
        render_progress_chart(progress_tracker)
    else:
        st.info("No study sessions recorded yet. Start studying to see your progress!")
    
    # Study streaks
    render_study_streaks(progress_tracker)

def render_ai_task_creator(progress_tracker):
    """Render AI-powered task creation interface."""
    st.subheader("🎯 AI Task Creator")
    st.markdown("Generate personalized study tasks based on your uploaded materials and analysis.")
    
    if not st.session_state.uploaded_files:
        st.info("Please upload and analyze your study materials first to create AI-powered tasks.")
        return
    
    # Initialize tasks in session state
    if 'study_tasks' not in st.session_state:
        st.session_state.study_tasks = []
    if 'completed_tasks' not in st.session_state:
        st.session_state.completed_tasks = []
    
    # Task creation form
    with st.expander("📝 Create New Study Tasks", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            num_tasks = st.slider(
                "How many tasks would you like to create?",
                min_value=1,
                max_value=10,
                value=5,
                help="Choose the number of study tasks to generate"
            )
        
        with col2:
            study_time = st.slider(
                "How much time do you want to study? (minutes)",
                min_value=30,
                max_value=480,
                value=120,
                step=30,
                help="Total study time available"
            )
        
        # Task difficulty preference
        difficulty_preference = st.selectbox(
            "Task Difficulty Preference:",
            ["Mixed (Recommended)", "Focus on Easy Topics", "Focus on Hard Topics", "Balanced Approach"]
        )
        
        # Task type preference
        task_types = st.multiselect(
            "Task Types to Include:",
            ["Review & Summary", "Practice Questions", "Concept Mapping", "Deep Study", "Quick Review"],
            default=["Review & Summary", "Practice Questions", "Deep Study"]
        )
        
        if st.button("🚀 Generate AI Tasks", type="primary"):
            if st.session_state.get('api_configured', False):
                generate_ai_tasks(num_tasks, study_time, difficulty_preference, task_types, progress_tracker)
            else:
                st.error("Please configure your AI API first in the main settings.")
    
    # Display existing tasks
    if st.session_state.study_tasks:
        st.subheader("📋 Your Study Tasks")
        
        # Task management buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Refresh Tasks"):
                st.rerun()
        with col2:
            if st.button("🗑️ Clear All Tasks"):
                st.session_state.study_tasks = []
                st.session_state.completed_tasks = []
                st.rerun()
        with col3:
            export_tasks_data()
        
        # Display tasks
        for i, task in enumerate(st.session_state.study_tasks):
            task_id = f"task_{i}"
            
            with st.expander(f"{task['priority_icon']} {task['title']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Description:** {task['description']}")
                    st.write(f"**Source:** {task['source_file']}")
                    st.write(f"**Estimated Time:** {task['time_estimate']} minutes")
                    st.write(f"**Difficulty:** {task['difficulty']}/10")
                    st.write(f"**Priority:** {task['priority']}")
                    
                    # Progress bar for task
                    progress = task.get('progress', 0)
                    st.progress(progress / 100)
                
                with col2:
                    # Task completion status
                    completed = st.checkbox(
                        "Completed",
                        value=task.get('completed', False),
                        key=f"complete_{task_id}"
                    )
                    
                    if completed and not task.get('completed', False):
                        # Mark task as completed
                        task['completed'] = True
                        task['completion_time'] = datetime.now().isoformat()
                        st.session_state.completed_tasks.append(task)
                        progress_tracker.add_study_session(task['time_estimate'], "task_completion")
                        st.success("Task completed! Progress recorded.")
                        st.rerun()
                    
                    # Update progress
                    new_progress = st.slider(
                        "Progress",
                        0, 100, 
                        value=task.get('progress', 0),
                        key=f"progress_{task_id}"
                    )
                    task['progress'] = new_progress
        
        # Task statistics
        render_task_statistics()
    
    else:
        st.info("No tasks created yet. Use the form above to generate your first set of AI-powered study tasks.")

def generate_ai_tasks(num_tasks, study_time, difficulty_preference, task_types, progress_tracker):
    """Generate AI-powered study tasks based on analysis."""
    try:
        with st.spinner("Generating AI-powered study tasks..."):
            ai_client = get_ai_client()
            
            # Collect analysis data from uploaded files
            materials_analysis = []
            for file in st.session_state.uploaded_files:
                analysis = file.get('analysis', {})
                materials_analysis.append({
                    'filename': file['name'],
                    'topics': analysis.get('key_topics', []),
                    'difficulty': analysis.get('difficulty', 5),
                    'study_time': analysis.get('study_time_estimate', 20),
                    'summary': analysis.get('summary', ''),
                    'important_concepts': analysis.get('important_concepts', [])
                })
            
            # Create prompt for AI task generation
            prompt = f"""
            Based on the following study materials analysis, create {num_tasks} specific study tasks for a student.
            
            Available study time: {study_time} minutes
            Difficulty preference: {difficulty_preference}
            Task types to include: {', '.join(task_types)}
            
            Materials Analysis:
            {json.dumps(materials_analysis, indent=2)}
            
            For each task, provide:
            1. Title (clear and specific)
            2. Description (detailed instructions)
            3. Source file name
            4. Estimated time (in minutes, total should not exceed {study_time})
            5. Difficulty level (1-10)
            6. Priority (High/Medium/Low based on importance and exam probability)
            7. Task type (from the preferred types)
            
            Make tasks practical, specific, and actionable. Focus on the most important topics based on the analysis.
            
            Respond in JSON format with an array of tasks:
            {{
                "tasks": [
                    {{
                        "title": "task title",
                        "description": "detailed description",
                        "source_file": "filename",
                        "time_estimate": 30,
                        "difficulty": 7,
                        "priority": "High",
                        "task_type": "Review & Summary"
                    }}
                ]
            }}
            """
            
            response = ai_client.generate_study_response(prompt, {}, [])
            
            try:
                # Parse JSON response
                tasks_data = json.loads(response)
                tasks = tasks_data.get('tasks', [])
                
                # Process and add tasks
                for task in tasks:
                    priority_icon = "🔴" if task['priority'] == "High" else "🟡" if task['priority'] == "Medium" else "🟢"
                    
                    task_obj = {
                        'title': task['title'],
                        'description': task['description'],
                        'source_file': task['source_file'],
                        'time_estimate': task['time_estimate'],
                        'difficulty': task['difficulty'],
                        'priority': task['priority'],
                        'priority_icon': priority_icon,
                        'task_type': task.get('task_type', 'Study'),
                        'created_at': datetime.now().isoformat(),
                        'completed': False,
                        'progress': 0
                    }
                    
                    st.session_state.study_tasks.append(task_obj)
                
                st.success(f"Successfully generated {len(tasks)} AI-powered study tasks!")
                
                # Record task creation in progress tracker
                progress_tracker.add_study_session(5, "task_creation")
                
            except json.JSONDecodeError:
                # Fallback: create basic tasks from analysis
                create_fallback_tasks(num_tasks, study_time, materials_analysis)
                st.warning("Created basic tasks from analysis. For better AI tasks, check your API configuration.")
            
    except Exception as e:
        st.error(f"Error generating tasks: {str(e)}")
        # Create fallback tasks
        create_fallback_tasks(num_tasks, study_time, materials_analysis)

def create_fallback_tasks(num_tasks, study_time, materials_analysis):
    """Create basic tasks when AI generation fails."""
    tasks_per_file = max(1, num_tasks // len(materials_analysis))
    time_per_task = study_time // num_tasks
    
    for material in materials_analysis[:num_tasks]:
        for i in range(min(tasks_per_file, num_tasks - len(st.session_state.study_tasks))):
            if len(st.session_state.study_tasks) >= num_tasks:
                break
                
            topics = material.get('topics', ['General Study'])
            topic = topics[i] if i < len(topics) else topics[0] if topics else 'General Study'
            
            task_obj = {
                'title': f"Study: {topic}",
                'description': f"Review and understand the concept of {topic} from {material['filename']}",
                'source_file': material['filename'],
                'time_estimate': time_per_task,
                'difficulty': material.get('difficulty', 5),
                'priority': "Medium",
                'priority_icon': "🟡",
                'task_type': "Review & Summary",
                'created_at': datetime.now().isoformat(),
                'completed': False,
                'progress': 0
            }
            
            st.session_state.study_tasks.append(task_obj)

def render_task_statistics():
    """Render task completion statistics."""
    st.subheader("📊 Task Progress Statistics")
    
    total_tasks = len(st.session_state.study_tasks)
    completed_tasks = len([t for t in st.session_state.study_tasks if t.get('completed', False)])
    
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", total_tasks)
        with col2:
            st.metric("Completed", completed_tasks)
        with col3:
            st.metric("Remaining", total_tasks - completed_tasks)
        with col4:
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        # Progress visualization
        if st.session_state.study_tasks:
            task_data = []
            for task in st.session_state.study_tasks:
                task_data.append({
                    'Task': task['title'][:30] + '...' if len(task['title']) > 30 else task['title'],
                    'Progress': task.get('progress', 0),
                    'Priority': task['priority'],
                    'Time': task['time_estimate']
                })
            
            df = pd.DataFrame(task_data)
            
            fig = px.bar(
                df,
                x='Task',
                y='Progress',
                color='Priority',
                title="Task Progress Overview",
                color_discrete_map={'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#27ae60'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

def export_tasks_data():
    """Export tasks data for download."""
    if st.session_state.study_tasks:
        tasks_text = "# Study Tasks\n\n"
        for i, task in enumerate(st.session_state.study_tasks, 1):
            status = "✅" if task.get('completed', False) else "⏳"
            tasks_text += f"## {i}. {status} {task['title']}\n"
            tasks_text += f"**Description:** {task['description']}\n"
            tasks_text += f"**Source:** {task['source_file']}\n"
            tasks_text += f"**Time:** {task['time_estimate']} minutes\n"
            tasks_text += f"**Priority:** {task['priority']}\n"
            tasks_text += f"**Progress:** {task.get('progress', 0)}%\n\n"
        
        st.download_button(
            label="📥 Export Tasks",
            data=tasks_text,
            file_name=f"study_tasks_{int(time.time())}.md",
            mime="text/markdown"
        )

def render_progress_chart(progress_tracker):
    """Render improved progress chart with better insights."""
    sessions = progress_tracker.get_session_history()
    
    if not sessions:
        st.info("No session data available.")
        return
    
    # Create comprehensive DataFrame
    df_sessions = pd.DataFrame(sessions)
    df_sessions['datetime'] = pd.to_datetime(df_sessions['timestamp'], unit='s')
    df_sessions['date'] = df_sessions['datetime'].dt.date
    df_sessions['weekday'] = df_sessions['datetime'].dt.day_name()
    df_sessions['hour'] = df_sessions['datetime'].dt.hour
    
    # Create two main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Study Time Trends")
        
        # Daily cumulative progress
        daily_stats = df_sessions.groupby('date').agg({
            'duration': 'sum',
            'timestamp': 'count'
        }).reset_index()
        daily_stats.columns = ['date', 'total_time', 'sessions']
        daily_stats['cumulative_time'] = daily_stats['total_time'].cumsum()
        
        # Create area chart for cumulative progress
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['cumulative_time'],
            mode='lines',
            fill='tonexty',
            name='Cumulative Study Time',
            line=dict(color='#3498db', width=3),
            fillcolor='rgba(52, 152, 219, 0.3)'
        ))
        
        fig_trend.add_trace(go.Bar(
            x=daily_stats['date'],
            y=daily_stats['total_time'],
            name='Daily Study Time',
            marker_color='rgba(231, 76, 60, 0.7)',
            yaxis='y2'
        ))
        
        fig_trend.update_layout(
            title='Study Progress Over Time',
            xaxis_title='Date',
            yaxis=dict(title='Cumulative Time (min)', side='left'),
            yaxis2=dict(title='Daily Time (min)', side='right', overlaying='y'),
            hovermode='x unified',
            height=350
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.subheader("Study Patterns")
        
        # Study efficiency analysis
        efficiency_data = []
        for _, row in daily_stats.iterrows():
            avg_session_time = row['total_time'] / row['sessions'] if row['sessions'] > 0 else 0
            efficiency_score = min(100, (avg_session_time / 30) * 100)  # 30 min = 100% efficiency
            
            efficiency_data.append({
                'date': row['date'],
                'efficiency': efficiency_score,
                'sessions': row['sessions'],
                'total_time': row['total_time']
            })
        
        efficiency_df = pd.DataFrame(efficiency_data)
        
        # Create efficiency scatter plot
        fig_efficiency = px.scatter(
            efficiency_df,
            x='sessions',
            y='efficiency',
            size='total_time',
            color='efficiency',
            hover_data=['date', 'total_time'],
            title='Study Efficiency Analysis',
            labels={
                'sessions': 'Number of Sessions',
                'efficiency': 'Session Efficiency (%)',
                'total_time': 'Total Time (min)'
            },
            color_continuous_scale='RdYlGn'
        )
        
        fig_efficiency.update_layout(height=350)
        st.plotly_chart(fig_efficiency, use_container_width=True)

def render_study_streaks(progress_tracker):
    """Render study streak information."""
    current_streak = progress_tracker.get_current_streak()
    longest_streak = progress_tracker.get_longest_streak()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="🔥 Current Streak",
            value=f"{current_streak} days",
            help="Consecutive days with study activity"
        )
    
    with col2:
        st.metric(
            label="🏆 Longest Streak",
            value=f"{longest_streak} days",
            help="Your best consecutive study streak"
        )
    
    # Streak visualization
    if current_streak > 0 or longest_streak > 0:
        streak_data = progress_tracker.get_streak_history()
        if streak_data:
            fig = px.line(
                x=range(len(streak_data)),
                y=streak_data,
                title="Study Streak History",
                labels={'x': 'Days', 'y': 'Streak Length'}
            )
            st.plotly_chart(fig, use_container_width=True)

def render_time_tracking(progress_tracker):
    """Render enhanced time tracking analytics with clearer insights."""
    st.subheader("⏰ Smart Time Analytics")
    
    sessions = progress_tracker.get_session_history()
    
    if not sessions:
        st.info("Start studying to see your time patterns and insights.")
        return
    
    df_sessions = pd.DataFrame(sessions)
    df_sessions['datetime'] = pd.to_datetime(df_sessions['timestamp'], unit='s')
    df_sessions['day_of_week'] = df_sessions['datetime'].dt.day_name()
    df_sessions['hour'] = df_sessions['datetime'].dt.hour
    df_sessions['date'] = df_sessions['datetime'].dt.date
    
    # Weekly pattern analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Weekly Study Pattern")
        
        # Calculate average time by weekday
        weekly_stats = df_sessions.groupby('day_of_week').agg({
            'duration': ['sum', 'count', 'mean']
        }).round(1)
        
        weekly_stats.columns = ['Total_Time', 'Sessions', 'Avg_Session']
        weekly_stats = weekly_stats.reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ], fill_value=0)
        
        # Create enhanced weekly chart
        fig_weekly = go.Figure()
        
        # Add total time bars
        fig_weekly.add_trace(go.Bar(
            x=weekly_stats.index,
            y=weekly_stats['Total_Time'],
            name='Total Study Time',
            marker_color='#3498db',
            yaxis='y'
        ))
        
        # Add average session line
        fig_weekly.add_trace(go.Scatter(
            x=weekly_stats.index,
            y=weekly_stats['Avg_Session'],
            name='Avg Session Length',
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig_weekly.update_layout(
            title='Weekly Study Pattern Analysis',
            xaxis_title='Day of Week',
            yaxis=dict(title='Total Time (min)', side='left'),
            yaxis2=dict(title='Avg Session (min)', side='right', overlaying='y'),
            hovermode='x unified',
            height=350
        )
        
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    with col2:
        st.subheader("Daily Focus Hours")
        
        # Analyze peak study hours
        hourly_analysis = df_sessions.groupby('hour').agg({
            'duration': ['sum', 'count', 'mean']
        }).round(1)
        
        hourly_analysis.columns = ['Total_Time', 'Sessions', 'Avg_Duration']
        
        # Create radar chart for daily patterns
        fig_hourly = px.bar(
            x=hourly_analysis.index,
            y=hourly_analysis['Total_Time'],
            title="Study Time by Hour of Day",
            labels={'x': 'Hour of Day', 'y': 'Total Study Time (min)'},
            color=hourly_analysis['Total_Time'],
            color_continuous_scale='Viridis'
        )
        
        fig_hourly.update_layout(
            height=350,
            xaxis=dict(tickmode='linear', tick0=0, dtick=2)
        )
        
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Session insights
    st.subheader("Session Quality Analysis")
    
    # Calculate session quality metrics
    session_quality = []
    for _, session in df_sessions.iterrows():
        duration = session['duration']
        hour = session['hour']
        
        # Quality scoring
        duration_score = min(100, (duration / 45) * 100)  # 45 min = optimal
        time_score = 100 if 9 <= hour <= 17 else 70 if 7 <= hour <= 21 else 40
        
        quality_score = (duration_score * 0.7) + (time_score * 0.3)
        
        session_quality.append({
            'date': session['date'],
            'duration': duration,
            'hour': hour,
            'quality_score': quality_score,
            'activity_type': session.get('activity_type', 'study')
        })
    
    quality_df = pd.DataFrame(session_quality)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Session duration trends
        fig_duration = px.scatter(
            quality_df,
            x='date',
            y='duration',
            color='quality_score',
            size='duration',
            title="Session Duration & Quality Over Time",
            labels={
                'duration': 'Session Duration (min)',
                'quality_score': 'Quality Score',
                'date': 'Date'
            },
            color_continuous_scale='RdYlGn'
        )
        
        fig_duration.update_layout(height=300)
        st.plotly_chart(fig_duration, use_container_width=True)
    
    with col2:
        # Activity type distribution
        activity_summary = quality_df.groupby('activity_type').agg({
            'duration': 'sum',
            'quality_score': 'mean'
        }).round(1)
        
        fig_activity = px.pie(
            values=activity_summary['duration'],
            names=activity_summary.index,
            title="Study Time by Activity Type",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_activity.update_layout(height=300)
        st.plotly_chart(fig_activity, use_container_width=True)
    
    # Performance insights
    avg_quality = quality_df['quality_score'].mean()
    peak_hour = hourly_analysis['Total_Time'].idxmax()
    best_day = weekly_stats['Total_Time'].idxmax()
    
    st.info(f"""
    **Your Study Insights:**
    - Average session quality: {avg_quality:.1f}/100
    - Peak study hour: {peak_hour}:00
    - Most productive day: {best_day}
    - Total sessions: {len(quality_df)}
    """)

def render_performance_metrics(progress_tracker):
    """Render performance metrics and insights."""
    st.subheader("🎯 Performance Metrics")
    
    # Chat interaction metrics
    chat_stats = progress_tracker.get_chat_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💬 Total Questions",
            value=chat_stats.get('total_questions', 0)
        )
    
    with col2:
        st.metric(
            label="📝 Avg Question Length",
            value=f"{chat_stats.get('avg_question_length', 0):.0f} chars"
        )
    
    with col3:
        st.metric(
            label="🤖 AI Responses",
            value=chat_stats.get('total_responses', 0)
        )
    
    # Performance trends
    if chat_stats.get('questions_over_time'):
        st.subheader("📈 Question Activity Over Time")
        questions_df = pd.DataFrame(chat_stats['questions_over_time'])
        
        fig_questions = px.line(
            questions_df,
            x='date',
            y='count',
            title="Questions Asked Per Day",
            labels={'date': 'Date', 'count': 'Number of Questions'}
        )
        st.plotly_chart(fig_questions, use_container_width=True)
    
    # Study insights
    render_study_insights_summary(progress_tracker)

def render_study_insights_summary(progress_tracker):
    """Render study insights and recommendations."""
    st.subheader("💡 Study Insights")
    
    insights = []
    
    # Generate insights based on usage patterns
    total_time = progress_tracker.get_total_study_time()
    total_sessions = progress_tracker.get_total_sessions()
    
    if total_sessions > 0:
        avg_session = total_time / total_sessions
        
        if avg_session < 15:
            insights.append({
                'type': 'warning',
                'title': 'Short Study Sessions',
                'message': f'Your average session is {avg_session:.1f} minutes. Consider longer sessions for better focus.',
                'recommendation': 'Try the Pomodoro technique: 25-minute focused sessions with 5-minute breaks.'
            })
        elif avg_session > 60:
            insights.append({
                'type': 'info',
                'title': 'Long Study Sessions',
                'message': f'Your average session is {avg_session:.1f} minutes. Great for deep focus!',
                'recommendation': 'Remember to take regular breaks to maintain concentration.'
            })
        else:
            insights.append({
                'type': 'success',
                'title': 'Optimal Session Length',
                'message': f'Your average session of {avg_session:.1f} minutes is in the optimal range.',
                'recommendation': 'Keep up the good work with your study rhythm!'
            })
    
    # Display insights
    for insight in insights:
        if insight['type'] == 'success':
            st.success(f"✅ **{insight['title']}**: {insight['message']} {insight['recommendation']}")
        elif insight['type'] == 'warning':
            st.warning(f"⚠️ **{insight['title']}**: {insight['message']} {insight['recommendation']}")
        else:
            st.info(f"💡 **{insight['title']}**: {insight['message']} {insight['recommendation']}")

def render_calendar_view(progress_tracker):
    """Render calendar view of study activity."""
    st.subheader("📅 Study Calendar")
    st.markdown("Visual representation of your study activity over time.")
    
    # Get session data for calendar
    sessions = progress_tracker.get_session_history()
    
    if not sessions:
        st.info("No study sessions recorded yet.")
        return
    
    # Create calendar heatmap data
    df_sessions = pd.DataFrame(sessions)
    df_sessions['date'] = pd.to_datetime(df_sessions['timestamp'], unit='s').dt.date
    
    # Aggregate by date
    daily_activity = df_sessions.groupby('date').agg({
        'duration': 'sum',
        'timestamp': 'count'
    }).rename(columns={'timestamp': 'sessions'}).reset_index()
    
    # Create heatmap
    fig = px.density_heatmap(
        daily_activity,
        x='date',
        y=[1] * len(daily_activity),  # Single row
        z='duration',
        title="Study Activity Heatmap",
        labels={'z': 'Study Time (minutes)', 'x': 'Date'},
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        yaxis=dict(showticklabels=False, title=''),
        height=200
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity summary
    st.subheader("📋 Recent Activity")
    
    # Last 7 days activity
    recent_sessions = [s for s in sessions if s['timestamp'] > time.time() - 7 * 24 * 3600]
    
    if recent_sessions:
        recent_df = pd.DataFrame(recent_sessions)
        recent_df['date'] = pd.to_datetime(recent_df['timestamp'], unit='s').dt.strftime('%Y-%m-%d')
        recent_df['time'] = pd.to_datetime(recent_df['timestamp'], unit='s').dt.strftime('%H:%M')
        
        st.dataframe(
            recent_df[['date', 'time', 'duration', 'activity_type']].rename(columns={
                'date': 'Date',
                'time': 'Time',
                'duration': 'Duration (min)',
                'activity_type': 'Activity'
            }),
            use_container_width=True
        )
    else:
        st.info("No activity in the last 7 days.")
