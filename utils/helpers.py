"""
Utility functions for file processing, logging, and data handling
"""
import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import PyPDF2
import pdfplumber
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

def setup_logging():
    """Setup logging directories and configuration"""
    os.makedirs('logs', exist_ok=True)
    return logging.getLogger(__name__)

logger = setup_logging()

class FileProcessor:
    """Handles file processing operations for PDFs and JSON files"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            text_content = ""
            
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content += text + "\n"
            
            # Fallback to PyPDF2 if pdfplumber fails
            if not text_content.strip():
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
            
            logger.info(f"Successfully extracted text from PDF: {file_path}")
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            raise Exception(f"Failed to process PDF file: {str(e)}")
    
    @staticmethod
    def load_json_file(file_path: str) -> Dict[str, Any]:
        """Load and parse JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Successfully loaded JSON file: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {str(e)}")
            raise Exception(f"Failed to load JSON file: {str(e)}")
    
    @staticmethod
    def save_json_file(data: Dict[str, Any], file_path: str) -> None:
        """Save data to JSON file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved JSON file: {file_path}")
        except Exception as e:
            logger.error(f"Error saving JSON file {file_path}: {str(e)}")
            raise Exception(f"Failed to save JSON file: {str(e)}")
    
    def validate_file(self, file_path: str, allowed_extensions: list = None) -> bool:
        """Validate if file exists and has allowed extension"""
        try:
            if not file_path:
                return False
            
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return False
            
            if allowed_extensions:
                file_ext = Path(file_path).suffix.lower()
                if file_ext not in allowed_extensions:
                    logger.error(f"File extension {file_ext} not in allowed extensions: {allowed_extensions}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {str(e)}")
            return False
    
    def read_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Read and parse JSON file"""
        try:
            if not self.validate_file(file_path, ['.json']):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"Successfully read JSON file: {file_path}")
                return data
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {str(e)}")
            return None

class DataValidator:
    """Validates input data and configurations"""
    
    @staticmethod
    def validate_pdf_file(file_path: str) -> bool:
        """Validate PDF file exists and is readable"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        # Check file size (max 10MB)
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        if file_size > 10:
            raise ValueError("PDF file too large (max 10MB)")
        
        return True
    
    @staticmethod
    def validate_json_file(file_path: str) -> bool:
        """Validate JSON file exists and is parseable"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        if not file_path.lower().endswith('.json'):
            raise ValueError("File must be a JSON")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        return True
    
    @staticmethod
    def validate_conversation_params(params: Dict[str, Any]) -> bool:
        """Validate conversation generation parameters"""
        required_fields = ['goal', 'tone', 'exchanges']
        
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required parameter: {field}")
        
        if not isinstance(params['exchanges'], int) or params['exchanges'] < 3:
            raise ValueError("Exchanges must be an integer >= 3")
        
        if params['exchanges'] > 15:
            raise ValueError("Exchanges cannot exceed 15")
        
        return True

def generate_unique_filename(base_name: str, extension: str = ".json") -> str:
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"

def ensure_directory_exists(directory_path: str) -> None:
    """Ensure directory exists, create if not"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)
