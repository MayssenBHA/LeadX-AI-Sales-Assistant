"""
Pure LangGraph B2B Sales Workflow Implementation
Orchestrates the entire B2B sales conversation generation and analysis process using standardized agent interfaces
"""
import logging
import asyncio
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from agents.document_analysis_agent import DocumentAnalysisAgent
from agents.message_composer_agent_pure import MessageComposerAgentPure
from agents.strategy_agent_pure import StrategyAgentPure
from agents.personality_classifier_agent_pure import PersonalityClassifierAgentPure
from utils.models import WorkflowState, ConversationParams
from utils.helpers import FileProcessor, generate_unique_filename, ensure_directory_exists
from config.settings import Config

logger = logging.getLogger(__name__)

class PureLangGraphB2BWorkflow:
    """Pure LangGraph implementation for B2B sales conversation generation workflow"""
    
    def __init__(self):
        logger.info("Initializing Pure LangGraph B2B Sales Workflow")
        
        # Initialize agents with standardized interface
        self.document_agent = DocumentAnalysisAgent()
        self.message_composer_agent = MessageComposerAgentPure()
        self.strategy_agent = StrategyAgentPure()
        self.personality_agent = PersonalityClassifierAgentPure()
        
        # Initialize utilities
        self.file_processor = FileProcessor()
        
        # Initialize checkpoint saver for main workflow
        self.checkpoint_saver = MemorySaver() if Config.ENABLE_CHECKPOINTING else None
        
        # Build main workflow
        self.workflow = self._build_main_workflow()
        
        logger.info("Pure LangGraph B2B Sales Workflow initialized successfully")
    
    def _build_main_workflow(self):
        """Build the main LangGraph workflow orchestrating all agents"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each major step
        workflow.add_node("initialize_execution", self._initialize_execution)
        workflow.add_node("document_analysis", self._run_document_analysis)
        workflow.add_node("message_composition", self._run_message_composition)
        workflow.add_node("parallel_analysis", self._run_parallel_analysis)
        workflow.add_node("integrate_results", self._integrate_results)
        workflow.add_node("save_outputs", self._save_outputs)
        workflow.add_node("finalize_workflow", self._finalize_workflow)
        
        # Add edges for sequential flow
        workflow.add_edge("initialize_execution", "document_analysis")
        workflow.add_edge("document_analysis", "message_composition")
        workflow.add_edge("message_composition", "parallel_analysis")
        workflow.add_edge("parallel_analysis", "integrate_results")
        workflow.add_edge("integrate_results", "save_outputs")
        workflow.add_edge("save_outputs", "finalize_workflow")
        workflow.add_edge("finalize_workflow", "__end__")
        
        # Set entry point
        workflow.set_entry_point("initialize_execution")
        
        # Compile with checkpointing if enabled
        if self.checkpoint_saver:
            return workflow.compile(checkpointer=self.checkpoint_saver)
        else:
            return workflow.compile()
    
    def _initialize_execution(self, state: WorkflowState) -> WorkflowState:
        """Initialize workflow execution with unique identifiers and metadata"""
        start_time = time.time()
        
        try:
            logger.info("Initializing workflow execution")
            
            # Generate execution ID if not provided
            if not hasattr(state, 'execution_id') or not state.execution_id:
                state.execution_id = str(uuid.uuid4())
            
            # Set thread ID for checkpointing
            if not state.thread_id:
                state.thread_id = f"b2b_workflow_{state.execution_id}"
            
            # Initialize timestamps
            state.started_at = datetime.now()
            state.updated_at = datetime.now()
            
            # Set initial status
            state.status = "initialized"
            state.current_step = "document_analysis"
            
            # Mark step completed
            state.mark_step_completed("initialize_execution", time.time() - start_time)
            
            logger.info(f"Workflow execution initialized with ID: {state.execution_id}")
            return state
            
        except Exception as e:
            logger.error(f"Error initializing workflow execution: {e}")
            state.add_error(f"Initialization error: {str(e)}")
            return state
    
    def _run_document_analysis(self, state: WorkflowState) -> WorkflowState:
        """Execute document analysis agent using standardized interface"""
        start_time = time.time()
        
        try:
            logger.info("Starting document analysis phase")
            
            # Configure execution
            config = {
                "configurable": {
                    "thread_id": f"{state.thread_id}_document_analysis"
                }
            }
            
            # Execute document analysis agent
            state = self.document_agent.execute(state, config)
            
            # Update workflow state
            state.current_step = "message_composition"
            state.mark_step_completed("document_analysis", time.time() - start_time)
            
            logger.info("Document analysis phase completed")
            return state
            
        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            state.add_error(f"Document analysis error: {str(e)}")
            return state
    
    def _run_message_composition(self, state: WorkflowState) -> WorkflowState:
        """Execute message composition agent using standardized interface"""
        start_time = time.time()
        
        try:
            logger.info("Starting message composition phase")
            
            # Validate prerequisites
            if not state.customer_analysis:
                raise ValueError("Customer analysis is required for message composition")
            
            # Configure execution
            config = {
                "configurable": {
                    "thread_id": f"{state.thread_id}_message_composition"
                }
            }
            
            # Execute message composition agent
            state = self.message_composer_agent.execute(state, config)
            
            # Update workflow state
            state.current_step = "parallel_analysis"
            state.mark_step_completed("message_composition", time.time() - start_time)
            
            logger.info("Message composition phase completed")
            return state
            
        except Exception as e:
            logger.error(f"Error in message composition: {e}")
            state.add_error(f"Message composition error: {str(e)}")
            return state
    
    def _run_parallel_analysis(self, state: WorkflowState) -> WorkflowState:
        """Execute strategy and personality analysis in parallel"""
        start_time = time.time()
        
        try:
            logger.info("Starting parallel analysis phase")
            
            # Validate prerequisites
            if not state.conversation:
                raise ValueError("Conversation is required for analysis")
            
            if Config.WORKFLOW_CONFIG.get("enable_parallel_analysis", True):
                # Run analyses in parallel using asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    state = loop.run_until_complete(self._run_parallel_analysis_async(state))
                finally:
                    loop.close()
            else:
                # Run analyses sequentially
                state = self._run_sequential_analysis(state)
            
            # Update workflow state
            state.current_step = "integrate_results"
            state.mark_step_completed("parallel_analysis", time.time() - start_time)
            
            logger.info("Parallel analysis phase completed")
            return state
            
        except Exception as e:
            logger.error(f"Error in parallel analysis: {e}")
            state.add_error(f"Parallel analysis error: {str(e)}")
            return state
    
    async def _run_parallel_analysis_async(self, state: WorkflowState) -> WorkflowState:
        """Run strategy and personality analysis asynchronously"""
        logger.info("Running strategy and personality analysis in parallel")
        
        # Configure execution for both agents
        strategy_config = {
            "configurable": {
                "thread_id": f"{state.thread_id}_strategy_analysis"
            }
        }
        
        personality_config = {
            "configurable": {
                "thread_id": f"{state.thread_id}_personality_analysis"
            }
        }
        
        # Create async wrapper functions for synchronous execute methods
        async def run_strategy():
            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.strategy_agent.execute, state.model_copy(), strategy_config)
        
        async def run_personality():
            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.personality_agent.execute, state.model_copy(), personality_config)
        
        # Create tasks for parallel execution
        strategy_task = asyncio.create_task(run_strategy())
        personality_task = asyncio.create_task(run_personality())
        
        # Wait for both analyses to complete
        strategy_result, personality_result = await asyncio.gather(
            strategy_task, 
            personality_task,
            return_exceptions=True
        )
        
        # Handle results and errors
        if isinstance(strategy_result, Exception):
            logger.error(f"Strategy analysis failed: {strategy_result}")
            state.add_error(f"Strategy analysis error: {str(strategy_result)}")
        else:
            state.strategy_analysis = strategy_result.strategy_analysis
        
        if isinstance(personality_result, Exception):
            logger.error(f"Personality analysis failed: {personality_result}")
            state.add_error(f"Personality analysis error: {str(personality_result)}")
        else:
            state.personality_analysis = personality_result.personality_analysis
        
        return state
    
    def _run_sequential_analysis(self, state: WorkflowState) -> WorkflowState:
        """Run strategy and personality analysis sequentially"""
        logger.info("Running strategy and personality analysis sequentially")
        
        # Strategy analysis
        try:
            strategy_config = {
                "configurable": {
                    "thread_id": f"{state.thread_id}_strategy_analysis"
                }
            }
            strategy_result = self.strategy_agent.execute(state, strategy_config)
            state.strategy_analysis = strategy_result.strategy_analysis
        except Exception as e:
            logger.error(f"Strategy analysis failed: {e}")
            state.add_error(f"Strategy analysis error: {str(e)}")
        
        # Personality analysis
        try:
            personality_config = {
                "configurable": {
                    "thread_id": f"{state.thread_id}_personality_analysis"
                }
            }
            personality_result = self.personality_agent.execute(state, personality_config)
            state.personality_analysis = personality_result.personality_analysis
        except Exception as e:
            logger.error(f"Personality analysis failed: {e}")
            state.add_error(f"Personality analysis error: {str(e)}")
        
        return state
    
    def _integrate_results(self, state: WorkflowState) -> WorkflowState:
        """Integrate all analysis results and prepare final output"""
        start_time = time.time()
        
        try:
            logger.info("Integrating workflow results")
            
            # Validate core results
            missing_components = []
            if not state.customer_analysis:
                missing_components.append("customer_analysis")
            if not state.conversation:
                missing_components.append("conversation")
            
            if missing_components:
                state.add_warning(f"Missing components: {', '.join(missing_components)}")
            
            # Create comprehensive results summary
            results_summary = {
                "execution_id": state.execution_id,
                "workflow_status": "completed" if not state.errors else "completed_with_errors",
                "execution_time": time.time() - state.started_at.timestamp(),
                "completed_steps": state.completed_steps,
                "step_durations": state.step_durations,
                "errors": state.errors,
                "warnings": state.warnings,
                "components": {
                    "customer_analysis": bool(state.customer_analysis),
                    "conversation": bool(state.conversation),
                    "strategy_analysis": bool(state.strategy_analysis),
                    "personality_analysis": bool(state.personality_analysis)
                }
            }
            
            state.intermediate_results["workflow_summary"] = results_summary
            
            # Update workflow state
            state.current_step = "save_outputs"
            state.mark_step_completed("integrate_results", time.time() - start_time)
            
            logger.info("Results integration completed")
            return state
            
        except Exception as e:
            logger.error(f"Error integrating results: {e}")
            state.add_error(f"Results integration error: {str(e)}")
            return state
    
    def _save_outputs(self, state: WorkflowState) -> WorkflowState:
        """Save workflow outputs to files"""
        start_time = time.time()
        
        try:
            logger.info("Saving workflow outputs")
            
            # Ensure output directory exists
            ensure_directory_exists(Config.OUTPUT_DIR)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"b2b_sales_workflow_{timestamp}_complete_results.json"
            output_path = f"{Config.OUTPUT_DIR}/{filename}"
            
            # Prepare complete output data
            output_data = {
                "execution_metadata": {
                    "execution_id": state.execution_id,
                    "thread_id": state.thread_id,
                    "started_at": state.started_at.isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "total_duration": time.time() - state.started_at.timestamp(),
                    "status": "completed" if not state.errors else "completed_with_errors"
                },
                "input_files": {
                    "customer_json_path": state.customer_json_path,
                    "company_pdf_path": state.company_pdf_path
                },
                "analysis_results": {
                    "customer_analysis": state.customer_analysis.dict() if state.customer_analysis else None,
                    "conversation": state.conversation.dict() if state.conversation else None,
                    "strategy_analysis": state.strategy_analysis.dict() if state.strategy_analysis else None,
                    "personality_analysis": state.personality_analysis.dict() if state.personality_analysis else None
                },
                "execution_details": {
                    "completed_steps": state.completed_steps,
                    "step_durations": state.step_durations,
                    "errors": state.errors,
                    "warnings": state.warnings,
                    "workflow_summary": state.intermediate_results.get("workflow_summary", {})
                }
            }
            
            # Save to file
            self.file_processor.save_json_file(output_data, output_path)
            
            # Update state with output information
            state.intermediate_results["output_path"] = output_path
            state.intermediate_results["output_filename"] = filename
            
            # Update workflow state
            state.current_step = "finalize_workflow"
            state.mark_step_completed("save_outputs", time.time() - start_time)
            
            logger.info(f"Workflow outputs saved to: {output_path}")
            return state
            
        except Exception as e:
            logger.error(f"Error saving outputs: {e}")
            state.add_error(f"Output saving error: {str(e)}")
            return state
    
    def _finalize_workflow(self, state: WorkflowState) -> WorkflowState:
        """Finalize workflow execution"""
        try:
            logger.info("Finalizing workflow execution")
            
            # Calculate final metrics
            state.total_duration = time.time() - state.started_at.timestamp()
            state.updated_at = datetime.now()
            
            # Set final status
            if state.errors:
                state.status = "completed_with_errors"
            else:
                state.status = "completed_successfully"
            
            logger.info(f"Workflow execution finalized with status: {state.status}")
            logger.info(f"Total execution time: {state.total_duration:.2f} seconds")
            logger.info(f"Completed steps: {len(state.completed_steps)}")
            
            if state.errors:
                logger.warning(f"Errors encountered: {len(state.errors)}")
            if state.warnings:
                logger.warning(f"Warnings generated: {len(state.warnings)}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error finalizing workflow: {e}")
            state.add_error(f"Workflow finalization error: {str(e)}")
            state.status = "finalization_error"
            return state
    
    def execute_complete_workflow(
        self, 
        customer_json_path: str,
        conversation_params: Optional[ConversationParams] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> WorkflowState:
        """
        Execute the complete B2B sales workflow
        
        Args:
            customer_json_path: Path to customer JSON file
            conversation_params: Optional conversation parameters
            config: Optional workflow configuration
            
        Returns:
            Final workflow state with all results
        """
        try:
            logger.info("Starting complete B2B sales workflow execution")
            
            # Initialize state
            execution_id = str(uuid.uuid4())
            initial_state = WorkflowState(
                execution_id=execution_id,
                customer_json_path=customer_json_path,
                conversation_params=conversation_params,
                status="starting",
                config=config or {}
            )
            
            # Prepare execution config
            exec_config = {
                "configurable": {
                    "thread_id": f"b2b_workflow_{execution_id}"
                }
            }
            
            # Execute workflow
            final_state = self.workflow.invoke(initial_state, config=exec_config)
            
            logger.info(f"Complete workflow execution finished with status: {final_state.status}")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            error_state = WorkflowState(
                execution_id=str(uuid.uuid4()),
                customer_json_path=customer_json_path,
                status="execution_error"
            )
            error_state.add_error(f"Workflow execution error: {str(e)}")
            return error_state
    
    def resume_workflow_from_checkpoint(self, thread_id: str) -> Optional[WorkflowState]:
        """Resume workflow execution from a checkpoint"""
        if not self.checkpoint_saver:
            logger.warning("Checkpointing not enabled, cannot resume from checkpoint")
            return None
        
        try:
            logger.info(f"Attempting to resume workflow from checkpoint: {thread_id}")
            
            # Get checkpoint
            checkpoint = self.checkpoint_saver.get({"configurable": {"thread_id": thread_id}})
            
            if not checkpoint:
                logger.warning(f"No checkpoint found for thread_id: {thread_id}")
                return None
            
            # Resume execution
            config = {"configurable": {"thread_id": thread_id}}
            final_state = self.workflow.invoke(checkpoint.values, config=config)
            
            logger.info(f"Successfully resumed workflow from checkpoint")
            return final_state
            
        except Exception as e:
            logger.error(f"Error resuming workflow from checkpoint: {e}")
            return None
    
    def run_document_analysis_only(self, customer_json_path: str) -> WorkflowState:
        """Run ONLY the document analysis step - for initial customer data processing"""
        try:
            logger.info("Starting document analysis only (customer JSON)")
            
            # Initialize state with minimal parameters
            conversation_params = ConversationParams(
                goal="Initial customer analysis",
                tone="professional",
                channel="email"
            )
            
            state = WorkflowState(
                customer_json_path=customer_json_path,
                conversation_params=conversation_params,
                status="initialized",
                current_step="document_analysis_only"
            )
            
            # Run just the document analysis agent
            config = {
                "configurable": {
                    "thread_id": f"{state.thread_id}_document_analysis_only"
                }
            }
            
            # Execute document analysis agent directly
            state = self.document_agent.execute(state, config)
            
            if state.status != "error":
                state.status = "document_analysis_complete"
                state.current_step = "awaiting_channel_selection"
                logger.info("Document analysis completed - ready for channel/type selection")
            
            return state
            
        except Exception as e:
            logger.error(f"Document analysis error: {str(e)}")
            error_state = WorkflowState(
                status="error",
                errors=[f"Document analysis error: {str(e)}"]
            )
            return error_state
    
    def run_conversation_generation(self, state: WorkflowState, conversation_params: ConversationParams) -> WorkflowState:
        """Run message composition + analysis after channel/type selection"""
        try:
            logger.info("Starting conversation generation with selected parameters")
            
            # Update conversation parameters
            state.conversation_params = conversation_params
            state.current_step = "conversation_generation"
            
            # Run the workflow starting from message composition
            # Update the state with conversation parameters
            state.updated_at = datetime.now()
            
            # Configure execution
            config = {
                "configurable": {
                    "thread_id": f"{state.thread_id}_conversation_generation"
                }
            }
            
            # Run message composition
            start_time = time.time()
            state = self.message_composer_agent.execute(state, config)
            state.mark_step_completed("message_composition", time.time() - start_time)
            
            if state.status == "error":
                return state
            
            # Run parallel analysis if conversation was generated successfully
            if state.conversation and state.conversation.messages:
                # Strategy analysis
                try:
                    strategy_config = {
                        "configurable": {
                            "thread_id": f"{state.thread_id}_strategy_analysis"
                        }
                    }
                    strategy_result = self.strategy_agent.execute(state, strategy_config)
                    state.strategy_analysis = strategy_result.strategy_analysis
                except Exception as e:
                    logger.error(f"Strategy analysis failed: {e}")
                    state.add_error(f"Strategy analysis error: {str(e)}")
                
                # Personality analysis
                try:
                    personality_config = {
                        "configurable": {
                            "thread_id": f"{state.thread_id}_personality_analysis"
                        }
                    }
                    personality_result = self.personality_agent.execute(state, personality_config)
                    state.personality_analysis = personality_result.personality_analysis
                except Exception as e:
                    logger.error(f"Personality analysis failed: {e}")
                    state.add_error(f"Personality analysis error: {str(e)}")
            
            # Mark as complete
            state.status = "conversation_complete"
            state.current_step = "completed"
            state.updated_at = datetime.now()
            
            logger.info(f"Conversation generation completed with status: {state.status}")
            return state
            
        except Exception as e:
            logger.error(f"Conversation generation error: {str(e)}")
            state.errors.append(str(e))
            state.status = "conversation_error"
            return state

# Maintain backward compatibility
class B2BSalesWorkflow(PureLangGraphB2BWorkflow):
    """Backward compatibility alias for the pure LangGraph workflow"""
    pass
