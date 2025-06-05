
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from utils.simple_auth import get_user_subjects, get_current_user, require_teacher_role

def render_teacher_dashboard():
    """Render teacher dashboard for monitoring student progress."""
    require_teacher_role()
    
    st.header("👨‍🏫 Teacher Dashboard")
    st.markdown("Monitor your students' progress and performance across subjects.")
    
    # Create tabs for different teacher functionalities
    overview_tab, students_tab, subjects_tab, assignments_tab, analytics_tab = st.tabs([
        "📊 Overview",
        "👥 Students",
        "📚 Subjects",
        "📝 Assignments",
        "📈 Analytics"
    ])
    
    with overview_tab:
        render_teacher_overview()
    
    with students_tab:
        render_student_management()
    
    with subjects_tab:
        render_subject_management()
    
    with assignments_tab:
        render_assignment_management()
    
    with analytics_tab:
        render_teacher_analytics()

def render_teacher_overview():
    """Render teacher overview dashboard."""
    st.subheader("📊 Teaching Overview")
    
    # Teacher info
    user_info = get_current_user()
    subjects = get_user_subjects()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Teacher:** {user_info.get('full_name', 'N/A')}")
        if user_info.get('institution'):
            st.info(f"**Institution:** {user_info.get('institution')}")
    
    with col2:
        if subjects:
            st.success(f"**Teaching Subjects:** {', '.join(subjects)}")
        else:
            st.warning("No subjects assigned yet.")
    
    # Student metrics
    students_data = get_assigned_students()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Students",
            value=len(students_data)
        )
    
    with col2:
        active_students = len([s for s in students_data if is_student_active(s)])
        st.metric(
            label="🟢 Active Students",
            value=active_students
        )
    
    with col3:
        total_study_time = sum(get_student_study_time(s) for s in students_data)
        st.metric(
            label="⏱️ Total Study Time",
            value=f"{total_study_time:.1f} hrs"
        )
    
    with col4:
        avg_performance = calculate_average_performance(students_data)
        st.metric(
            label="📊 Avg Performance",
            value=f"{avg_performance:.1f}%"
        )
    
    # Recent activity
    render_recent_student_activity(students_data)

