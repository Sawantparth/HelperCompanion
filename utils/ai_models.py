import streamlit as st
import os
import json
from typing import Dict, List, Optional

# Import AI libraries based on available models
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIClient:
    """Base AI client interface."""
    
    def analyze_study_material(self, content: str, filename: str) -> Dict:
        """Analyze study material and return insights."""
        raise NotImplementedError
    
    def generate_study_response(self, question: str, context: Dict, chat_history: List) -> str:
        """Generate response to study question."""
        raise NotImplementedError

class GeminiClient(AIClient):
    """Google Gemini AI client."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library not available")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
    
    def analyze_study_material(self, content: str, filename: str) -> Dict:
        """Analyze study material using Gemini."""
        try:
            prompt = f"""
            Analyze the following study material from file "{filename}":

            {content[:4000]}  # Limit content to avoid token limits

            Please provide a comprehensive analysis including:
            1. A brief summary (2-3 sentences)
            2. Key topics covered (list of 5-8 main topics)
            3. Difficulty level (1-10 scale)
            4. Estimated study time in minutes
            5. Important concepts to focus on
            6. Suggested study approach

            Respond in JSON format with the following structure:
            {{
                "summary": "brief summary",
                "key_topics": ["topic1", "topic2", ...],
                "difficulty": 5,
                "study_time_estimate": 30,
                "important_concepts": ["concept1", "concept2", ...],
                "study_approach": "suggested approach"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response.text)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                return {
                    "summary": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                    "key_topics": self._extract_topics_from_text(response.text),
                    "difficulty": 5,  # Default difficulty
                    "study_time_estimate": max(10, len(content) // 200),  # Rough estimate
                    "important_concepts": ["Review the material carefully"],
                    "study_approach": "Active reading and note-taking recommended"
                }
            
        except Exception as e:
            st.error(f"Error analyzing material with Gemini: {str(e)}")
            return {
                "summary": "Analysis unavailable due to error",
                "key_topics": ["General study material"],
                "difficulty": 5,
                "study_time_estimate": 20,
                "important_concepts": ["Review content thoroughly"],
                "study_approach": "Standard study approach recommended"
            }
    
    def generate_study_response(self, question: str, context: Dict, chat_history: List) -> str:
        """Generate study response using Gemini."""
        try:
            # Prepare context from study materials
            materials_context = ""
            if context.get('materials'):
                materials_context = "Based on your uploaded study materials:\n\n"
                for material in context['materials'][:3]:  # Limit to 3 materials
                    materials_context += f"From {material['name']}:\n{material['content_preview'][:500]}...\n\n"
            
            # Prepare recent chat history
            recent_history = ""
            if chat_history:
                recent_history = "Recent conversation:\n"
                for msg in chat_history[-4:]:  # Last 4 messages
                    role = "You" if msg['role'] == 'user' else "Assistant"
                    recent_history += f"{role}: {msg['content'][:100]}...\n"
                recent_history += "\n"
            
            prompt = f"""
            You are a helpful AI study assistant. Help the student with their question based on their study materials.

            {recent_history}

            {materials_context}

            Student Question: {question}

            Please provide a helpful, educational response that:
            1. Directly addresses the question
            2. References the study materials when relevant
            3. Provides clear explanations
            4. Suggests follow-up study activities if appropriate
            5. Is encouraging and supportive

            Keep your response concise but comprehensive (2-4 paragraphs).
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I encountered an error while processing your question: {str(e)}. Please try rephrasing your question or check your API configuration."
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract potential topics from text response."""
        # Simple topic extraction - look for capitalized words/phrases
        import re
        topics = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return list(set(topics[:8]))  # Return unique topics, max 8

class OpenAIClient(AIClient):
    """OpenAI GPT client."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available")
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
    
    def analyze_study_material(self, content: str, filename: str) -> Dict:
        """Analyze study material using OpenAI."""
        try:
            prompt = f"""
            Analyze the following study material from file "{filename}":

            {content[:4000]}  # Limit content to avoid token limits

            Please provide a comprehensive analysis including:
            1. A brief summary (2-3 sentences)
            2. Key topics covered (list of 5-8 main topics)
            3. Difficulty level (1-10 scale)
            4. Estimated study time in minutes
            5. Important concepts to focus on
            6. Suggested study approach

            Respond in JSON format with the following structure:
            {{
                "summary": "brief summary",
                "key_topics": ["topic1", "topic2", ...],
                "difficulty": 5,
                "study_time_estimate": 30,
                "important_concepts": ["concept1", "concept2", ...],
                "study_approach": "suggested approach"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert educational content analyzer. Provide detailed analysis in the requested JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            st.error(f"Error analyzing material with OpenAI: {str(e)}")
            return {
                "summary": "Analysis unavailable due to error",
                "key_topics": ["General study material"],
                "difficulty": 5,
                "study_time_estimate": 20,
                "important_concepts": ["Review content thoroughly"],
                "study_approach": "Standard study approach recommended"
            }
    
    def generate_study_response(self, question: str, context: Dict, chat_history: List) -> str:
        """Generate study response using OpenAI."""
        try:
            # Prepare context from study materials
            materials_context = ""
            if context.get('materials'):
                materials_context = "Based on your uploaded study materials:\n\n"
                for material in context['materials'][:3]:  # Limit to 3 materials
                    materials_context += f"From {material['name']}:\n{material['content_preview'][:500]}...\n\n"
            
            # Prepare chat history for context
            messages = [
                {"role": "system", "content": """You are a helpful AI study assistant. Help students with their questions based on their study materials. 
                Provide clear, educational responses that reference their materials when relevant. Be encouraging and supportive."""}
            ]
            
            # Add recent chat history
            for msg in chat_history[-6:]:  # Last 6 messages for context
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Add current question with context
            user_message = f"{materials_context}\n\nStudent Question: {question}"
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I encountered an error while processing your question: {str(e)}. Please try rephrasing your question or check your API configuration."

def get_ai_client() -> AIClient:
    """Get configured AI client based on session state."""
    if not st.session_state.get('api_configured', False):
        raise Exception("API not configured. Please configure your AI model first.")
    
    provider = st.session_state.get('model_provider', '')
    api_key = st.session_state.get('api_key', '')
    model_version = st.session_state.get('model_version', '')
    
    if not api_key:
        raise Exception("API key not provided.")
    
    try:
        if provider == "Google Gemini":
            if not GEMINI_AVAILABLE:
                raise Exception("Google Generative AI library not available. Please install google-generativeai.")
            return GeminiClient(api_key, model_version)
        
        elif provider == "OpenAI":
            if not OPENAI_AVAILABLE:
                raise Exception("OpenAI library not available. Please install openai.")
            return OpenAIClient(api_key, model_version)
        
        else:
            raise Exception(f"Unsupported AI provider: {provider}")
            
    except Exception as e:
        raise Exception(f"Failed to initialize AI client: {str(e)}")

def test_ai_connection() -> tuple[bool, str]:
    """Test AI connection with current configuration."""
    try:
        ai_client = get_ai_client()
        
        # Simple test
        test_response = ai_client.generate_study_response(
            "Hello, can you help me study?",
            {"materials": []},
            []
        )
        
        if test_response and len(test_response) > 10:
            return True, "AI connection successful!"
        else:
            return False, "AI connection test failed - no response received."
            
    except Exception as e:
        return False, f"AI connection test failed: {str(e)}"

def get_available_models() -> Dict[str, List[str]]:
    """Get available AI models based on installed libraries."""
    models = {}
    
    if GEMINI_AVAILABLE:
        models["Google Gemini"] = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
    
    if OPENAI_AVAILABLE:
        models["OpenAI"] = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    
    return models
