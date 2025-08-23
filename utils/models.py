"""
Pydantic models for data validation and structure
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ConversationTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CONSULTATIVE = "consultative"

class MessageType(str, Enum):
    INTRO = "Intro"
    FOLLOW_UP = "Follow-up"
    MEETING_REQUEST = "Meeting Request"
    PROPOSAL = "Proposal"
    CLOSING = "Closing"
    OPENING = "opening"
    QUALIFICATION = "qualification"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"

class ConversationChannel(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    LINKEDIN = "linkedin"
    MEETING = "meeting"

class CompanyAnalysis(BaseModel):
    company_name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry sector")
    value_propositions: List[str] = Field(..., description="Key value propositions")
    products_services: List[str] = Field(..., description="Products and services offered")
    competitive_advantages: List[str] = Field(..., description="Competitive advantages")
    target_markets: List[str] = Field(..., description="Target market segments")
    company_culture: str = Field(..., description="Company culture and values")
    messaging_tone: str = Field(..., description="Preferred communication tone")
    key_contacts: List[Dict[str, str]] = Field(default=[], description="Key contact information")

class CustomerAnalysis(BaseModel):
    customer_name: str = Field(..., description="Customer/company name")
    industry: str = Field(..., description="Customer industry")
    company_size: str = Field(..., description="Company size category")
    pain_points: List[Dict[str, Any]] = Field(..., description="Identified pain points with details")
    needs: List[Dict[str, Any]] = Field(..., description="Business needs and requirements with details")
    decision_criteria: List[str] = Field(default=[], description="Decision-making criteria")
    budget_range: Optional[str] = Field(None, description="Budget considerations")
    timeline: Optional[str] = Field(None, description="Implementation timeline")
    communication_style: str = Field(default="professional", description="Preferred communication style")
    decision_makers: List[Dict[str, Any]] = Field(default=[], description="Key decision makers with details")

class ConversationParams(BaseModel):
    goal: str = Field(..., description="Conversation objective")
    tone: ConversationTone = Field(..., description="Conversation tone")
    channel: ConversationChannel = Field(default=ConversationChannel.EMAIL, description="Communication channel")
    exchanges: int = Field(default=6, ge=1, le=15, description="Number of message exchanges")
    company_representative: str = Field(default="Sales Representative", description="Company representative role")
    customer_representative: str = Field(default="Customer", description="Customer representative role")

class Message(BaseModel):
    sender: str = Field(..., description="Message sender (company/customer)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    message_type: str = Field(default="text", description="Type of message")

class Conversation(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation identifier")
    goal: Optional[str] = Field(None, description="Conversation objective")
    channel: ConversationChannel = Field(default=ConversationChannel.EMAIL, description="Communication channel")
    participants: Optional[Dict[str, str]] = Field(None, description="Conversation participants")
    messages: List[Message] = Field(..., description="List of conversation messages")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    status: Optional[str] = Field(default="active", description="Conversation status")

class StrategyAnalysis(BaseModel):
    conversation_id: str = Field(..., description="Associated conversation ID")
    overall_effectiveness: float = Field(..., ge=0, le=10, description="Overall effectiveness score (0-10)")
    methodology_score: float = Field(default=None, description="Methodology score (1-10)")
    positioning_score: float = Field(default=None, description="Positioning score (1-10)")
    value_prop_score: float = Field(default=None, description="Value proposition score (1-10)")
    methodology_assessment: Dict[str, Any] = Field(..., description="Sales methodology evaluation")
    competitive_positioning: Dict[str, Any] = Field(..., description="Competitive positioning analysis")
    objection_handling: Dict[str, Any] = Field(..., description="Objection handling effectiveness")
    value_proposition_delivery: Dict[str, Any] = Field(..., description="Value proposition assessment")
    recommendations: List[str] = Field(..., description="Strategic recommendations")
    improvement_areas: List[str] = Field(..., description="Areas for improvement")
    strengths: List[str] = Field(..., description="Conversation strengths")
    next_steps: List[str] = Field(..., description="Recommended next steps")
    raw_details: Dict[str, Any] = Field(default_factory=dict, description="All raw merged LLM outputs for UI display")

class PersonalityAnalysis(BaseModel):
    conversation_id: str = Field(..., description="Associated conversation ID")
    communication_style: str = Field(..., description="Primary communication style")
    disc_profile: Dict[str, float] = Field(..., description="DISC personality scores")
    decision_making_style: str = Field(..., description="Decision-making approach")
    relationship_orientation: str = Field(..., description="Relationship vs task orientation")
    risk_tolerance: str = Field(..., description="Risk tolerance level")
    information_processing: str = Field(..., description="Information processing preference")
    motivational_drivers: List[str] = Field(..., description="Key motivational factors")
    personality_based_recommendations: List[str] = Field(..., description="Personality-based approach recommendations")
    optimal_communication_approach: Dict[str, str] = Field(..., description="Optimal communication strategies")
    objection_handling_style: str = Field(..., description="Recommended objection handling approach")

class WorkflowState(BaseModel):
    execution_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()), description="Unique execution identifier")
    thread_id: Optional[str] = Field(None, description="Thread ID for checkpointing")
    started_at: datetime = Field(default_factory=datetime.now, description="Execution start time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    max_iterations: int = Field(default=30, description="Maximum allowed workflow iterations to prevent infinite loops")
    company_pdf_path: Optional[str] = None
    customer_json_path: Optional[str] = None
    company_analysis: Optional[CompanyAnalysis] = None
    customer_analysis: Optional[CustomerAnalysis] = None
    conversation_params: Optional[ConversationParams] = None
    conversation: Optional[Conversation] = None
    strategy_analysis: Optional[StrategyAnalysis] = None
    personality_analysis: Optional[PersonalityAnalysis] = None
    completed_steps: List[str] = Field(default=[], description="List of completed workflow steps")
    current_step: str = Field(default="document_analysis", description="Current workflow step")
    errors: List[str] = Field(default=[], description="Error messages during execution")
    warnings: List[str] = Field(default=[], description="Warning messages during execution")
    status: str = Field(default="initialized", description="Workflow status")
    config: Dict[str, Any] = Field(default={}, description="Workflow configuration")
    intermediate_results: Dict[str, Any] = Field(default={}, description="Intermediate results storage")
    step_durations: Dict[str, float] = Field(default={}, description="Duration of each step in seconds")
    total_duration: Optional[float] = Field(None, description="Total execution duration")

    def mark_step_completed(self, step_name: str, duration: Optional[float] = None):
        if step_name not in self.completed_steps:
            self.completed_steps.append(step_name)
        if duration is not None:
            self.step_durations[step_name] = duration
        self.updated_at = datetime.now()

    def add_error(self, error_message: str):
        self.errors.append(f"[{datetime.now().isoformat()}] {error_message}")
        self.updated_at = datetime.now()

    def add_warning(self, warning_message: str):
        self.warnings.append(f"[{datetime.now().isoformat()}] {warning_message}")
        self.updated_at = datetime.now()

    def is_step_completed(self, step_name: str) -> bool:
        return step_name in self.completed_steps

    def get_progress_percentage(self) -> float:
        total_steps = ["document_analysis", "message_composition", "strategy_analysis", "personality_analysis", "integration", "save_outputs"]
        if not total_steps:
            return 0.0
        return (len(self.completed_steps) / len(total_steps)) * 100.0
"""
Pydantic models for data validation and structure
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class ConversationTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CONSULTATIVE = "consultative"