def render_student_management():
    """Render student management interface."""
    st.subheader("👥 Student Management")
    
    # Add student form
    with st.expander("➕ Add New Student", expanded=False):
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                student_email = st.text_input("Student Email")
                student_name = st.text_input("Student Name")
            
            with col2:
                assigned_subjects = st.multiselect(
                    "Assign Subjects:",
                    get_user_subjects(),
                    help="Select subjects to assign to this student"
                )
                grade_level = st.selectbox(
                    "Grade Level:",
                    ["Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10", 
                     "Grade 11", "Grade 12", "Undergraduate", "Graduate"]
                )
            
            if st.form_submit_button("Add Student"):
                if student_email and student_name:
                    add_student_assignment(student_email, student_name, assigned_subjects, grade_level)
                    st.success(f"Student {student_name} added successfully!")
                else:
                    st.error("Please fill in all required fields.")
    
    # Display assigned students
    students_data = get_assigned_students()
    
    if students_data:
        st.subheader("📋 Your Students")
        
        for student in students_data:
            with st.expander(f"👤 {student['name']} ({student['email']})", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Grade:** {student.get('grade_level', 'N/A')}")
                    st.write(f"**Subjects:** {', '.join(student.get('subjects', []))}")
                
                with col2:
                    study_time = get_student_study_time(student)
                    st.write(f"**Study Time:** {study_time:.1f} hrs")
                    
                    last_active = get_student_last_activity(student)
                    st.write(f"**Last Active:** {last_active}")
                
                with col3:
                    performance = get_student_performance(student)
                    st.write(f"**Performance:** {performance:.1f}%")
                    
                    if st.button(f"View Details", key=f"view_{student['email']}"):
                        show_student_details(student)
    else:
        st.info("No students assigned yet. Use the form above to add students.")

def render_subject_management():
    """Render subject management interface."""
    st.subheader("📚 Subject Management")
    
    subjects = get_user_subjects()
    
    if not subjects:
        st.warning("No subjects assigned to you. Contact administrator to update your teaching subjects.")
        return
    
    for subject in subjects:
        with st.expander(f"📖 {subject}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                students_in_subject = get_students_by_subject(subject)
                st.write(f"**Students Enrolled:** {len(students_in_subject)}")
                
                if students_in_subject:
                    avg_performance = sum(get_student_performance(s) for s in students_in_subject) / len(students_in_subject)
                    st.write(f"**Average Performance:** {avg_performance:.1f}%")
            
            with col2:
                total_study_time = sum(get_student_study_time_by_subject(s, subject) for s in students_in_subject)
                st.write(f"**Total Study Time:** {total_study_time:.1f} hrs")
                
                if st.button(f"Create Assignment", key=f"assign_{subject}"):
                    st.session_state.create_assignment_subject = subject
                    st.rerun()

def render_assignment_management():
    """Render assignment management interface."""
    st.subheader("📝 Assignment Management")
    
    # Create assignment form
    if st.session_state.get('create_assignment_subject'):
        subject = st.session_state.create_assignment_subject
        st.subheader(f"Create Assignment for {subject}")
        
        with st.form("create_assignment_form"):
            assignment_title = st.text_input("Assignment Title")
            assignment_description = st.text_area("Assignment Description")
            
            col1, col2 = st.columns(2)
            with col1:
                due_date = st.date_input("Due Date")
                difficulty_level = st.selectbox("Difficulty Level:", ["Easy", "Medium", "Hard"])
            
            with col2:
                estimated_time = st.number_input("Estimated Time (minutes):", min_value=15, max_value=480, value=60)
                students_to_assign = st.multiselect(
                    "Assign to Students:",
                    [s['name'] for s in get_students_by_subject(subject)]
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Create Assignment"):
                    create_assignment(subject, assignment_title, assignment_description, 
                                    due_date, difficulty_level, estimated_time, students_to_assign)
                    st.success("Assignment created successfully!")
                    del st.session_state.create_assignment_subject
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel"):
                    del st.session_state.create_assignment_subject
                    st.rerun()
    
    # Display existing assignments
    assignments = get_teacher_assignments()
    
    if assignments:
        st.subheader("📋 Your Assignments")
        
        for assignment in assignments:
            with st.expander(f"📝 {assignment['title']} - {assignment['subject']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Due Date:** {assignment['due_date']}")
                    st.write(f"**Difficulty:** {assignment['difficulty']}")
                    st.write(f"**Estimated Time:** {assignment['estimated_time']} min")
                
                with col2:
                    submitted = assignment.get('submissions', 0)
                    total_assigned = assignment.get('total_assigned', 0)
                    st.write(f"**Submissions:** {submitted}/{total_assigned}")
                    
                    completion_rate = (submitted / total_assigned * 100) if total_assigned > 0 else 0
                    st.write(f"**Completion Rate:** {completion_rate:.1f}%")
    else:
        st.info("No assignments created yet.")

def render_teacher_analytics():
    """Render teacher analytics dashboard."""
    st.subheader("📈 Teaching Analytics")
    
    students_data = get_assigned_students()
    
    if not students_data:
        st.info("No student data available for analytics.")
        return
    
    # Performance distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Student Performance Distribution")
        performances = [get_student_performance(s) for s in students_data]
        
        fig_perf = px.histogram(
            x=performances,
            nbins=10,
            title="Performance Distribution",
            labels={'x': 'Performance (%)', 'y': 'Number of Students'}
        )
        st.plotly_chart(fig_perf, use_container_width=True)
    
    with col2:
        st.subheader("⏰ Study Time by Subject")
        subject_times = {}
        
        for subject in get_user_subjects():
            total_time = sum(get_student_study_time_by_subject(s, subject) for s in students_data)
            subject_times[subject] = total_time
        
        if subject_times:
            fig_time = px.bar(
                x=list(subject_times.keys()),
                y=list(subject_times.values()),
                title="Total Study Time by Subject",
                labels={'x': 'Subject', 'y': 'Study Time (hours)'}
            )
            st.plotly_chart(fig_time, use_container_width=True)
    
    # Student progress over time
    st.subheader("📈 Student Progress Over Time")
    progress_data = get_student_progress_over_time(students_data)
    
    if progress_data:
        df_progress = pd.DataFrame(progress_data)
        fig_progress = px.line(
            df_progress,
            x='date',
            y='performance',
            color='student',
            title="Student Performance Trends"
        )
        st.plotly_chart(fig_progress, use_container_width=True)

# Helper functions
def get_assigned_students():
    """Get students assigned to current teacher."""
    # This would typically come from a database
    # For now, return mock data
    return [
        {
            'email': 'student1@example.com',
            'name': 'John Doe',
            'subjects': ['Mathematics', 'Physics'],
            'grade_level': 'Grade 10'
        },
        {
            'email': 'student2@example.com',
            'name': 'Jane Smith',
            'subjects': ['Mathematics'],
            'grade_level': 'Grade 11'
        }
    ]

def is_student_active(student):
    """Check if student was active recently."""
    # Mock implementation
    return True

def get_student_study_time(student):
    """Get total study time for student."""
    # Mock implementation
    return 25.5

def get_student_study_time_by_subject(student, subject):
    """Get study time for specific subject."""
    # Mock implementation
    return 10.2

def calculate_average_performance(students):
    """Calculate average performance across students."""
    # Mock implementation
    return 78.5

def get_student_performance(student):
    """Get student performance percentage."""
    # Mock implementation
    return 82.3

def get_student_last_activity(student):
    """Get student's last activity date."""
    return "2 hours ago"

def get_students_by_subject(subject):
    """Get students enrolled in specific subject."""
    return get_assigned_students()

def add_student_assignment(email, name, subjects, grade):
    """Add student assignment to teacher."""
    # Implementation would save to database
    pass

def create_assignment(subject, title, description, due_date, difficulty, time, students):
    """Create new assignment."""
    # Implementation would save to database
    pass

def get_teacher_assignments():
    """Get assignments created by teacher."""
    return []

def get_student_progress_over_time(students):
    """Get student progress data over time."""
    return []

def show_student_details(student):
    """Show detailed student information."""
    st.json(student)

def render_recent_student_activity(students_data):
    """Render recent student activity."""
    st.subheader("🕐 Recent Student Activity")
    
    if students_data:
        activity_data = []
        for student in students_data[:5]:  # Show last 5 students
            activity_data.append({
                'Student': student['name'],
                'Subject': ', '.join(student.get('subjects', [])),
                'Last Activity': get_student_last_activity(student),
                'Study Time': f"{get_student_study_time(student):.1f} hrs"
            })
        
        df_activity = pd.DataFrame(activity_data)
        st.dataframe(df_activity, use_container_width=True)
    else:
        st.info("No recent activity to display.")
