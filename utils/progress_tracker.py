import time
from datetime import datetime, timedelta
import json
import os

class ProgressTracker:
    """Track user progress and study analytics."""
    
    def __init__(self, user_id=None):
        from utils.simple_auth import get_user_id
        self.user_id = user_id or get_user_id()
        self.data_file = f"progress_{self.user_id}.json"
        self.data = self.load_data()
    
    def load_data(self):
        """Load progress data from file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default data structure
        return {
            'sessions': [],
            'chat_interactions': [],
            'file_uploads': [],
            'total_study_time': 0,
            'created_at': time.time(),
            'last_updated': time.time()
        }
    
    def save_data(self):
        """Save progress data to file."""
        self.data['last_updated'] = time.time()
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving progress data: {e}")
    
    def add_study_session(self, duration_minutes, activity_type="study"):
        """Add a study session."""
        session = {
            'timestamp': time.time(),
            'duration': duration_minutes,
            'activity_type': activity_type,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.data['sessions'].append(session)
        self.data['total_study_time'] += duration_minutes
        self.save_data()
    
    def add_chat_interaction(self, question, response):
        """Add a chat interaction."""
        interaction = {
            'timestamp': time.time(),
            'question': question,
            'response': response,
            'question_length': len(question),
            'response_length': len(response),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.data['chat_interactions'].append(interaction)
        # Estimate 1 minute per interaction
        self.add_study_session(1, "chat")
    
    def add_file_upload(self, filename, file_size, content_length):
        """Add file upload record."""
        upload = {
            'timestamp': time.time(),
            'filename': filename,
            'file_size': file_size,
            'content_length': content_length,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.data['file_uploads'].append(upload)
        # Estimate processing time based on content length
        processing_time = max(1, content_length / 1000)  # 1 minute per 1000 chars
        self.add_study_session(processing_time, "file_processing")
    
    def get_total_sessions(self):
        """Get total number of study sessions."""
        return len(self.data['sessions'])
    
    def get_total_study_time(self):
        """Get total study time in minutes."""
        return self.data['total_study_time']
    
    def get_average_session_time(self):
        """Get average session time in minutes."""
        sessions = self.data['sessions']
        if not sessions:
            return 0
        
        total_time = sum(s['duration'] for s in sessions)
        return total_time / len(sessions)
    
    def get_session_history(self):
        """Get session history."""
        return self.data['sessions']
    
    def get_current_streak(self):
        """Get current study streak in days."""
        sessions = self.data['sessions']
        if not sessions:
            return 0
        
        # Get unique study dates
        study_dates = sorted(set(s['date'] for s in sessions))
        
        if not study_dates:
            return 0
        
        # Check streak from today backwards
        today = datetime.now().date()
        current_streak = 0
        check_date = today
        
        for i in range(len(study_dates)):
            date_str = check_date.strftime('%Y-%m-%d')
            if date_str in study_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        return current_streak
    
    def get_longest_streak(self):
        """Get longest study streak in days."""
        sessions = self.data['sessions']
        if not sessions:
            return 0
        
        # Get unique study dates
        study_dates = sorted(set(s['date'] for s in sessions))
        study_date_objects = [datetime.strptime(d, '%Y-%m-%d').date() for d in study_dates]
        
        if not study_date_objects:
            return 0
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(study_date_objects)):
            if study_date_objects[i] - study_date_objects[i-1] == timedelta(days=1):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def get_streak_history(self):
        """Get streak history for visualization."""
        sessions = self.data['sessions']
        if not sessions:
            return []
        
        # Get daily activity counts
        daily_counts = {}
        for session in sessions:
            date = session['date']
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        # Calculate daily streaks
        dates = sorted(daily_counts.keys())
        streak_history = []
        current_streak = 0
        
        for i, date in enumerate(dates):
            if i == 0:
                current_streak = 1
            else:
                prev_date = datetime.strptime(dates[i-1], '%Y-%m-%d').date()
                curr_date = datetime.strptime(date, '%Y-%m-%d').date()
                
                if curr_date - prev_date == timedelta(days=1):
                    current_streak += 1
                else:
                    current_streak = 1
            
            streak_history.append(current_streak)
        
        return streak_history
    
    def get_chat_statistics(self):
        """Get chat interaction statistics."""
        interactions = self.data['chat_interactions']
        
        if not interactions:
            return {
                'total_questions': 0,
                'total_responses': 0,
                'avg_question_length': 0,
                'avg_response_length': 0,
                'questions_over_time': []
            }
        
        # Basic stats
        total_questions = len(interactions)
        avg_question_length = sum(i['question_length'] for i in interactions) / total_questions
        avg_response_length = sum(i['response_length'] for i in interactions) / total_questions
        
        # Questions over time
        daily_questions = {}
        for interaction in interactions:
            date = interaction['date']
            daily_questions[date] = daily_questions.get(date, 0) + 1
        
        questions_over_time = [
            {'date': date, 'count': count}
            for date, count in sorted(daily_questions.items())
        ]
        
        return {
            'total_questions': total_questions,
            'total_responses': total_questions,  # Same as questions
            'avg_question_length': avg_question_length,
            'avg_response_length': avg_response_length,
            'questions_over_time': questions_over_time
        }
    
    def get_sessions_this_week(self):
        """Get number of sessions this week."""
        week_ago = (datetime.now() - timedelta(days=7)).timestamp()
        recent_sessions = [s for s in self.data['sessions'] if s['timestamp'] > week_ago]
        return len(recent_sessions)
    
    def get_time_this_week(self):
        """Get study time this week."""
        week_ago = (datetime.now() - timedelta(days=7)).timestamp()
        recent_sessions = [s for s in self.data['sessions'] if s['timestamp'] > week_ago]
        return sum(s['duration'] for s in recent_sessions)
    
    def export_data(self):
        """Export progress data."""
        return self.data.copy()
    
    def import_data(self, data):
        """Import progress data."""
        self.data = data
        self.save_data()
    
    def reset_progress(self):
        """Reset all progress data."""
        self.data = {
            'sessions': [],
            'chat_interactions': [],
            'file_uploads': [],
            'total_study_time': 0,
            'created_at': time.time(),
            'last_updated': time.time()
        }
        self.save_data()
    
    @staticmethod
    def get_student_progress(student_id):
        """Get progress data for a specific student (teacher access)."""
        progress_file = f"progress_{student_id}.json"
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    @staticmethod
    def get_all_students_progress():
        """Get progress data for all students (teacher access)."""
        students_progress = {}
        
        # Find all progress files
        for filename in os.listdir('.'):
            if filename.startswith('progress_') and filename.endswith('.json'):
                student_id = filename.replace('progress_', '').replace('.json', '')
                try:
                    with open(filename, 'r') as f:
                        students_progress[student_id] = json.load(f)
                except Exception:
                    continue
        
        return students_progress