class MessageType(str, Enum):
    INTRO = "Intro"
    FOLLOW_UP = "Follow-up"
    MEETING_REQUEST = "Meeting Request"
    PROPOSAL = "Proposal"
    CLOSING = "Closing"
    OPENING = "opening"
    QUALIFICATION = "qualification"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"

class ConversationChannel(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    LINKEDIN = "linkedin"
    MEETING = "meeting"

class CompanyAnalysis(BaseModel):
    """Structure for company analysis output"""
    company_name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry sector")
    value_propositions: List[str] = Field(..., description="Key value propositions")
    products_services: List[str] = Field(..., description="Products and services offered")
    competitive_advantages: List[str] = Field(..., description="Competitive advantages")
    target_markets: List[str] = Field(..., description="Target market segments")
    company_culture: str = Field(..., description="Company culture and values")
    messaging_tone: str = Field(..., description="Preferred communication tone")
    key_contacts: List[Dict[str, str]] = Field(default=[], description="Key contact information")

class CustomerAnalysis(BaseModel):
    """Structure for customer analysis output"""
    customer_name: str = Field(..., description="Customer/company name")
    industry: str = Field(..., description="Customer industry")
    company_size: str = Field(..., description="Company size category")
    pain_points: List[Dict[str, Any]] = Field(..., description="Identified pain points with details")
    needs: List[Dict[str, Any]] = Field(..., description="Business needs and requirements with details")
    decision_criteria: List[str] = Field(default=[], description="Decision-making criteria")
    budget_range: Optional[str] = Field(None, description="Budget considerations")
    timeline: Optional[str] = Field(None, description="Implementation timeline")
    communication_style: str = Field(default="professional", description="Preferred communication style")
    decision_makers: List[Dict[str, Any]] = Field(default=[], description="Key decision makers with details")

class ConversationParams(BaseModel):
    """Parameters for conversation generation"""
    goal: str = Field(..., description="Conversation objective")
    tone: ConversationTone = Field(..., description="Conversation tone")
    channel: ConversationChannel = Field(default=ConversationChannel.EMAIL, description="Communication channel")
    exchanges: int = Field(default=6, ge=1, le=15, description="Number of message exchanges")
    company_representative: str = Field(default="Sales Representative", description="Company representative role")
    customer_representative: str = Field(default="Customer", description="Customer representative role")

class Message(BaseModel):
    """Individual message in conversation"""
    sender: str = Field(..., description="Message sender (company/customer)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    message_type: str = Field(default="text", description="Type of message")

class Conversation(BaseModel):
    """Complete conversation structure"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    goal: Optional[str] = Field(None, description="Conversation objective")
    channel: ConversationChannel = Field(default=ConversationChannel.EMAIL, description="Communication channel")
    participants: Optional[Dict[str, str]] = Field(None, description="Conversation participants")
    messages: List[Message] = Field(..., description="List of conversation messages")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    status: Optional[str] = Field(default="active", description="Conversation status")

class StrategyAnalysis(BaseModel):
    """Strategy analysis output structure"""
    conversation_id: str = Field(..., description="Associated conversation ID")
    overall_effectiveness: float = Field(..., ge=0, le=10, description="Overall effectiveness score (0-10)")
    methodology_assessment: Dict[str, Any] = Field(..., description="Sales methodology evaluation")
    competitive_positioning: Dict[str, Any] = Field(..., description="Competitive positioning analysis")
    objection_handling: Dict[str, Any] = Field(..., description="Objection handling effectiveness")
    value_proposition_delivery: Dict[str, Any] = Field(..., description="Value proposition assessment")
    recommendations: List[str] = Field(..., description="Strategic recommendations")
    improvement_areas: List[str] = Field(..., description="Areas for improvement")
    strengths: List[str] = Field(..., description="Conversation strengths")
    next_steps: List[str] = Field(..., description="Recommended next steps")
    raw_details: Dict[str, Any] = Field(default_factory=dict, description="All raw merged LLM outputs for UI display")

class PersonalityAnalysis(BaseModel):
    """Personality analysis output structure"""
    conversation_id: str = Field(..., description="Associated conversation ID")
    communication_style: str = Field(..., description="Primary communication style")
    disc_profile: Dict[str, float] = Field(..., description="DISC personality scores")
    decision_making_style: str = Field(..., description="Decision-making approach")
    relationship_orientation: str = Field(..., description="Relationship vs task orientation")
    risk_tolerance: str = Field(..., description="Risk tolerance level")
    information_processing: str = Field(..., description="Information processing preference")
    motivational_drivers: List[str] = Field(..., description="Key motivational factors")
    personality_based_recommendations: List[str] = Field(..., description="Personality-based approach recommendations")
    optimal_communication_approach: Dict[str, str] = Field(..., description="Optimal communication strategies")
    objection_handling_style: str = Field(..., description="Recommended objection handling approach")

class WorkflowState(BaseModel):
    """Enhanced state management for Pure LangGraph workflow with checkpointing support"""
    # Execution metadata
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique execution identifier")
    thread_id: Optional[str] = Field(None, description="Thread ID for checkpointing")
    started_at: datetime = Field(default_factory=datetime.now, description="Execution start time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    max_iterations: int = Field(default=30, description="Maximum allowed workflow iterations to prevent infinite loops")
    
    # Input files
    company_pdf_path: Optional[str] = None
    customer_json_path: Optional[str] = None
    
    # Analysis results
    company_analysis: Optional[CompanyAnalysis] = None
    customer_analysis: Optional[CustomerAnalysis] = None
    conversation_params: Optional[ConversationParams] = None
    conversation: Optional[Conversation] = None
    strategy_analysis: Optional[StrategyAnalysis] = None
    personality_analysis: Optional[PersonalityAnalysis] = None
    
    # Execution tracking
    completed_steps: List[str] = Field(default=[], description="List of completed workflow steps")
    current_step: str = Field(default="document_analysis", description="Current workflow step")
    errors: List[str] = Field(default=[], description="Error messages during execution")
    warnings: List[str] = Field(default=[], description="Warning messages during execution")
    
    # Status and configuration
    status: str = Field(default="initialized", description="Workflow status")
    config: Dict[str, Any] = Field(default={}, description="Workflow configuration")
    intermediate_results: Dict[str, Any] = Field(default={}, description="Intermediate results storage")
    

    # --- Personality Analysis State (ensure persistence across steps) ---
    personality_components: Dict[str, Any] = Field(default_factory=dict, description="Intermediate personality analysis components")
    personality_recommendations: Dict[str, Any] = Field(default_factory=dict, description="Intermediate personality recommendations")

    # Performance metrics
    step_durations: Dict[str, float] = Field(default={}, description="Duration of each step in seconds")
    total_duration: Optional[float] = Field(None, description="Total execution duration")
    
    def mark_step_completed(self, step_name: str, duration: Optional[float] = None):
        """Mark a step as completed"""
        if step_name not in self.completed_steps:
            self.completed_steps.append(step_name)
        
        if duration is not None:
            self.step_durations[step_name] = duration
        
        self.updated_at = datetime.now()
    
    def add_error(self, error_message: str):
        """Add an error message"""
        self.errors.append(f"[{datetime.now().isoformat()}] {error_message}")
        self.updated_at = datetime.now()
    
    def add_warning(self, warning_message: str):
        """Add a warning message"""
        self.warnings.append(f"[{datetime.now().isoformat()}] {warning_message}")
        self.updated_at = datetime.now()
    
    def is_step_completed(self, step_name: str) -> bool:
        """Check if a step has been completed"""
        return step_name in self.completed_steps
    
    def get_progress_percentage(self) -> float:
        """Calculate completion percentage"""
        total_steps = ["document_analysis", "message_composition", "strategy_analysis", "personality_analysis", "integration", "save_outputs"]
        if not total_steps:
            return 0.0
        return (len(self.completed_steps) / len(total_steps)) * 100.0
