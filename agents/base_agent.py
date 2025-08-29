"""
Base Agent Interface for Pure LangGraph Implementation
Provides standardized interface and checkpointing capabilities for all agents
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq

from config.settings import Config
from utils.models import WorkflowState

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all LangGraph agents with standardized interface"""
    
    def __init__(self, agent_name: str, enable_checkpointing: bool = True):
        self.agent_name = agent_name
        self.enable_checkpointing = enable_checkpointing
        
        # Initialize LLM with standard configuration
        self.llm = ChatGroq(
            model=Config.MODEL_NAME,
            groq_api_key=Config.GROQ_API_KEY,
            temperature=Config.TEMPERATURE
        )
        
        # Initialize checkpoint saver if enabled
        self.checkpoint_saver = MemorySaver() if enable_checkpointing else None
        
        # Build agent workflow
        self.workflow = self._build_workflow()
        
        logger.info(f"Initialized {agent_name} with checkpointing={'enabled' if enable_checkpointing else 'disabled'}")
    
    @abstractmethod
    def _build_workflow(self):
        """Build the LangGraph workflow for this agent. Must be implemented by subclasses."""
        pass
    
    def execute(self, state: WorkflowState, config: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """
        Standard execution method for all agents
        
        Args:
            state: Current workflow state
            config: Optional configuration for execution (thread_id, etc.)
            
        Returns:
            Updated workflow state
        """
        try:
            logger.info(f"Starting execution of {self.agent_name}")
            
            # Prepare execution config
            exec_config = config or {}
            if self.enable_checkpointing and "configurable" not in exec_config:
                exec_config["configurable"] = {"thread_id": f"{self.agent_name}_{state.execution_id}"}
            
            # Execute workflow
            result = self.workflow.invoke(state, config=exec_config)
            
            # Convert result back to WorkflowState if needed
            if (hasattr(result, '__class__') and 
                ('AddableValuesDict' in str(result.__class__) or isinstance(result, dict))):
                # LangGraph returned AddableValuesDict or dict, convert back to WorkflowState
                try:
                    # Create a new WorkflowState from the result dict
                    from utils.models import WorkflowState
                    # Convert the dict result to a proper WorkflowState
                    if isinstance(result, dict):
                        # Get all valid WorkflowState field names
                        valid_fields = set(WorkflowState.model_fields.keys())
                        
                        # Filter result dict to only include valid fields
                        state_dict = {}
                        for key, value in result.items():
                            if key in valid_fields:
                                state_dict[key] = value
                        
                        # Add debug logging for customer_analysis
                        if 'customer_analysis' in result:
                            logger.info(f"DEBUG: customer_analysis found in result: {result['customer_analysis']}")
                            logger.info(f"DEBUG: customer_analysis type in result: {type(result['customer_analysis'])}")
                        else:
                            logger.warning("DEBUG: customer_analysis NOT found in result")
                        
                        # Debug: log all available keys
                        logger.info(f"DEBUG: Available keys in result: {list(result.keys())}")
                        logger.info(f"DEBUG: Valid WorkflowState fields: {list(valid_fields)}")
                        logger.info(f"DEBUG: Filtered state_dict keys: {list(state_dict.keys())}")
                        
                        # Create new WorkflowState with the filtered data
                        final_result = WorkflowState(**state_dict)
                        
                        # Verify customer_analysis was preserved
                        logger.info(f"DEBUG: Final result customer_analysis: {final_result.customer_analysis}")
                        logger.info(f"DEBUG: Final result customer_analysis type: {type(final_result.customer_analysis)}")
                    else:
                        final_result = state
                except Exception as conv_error:
                    logger.warning(f"Failed to convert result to WorkflowState: {conv_error}, using original state")
                    # If conversion fails, manually update the original state
                    if isinstance(result, dict):
                        for key, value in result.items():
                            if hasattr(state, key):
                                setattr(state, key, value)
                    final_result = state
            else:
                final_result = result
            
            logger.info(f"Successfully completed execution of {self.agent_name}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in {self.agent_name} execution: {str(e)}")
            state.errors.append(f"{self.agent_name}: {str(e)}")
            return state
    
    async def execute_async(self, state: WorkflowState, config: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """
        Async execution method for all agents
        
        Args:
            state: Current workflow state
            config: Optional configuration for execution
            
        Returns:
            Updated workflow state
        """
        try:
            logger.info(f"Starting async execution of {self.agent_name}")
            
            # Prepare execution config
            exec_config = config or {}
            if self.enable_checkpointing and "configurable" not in exec_config:
                exec_config["configurable"] = {"thread_id": f"{self.agent_name}_{state.execution_id}"}
            
            # Execute workflow asynchronously
            result = await self.workflow.ainvoke(state, config=exec_config)
            
            # Convert result back to WorkflowState if needed
            if hasattr(result, '__class__') and 'AddableValuesDict' in str(result.__class__):
                # LangGraph returned AddableValuesDict, convert back to WorkflowState
                try:
                    # Create a new WorkflowState from the result dict
                    from utils.models import WorkflowState
                    # Convert the dict result to a proper WorkflowState
                    if isinstance(result, dict):
                        # Filter out any keys that aren't WorkflowState fields
                        state_dict = {}
                        for key, value in result.items():
                            if hasattr(WorkflowState, key):
                                state_dict[key] = value
                        
                        # Create new WorkflowState with the filtered data
                        final_result = WorkflowState(**state_dict)
                    else:
                        final_result = state
                except Exception as conv_error:
                    logger.warning(f"Failed to convert async result to WorkflowState: {conv_error}, using original state")
                    # If conversion fails, manually update the original state
                    if isinstance(result, dict):
                        for key, value in result.items():
                            if hasattr(state, key):
                                setattr(state, key, value)
                    final_result = state
            else:
                final_result = result
            
            logger.info(f"Successfully completed async execution of {self.agent_name}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in {self.agent_name} async execution: {str(e)}")
            state.errors.append(f"{self.agent_name}: {str(e)}")
            return state
    
    def get_workflow_state(self, thread_id: str) -> Optional[WorkflowState]:
        """Get current state from checkpoint if available"""
        if not self.enable_checkpointing or not self.checkpoint_saver:
            return None
        
        try:
            checkpoint = self.checkpoint_saver.get({"configurable": {"thread_id": thread_id}})
            return checkpoint.state if checkpoint else None
        except Exception as e:
            logger.warning(f"Could not retrieve checkpoint for {thread_id}: {str(e)}")
            return None
    
    def resume_from_checkpoint(self, thread_id: str, state: WorkflowState) -> WorkflowState:
        """Resume execution from a checkpoint"""
        if not self.enable_checkpointing:
            logger.warning(f"Checkpointing not enabled for {self.agent_name}")
            return self.execute(state)
        
        try:
            config = {"configurable": {"thread_id": thread_id}}
            result = self.workflow.invoke(state, config=config)
            logger.info(f"Successfully resumed {self.agent_name} from checkpoint {thread_id}")
            return result
        except Exception as e:
            logger.error(f"Error resuming {self.agent_name} from checkpoint: {str(e)}")
            state.errors.append(f"{self.agent_name} resume: {str(e)}")
            return state
    
    def _validate_state(self, state: WorkflowState) -> bool:
        """Validate state before processing. Override in subclasses for specific validation."""
        if not state:
            logger.error(f"{self.agent_name}: Invalid state - state is None")
            return False
        
        # execution_id is now auto-generated, so we don't need to check for it
        # Just ensure it exists (it should due to default_factory)
        if not hasattr(state, 'execution_id'):
            logger.error(f"{self.agent_name}: Invalid state - missing execution_id")
            return False
        
        return True
    
    def _handle_error(self, state: WorkflowState, error: Exception, context: str) -> WorkflowState:
        """Standard error handling for all agents"""
        error_msg = f"{self.agent_name} - {context}: {str(error)}"
        logger.error(error_msg)
        state.errors.append(error_msg)
        return state
