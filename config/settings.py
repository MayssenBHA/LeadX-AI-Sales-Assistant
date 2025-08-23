"""
Configuration settings for the B2B Sales Conversation Generator
Pure LangGraph Implementation with Checkpointing Support
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

class Config:
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = "llama-3.1-8b-instant"  # Faster and uses fewer tokens
    
    # Application Settings
    MAX_TOKENS = 4096  # Reduced token limit
    TEMPERATURE = 0.7
    
    # File Settings
    MAX_FILE_SIZE_MB = 10
    ALLOWED_PDF_EXTENSIONS = ['.pdf']
    ALLOWED_JSON_EXTENSIONS = ['.json']
    
    # Conversation Settings
    DEFAULT_EXCHANGES = 6
    MIN_EXCHANGES = 3
    MAX_EXCHANGES = 15
    
    # Output Directories
    OUTPUT_DIR = "data/outputs"
    TEMP_DIR = "data/temp"
    LOGS_DIR = "logs"
    
    # LangGraph Configuration
    ENABLE_CHECKPOINTING = True
    CHECKPOINT_NAMESPACE = "b2b_sales_workflow"
    PARALLEL_EXECUTION = True
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    
    # Agent Configuration
    AGENT_CONFIGS = {
        "document_analysis": {
            "enabled": True,
            "checkpointing": True,
            "timeout": 300,  # 5 minutes
            "max_retries": 2
        },
        "message_composer": {
            "enabled": True,
            "checkpointing": True,
            "timeout": 600,  # 10 minutes
            "max_retries": 3
        },
        "strategy_analysis": {
            "enabled": True,
            "checkpointing": True,
            "timeout": 300,  # 5 minutes
            "max_retries": 2
        },
        "personality_analysis": {
            "enabled": True,
            "checkpointing": True,
            "timeout": 300,  # 5 minutes
            "max_retries": 2
        }
    }
    
    # Workflow Configuration
    WORKFLOW_CONFIG = {
        "enable_parallel_analysis": True,
        "save_intermediate_results": True,
        "auto_retry_failed_steps": True,
        "checkpoint_frequency": "step"  # "step" or "node"
    }
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")
        return True
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        return cls.AGENT_CONFIGS.get(agent_name, {
            "enabled": True,
            "checkpointing": cls.ENABLE_CHECKPOINTING,
            "timeout": 300,
            "max_retries": 2
        })
    
    @classmethod
    def get_workflow_config(cls) -> Dict[str, Any]:
        """Get workflow-level configuration"""
        return cls.WORKFLOW_CONFIG.copy()
