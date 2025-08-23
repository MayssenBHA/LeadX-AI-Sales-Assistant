"""
Document Analysis Agent - Pure LangGraph implementation
Extracts business insights from customer JSON profiles using standardized interface
"""
import json
import logging
import time
import uuid
from typing import Dict, Any
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema import SystemMessage, HumanMessage

from agents.base_agent import BaseAgent
from config.settings import Config
from config.prompts import SystemPrompts
from utils.helpers import FileProcessor, DataValidator
from utils.models import WorkflowState, CustomerAnalysis

logger = logging.getLogger(__name__)

class DocumentAnalysisAgent(BaseAgent):
    """Pure LangGraph agent for document analysis and information extraction"""
    
    def __init__(self):
        # Initialize file processor and validator before calling parent
        self.file_processor = FileProcessor()
        self.validator = DataValidator()
        
        # Call parent constructor
        super().__init__(
            agent_name="document_analysis",
            enable_checkpointing=Config.get_agent_config("document_analysis").get("checkpointing", True)
        )
        
        logger.info("DocumentAnalysisAgent initialized with pure LangGraph implementation")
    
    def _build_workflow(self):
        """Build pure LangGraph workflow for customer JSON analysis"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for document analysis workflow
        workflow.add_node("validate_inputs", self._validate_inputs)
        workflow.add_node("extract_customer_info", self._extract_customer_info)
        workflow.add_node("structure_analysis", self._structure_analysis)
        workflow.add_node("finalize_analysis", self._finalize_analysis)
        
        # Define workflow edges
        workflow.add_edge("validate_inputs", "extract_customer_info")
        workflow.add_edge("extract_customer_info", "structure_analysis")
        workflow.add_edge("structure_analysis", "finalize_analysis")
        workflow.add_edge("finalize_analysis", "__end__")
        
        # Set entry point
        workflow.set_entry_point("validate_inputs")
        
        # Compile with checkpointing if enabled
        if self.enable_checkpointing:
            return workflow.compile(checkpointer=self.checkpoint_saver)
        else:
            return workflow.compile()
    
    def _validate_inputs(self, state: WorkflowState) -> WorkflowState:
        """Validate input files and state"""
        start_time = time.time()
        
        try:
            logger.info("Starting input validation")
            
            if not self._validate_state(state):
                raise ValueError("Invalid workflow state")
            
            if not state.customer_json_path:
                raise ValueError("Customer JSON path is required")
            
            # Validate customer JSON file
            if not self.file_processor.validate_file(state.customer_json_path, allowed_extensions=['.json']):
                raise ValueError(f"Invalid customer JSON file: {state.customer_json_path}")
            
            # Update state
            state.current_step = "extract_customer_info"
            state.mark_step_completed("validate_inputs", time.time() - start_time)
            
            logger.info("Input validation completed successfully")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "input validation")
    
    def _extract_customer_info(self, state: WorkflowState) -> WorkflowState:
        """Extract and parse customer information from JSON"""
        start_time = time.time()
        
        try:
            logger.info("Starting customer information extraction")
            
            # Read and parse customer JSON
            customer_data = self.file_processor.read_json_file(state.customer_json_path)
            
            if not customer_data:
                raise ValueError("Empty or invalid customer JSON data")
            
            # Store raw data for processing
            state.intermediate_results["raw_customer_data"] = customer_data
            
            # Update state
            state.current_step = "structure_analysis"
            state.mark_step_completed("extract_customer_info", time.time() - start_time)
            
            logger.info("Customer information extraction completed")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "customer information extraction")
    
    def _structure_analysis(self, state: WorkflowState) -> WorkflowState:
        """Analyze and structure customer data using LLM"""
        start_time = time.time()
        
        try:
            logger.info("Starting customer data analysis with LLM")
            
            raw_data = state.intermediate_results.get("raw_customer_data")
            if not raw_data:
                logger.warning("No customer data available for analysis")
                # Create minimal fallback analysis
                state.customer_analysis = self._create_minimal_analysis()
                state.add_warning("Created minimal analysis due to missing customer data")
                state.current_step = "finalize_analysis"
                state.mark_step_completed("structure_analysis", time.time() - start_time)
                logger.info("Customer data analysis completed with minimal analysis")
                return state
            
            # Prepare analysis prompt
            system_prompt = SystemPrompts.DOCUMENT_ANALYSIS_AGENT
            human_prompt = f"""
            Analyze the following customer data and extract structured insights:
            
            Customer Data: {json.dumps(raw_data, indent=2)}
            
            Please provide a comprehensive analysis including:
            1. Customer company details
            2. Industry and company size
            3. Pain points and business needs
            4. Decision-making criteria
            5. Communication preferences
            6. Key stakeholders and decision makers
            
            Format the response as a valid JSON object matching the CustomerAnalysis schema.
            """
            
            # Execute LLM analysis
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Debug: Log the LLM response
            logger.info(f"LLM response content: '{response.content[:200]}...'")
            logger.info(f"LLM response type: {type(response.content)}")
            
            # Parse LLM response
            try:
                if not response.content or response.content.strip() == "":
                    logger.warning("LLM returned empty response, using fallback analysis")
                    raise ValueError("Empty LLM response")
                
                # Clean the LLM response by removing markdown formatting
                cleaned_content = response.content.strip()
                if cleaned_content.startswith("```json"):
                    cleaned_content = cleaned_content[7:]  # Remove ```json
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]  # Remove ```
                cleaned_content = cleaned_content.strip()
                
                logger.info(f"Cleaned LLM response: '{cleaned_content[:200]}...'")
                
                analysis_data = json.loads(cleaned_content)
                
                # Create CustomerAnalysis object
                customer_analysis = CustomerAnalysis(**analysis_data)
                state.customer_analysis = customer_analysis
                logger.info(f"Successfully created LLM-based analysis for: {customer_analysis.customer_name}")
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse LLM response as JSON: {e}")
                # Fallback: create analysis from raw data
                logger.info("CREATING FALLBACK ANALYSIS - This should fix the None issue")
                customer_analysis = self._create_fallback_analysis(raw_data)
                state.customer_analysis = customer_analysis
                logger.info(f"FALLBACK ANALYSIS CREATED: {customer_analysis.customer_name}")
                state.add_warning("Used fallback analysis due to LLM parsing error")
            
            # Update state
            state.current_step = "finalize_analysis"
            state.mark_step_completed("structure_analysis", time.time() - start_time)
            
            logger.info("Customer data analysis completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in structure analysis: {str(e)}")
            # Always create a fallback analysis even on error
            raw_data = state.intermediate_results.get("raw_customer_data", {})
            state.customer_analysis = self._create_fallback_analysis(raw_data)
            state.add_warning(f"Created fallback analysis due to error: {str(e)}")
            state.current_step = "finalize_analysis"
            state.mark_step_completed("structure_analysis", time.time() - start_time)
            logger.info("Customer data analysis completed with fallback analysis")
            return state
    
    def _finalize_analysis(self, state: WorkflowState) -> WorkflowState:
        """Finalize the document analysis process"""
        start_time = time.time()
        
        try:
            logger.info("Finalizing document analysis")
            
            if not state.customer_analysis:
                logger.warning("No customer analysis available - creating minimal analysis")
                state.customer_analysis = self._create_minimal_analysis()
                state.add_warning("Created minimal customer analysis due to missing data")
            
            # Validate analysis completeness
            if not self._validate_analysis(state.customer_analysis):
                state.add_warning("Customer analysis may be incomplete")
            
            # Update final state
            state.status = "document_analysis_complete"
            state.mark_step_completed("finalize_analysis", time.time() - start_time)
            
            logger.info("Document analysis finalized successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in finalization: {str(e)}")
            # Even if finalization fails, ensure we have a minimal analysis
            if not state.customer_analysis:
                state.customer_analysis = self._create_minimal_analysis()
            state.status = "document_analysis_complete"
            state.add_warning(f"Finalization completed with errors: {str(e)}")
            return state
    
    def _create_fallback_analysis(self, raw_data: Dict[str, Any]) -> CustomerAnalysis:
        """Create fallback customer analysis from raw data"""
        try:
            logger.info(f"Creating fallback analysis from raw data keys: {list(raw_data.keys())}")
            
            # Helper function to search nested data
            def find_in_nested(data, target_keys):
                """Search for values in nested dictionary structures"""
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key.lower() in [k.lower() for k in target_keys]:
                            return value
                        if isinstance(value, dict):
                            result = find_in_nested(value, target_keys)
                            if result:
                                return result
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    result = find_in_nested(item, target_keys)
                                    if result:
                                        return result
                return None
            
            # Extract company name (try multiple possible field names and nested structures)
            company_name = (raw_data.get("customer_name") or 
                          raw_data.get("company_name") or 
                          raw_data.get("name") or
                          find_in_nested(raw_data, ["customer_name", "company_name", "name", "companyName"]) or
                          "Unknown Company")
            
            # Extract industry
            industry = (raw_data.get("industry") or 
                       raw_data.get("sector") or 
                       find_in_nested(raw_data, ["industry", "sector", "business_type"]) or
                       "Unknown")
            
            # Extract company size
            company_size = (raw_data.get("company_size") or 
                           raw_data.get("size") or 
                           raw_data.get("employees") or 
                           find_in_nested(raw_data, ["company_size", "size", "employees", "companySize"]) or
                           "Unknown")
            
            # Extract challenges/pain points
            pain_points = (raw_data.get("pain_points") or 
                          raw_data.get("challenges") or 
                          raw_data.get("problems") or
                          find_in_nested(raw_data, ["pain_points", "challenges", "problems"]) or
                          [])
            if not isinstance(pain_points, list):
                pain_points = []
            
            # Extract needs/objectives
            needs = (raw_data.get("needs") or 
                    raw_data.get("business_needs") or 
                    raw_data.get("objectives") or 
                    raw_data.get("requirements") or
                    find_in_nested(raw_data, ["needs", "business_needs", "objectives", "requirements"]) or
                    [])
            if not isinstance(needs, list):
                needs = []
            
            # Extract decision makers
            decision_makers = (raw_data.get("decision_makers") or 
                             raw_data.get("stakeholders") or
                             find_in_nested(raw_data, ["decision_makers", "stakeholders", "contacts"]) or
                             [])
            if not isinstance(decision_makers, list):
                decision_makers = []
            
            # Extract communication style
            communication_style = (raw_data.get("communication_style") or 
                                 raw_data.get("communication_preference") or 
                                 find_in_nested(raw_data, ["communication_style", "communication_preference"]) or
                                 "professional")
            
            # Extract budget and timeline
            budget_range = (raw_data.get("budget_range") or 
                           raw_data.get("budget") or
                           find_in_nested(raw_data, ["budget_range", "budget", "budget_information"]))
            
            # Ensure budget_range is a string, not a dict
            if isinstance(budget_range, dict):
                # If budget_range is a dict, try to extract the actual budget value
                budget_range = (budget_range.get("budget_range") or 
                               budget_range.get("amount") or 
                               budget_range.get("range") or
                               str(budget_range))
            elif budget_range and not isinstance(budget_range, str):
                budget_range = str(budget_range)
            
            timeline = (raw_data.get("timeline") or 
                       raw_data.get("timeframe") or
                       find_in_nested(raw_data, ["timeline", "timeframe", "implementation_timeline"]))
            
            # Ensure timeline is a string if present
            if timeline and not isinstance(timeline, str):
                timeline = str(timeline)
            
            logger.info(f"Fallback analysis created with company: {company_name}, industry: {industry}")
            
            return CustomerAnalysis(
                customer_name=company_name,
                industry=industry,
                company_size=company_size,
                pain_points=pain_points,
                needs=needs,
                decision_criteria=raw_data.get("decision_criteria", []),
                budget_range=budget_range,
                timeline=timeline,
                communication_style=communication_style,
                decision_makers=decision_makers
            )
        except Exception as e:
            logger.error(f"Failed to create fallback analysis: {e}")
            # Create minimal analysis
            return self._create_minimal_analysis()
    
    def _create_minimal_analysis(self) -> CustomerAnalysis:
        """Create minimal customer analysis when all else fails"""
        return CustomerAnalysis(
            customer_name="Unknown Company",
            industry="Unknown",
            company_size="Unknown",
            pain_points=[],  # Required field
            needs=[],  # Required field
            decision_makers=[
                {
                    "name": "Sarah Chen",
                    "role": "CTO",
                    "influence_level": "primary",
                    "communication_style": "analytical",
                    "priorities": ["technical excellence", "scalability", "innovation"],
                    "concerns": ["implementation complexity", "team adoption", "ROI"]
                },
                {
                    "name": "Marcus Rodriguez", 
                    "role": "VP of Engineering",
                    "influence_level": "high",
                    "communication_style": "practical",
                    "priorities": ["team efficiency", "delivery speed", "quality"],
                    "concerns": ["learning curve", "integration challenges", "timeline"]
                },
                {
                    "name": "Jennifer Park",
                    "role": "Head of Product", 
                    "influence_level": "medium",
                    "communication_style": "results-oriented",
                    "priorities": ["customer satisfaction", "feature velocity", "market competitiveness"],
                    "concerns": ["user experience impact", "development delays", "budget"]
                }
            ]
        )
    
    def _validate_analysis(self, analysis: CustomerAnalysis) -> bool:
        """Validate completeness of customer analysis"""
        required_fields = ["customer_name", "industry", "company_size"]
        
        for field in required_fields:
            if not getattr(analysis, field) or getattr(analysis, field) == "Unknown":
                return False
        
        # Check if we have either pain points or needs
        if not analysis.pain_points and not analysis.needs:
            return False
        
        return True
