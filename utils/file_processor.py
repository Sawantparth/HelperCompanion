import streamlit as st
import PyPDF2
import io
import re
from typing import Optional

class FileProcessor:
    """Handle file processing and text extraction."""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': self.extract_from_pdf,
            'txt': self.extract_from_txt,
            'md': self.extract_from_txt,
            'docx': self.extract_from_docx
        }
    
    def extract_text(self, uploaded_file) -> Optional[str]:
        """Extract text from uploaded file based on its type."""
        try:
            # Get file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension in self.supported_formats:
                extractor = self.supported_formats[file_extension]
                return extractor(uploaded_file)
            else:
                st.error(f"Unsupported file format: {file_extension}")
                return None
                
        except Exception as e:
            st.error(f"Error extracting text from {uploaded_file.name}: {str(e)}")
            return None
    
    def extract_from_pdf(self, uploaded_file) -> str:
        """Extract text from PDF file."""
        try:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return self.clean_text(text)
            
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_from_txt(self, uploaded_file) -> str:
        """Extract text from TXT/MD file."""
        try:
            # Read text file
            text = uploaded_file.read().decode('utf-8')
            return self.clean_text(text)
            
        except UnicodeDecodeError:
            # Try different encodings
            try:
                uploaded_file.seek(0)
                text = uploaded_file.read().decode('latin-1')
                return self.clean_text(text)
            except Exception as e:
                raise Exception(f"Error reading text file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")
    
    def extract_from_docx(self, uploaded_file) -> str:
        """Extract text from DOCX file."""
        try:
            # For now, show info message about DOCX support
            st.info("DOCX support is limited. For best results, please convert to PDF or TXT format.")
            
            # Basic DOCX text extraction (simplified)
            # This is a basic implementation - for full DOCX support, python-docx library would be needed
            content = uploaded_file.read()
            
            # Try to extract readable text (very basic approach)
            text = str(content, errors='ignore')
            
            # Clean up the extracted text
            text = re.sub(r'[^\x20-\x7E\n]', '', text)  # Remove non-printable characters
            text = re.sub(r'\n+', '\n', text)  # Remove multiple newlines
            
            if len(text.strip()) < 100:  # If extraction didn't work well
                st.warning("Text extraction from DOCX may be incomplete. Consider converting to PDF or TXT format.")
                return "DOCX content extraction incomplete. Please convert to PDF or TXT format for better results."
            
            return self.clean_text(text)
            
        except Exception as e:
            raise Exception(f"Error reading DOCX file: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters but keep newlines
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Remove excessive blank lines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def get_text_statistics(self, text: str) -> dict:
        """Get statistics about the extracted text."""
        if not text:
            return {
                'characters': 0,
                'words': 0,
                'lines': 0,
                'paragraphs': 0
            }
        
        return {
            'characters': len(text),
            'words': len(text.split()),
            'lines': len(text.split('\n')),
            'paragraphs': len([p for p in text.split('\n\n') if p.strip()])
        }
    
    def validate_file(self, uploaded_file) -> tuple[bool, str]:
        """Validate uploaded file."""
        if uploaded_file is None:
            return False, "No file provided"
        
        # Check file size (limit to 50MB)
        if uploaded_file.size > 50 * 1024 * 1024:
            return False, "File too large. Maximum size is 50MB."
        
        # Check file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in self.supported_formats:
            return False, f"Unsupported file format: {file_extension}"
        
        return True, "File is valid"
    
    def preview_text(self, text: str, max_length: int = 500) -> str:
        """Get a preview of the extracted text."""
        if not text:
            return "No text content available."
        
        if len(text) <= max_length:
            return text
        
        # Find a good breaking point near the max length
        preview = text[:max_length]
        last_space = preview.rfind(' ')
        last_newline = preview.rfind('\n')
        
        break_point = max(last_space, last_newline)
        if break_point > max_length * 0.8:  # If break point is reasonably close
            preview = text[:break_point]
        
        return preview + "..."
