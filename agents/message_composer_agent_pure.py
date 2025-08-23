"""
Message Composer Agent - Pure LangGraph implementation  
Generates realistic B2B sales conversations between Talan Tunisie and clients
"""
import json
import logging
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime
from langgraph.graph import StateGraph
from langchain.schema import SystemMessage, HumanMessage

from agents.base_agent import BaseAgent
from config.settings import Config
from config.prompts import SystemPrompts
from config.talan_config import TALAN_COMPANY_INFO, MESSAGE_FORMATS, MESSAGE_TYPES
from utils.models import WorkflowState, Conversation, Message, ConversationParams, ConversationTone, ConversationChannel

logger = logging.getLogger(__name__)


class MessageComposerAgentPure(BaseAgent):
    """Pure LangGraph agent for generating B2B sales conversations"""
    def __init__(self, mode: str = "full"):
        # mode: 'talan_only', 'customer_only', 'full'
        self.mode = mode
        super().__init__(
            agent_name="message_composer",
            enable_checkpointing=Config.get_agent_config("message_composer").get("checkpointing", True)
        )
        logger.info(f"MessageComposerAgent initialized with pure LangGraph implementation (mode={self.mode})")

    def _build_workflow(self):
        """Build pure LangGraph workflow for message composition"""
        workflow = StateGraph(WorkflowState)

        # Always add the core nodes
        workflow.add_node("validate_inputs", self._validate_inputs)
        workflow.add_node("initialize_conversation", self._initialize_conversation)
        workflow.add_node("determine_message_type", self._determine_message_type)
        workflow.add_node("generate_talan_message", self._generate_talan_message)

        # Only add customer response and further nodes if needed
        if self.mode in ("customer_only", "full"):
            workflow.add_node("generate_customer_response", self._generate_customer_response)
        if self.mode == "full":
            workflow.add_node("check_completion", self._check_completion)
            workflow.add_node("finalize_conversation", self._finalize_conversation)

        # Workflow edges
        workflow.add_edge("validate_inputs", "initialize_conversation")
        workflow.add_edge("initialize_conversation", "determine_message_type")
        workflow.add_edge("determine_message_type", "generate_talan_message")

        if self.mode == "talan_only":
            workflow.add_edge("generate_talan_message", "__end__")
        elif self.mode == "customer_only":
            workflow.add_edge("generate_talan_message", "generate_customer_response")
            workflow.add_edge("generate_customer_response", "__end__")
        else:  # full conversation
            workflow.add_edge("generate_talan_message", "generate_customer_response")
            workflow.add_edge("generate_customer_response", "check_completion")
            workflow.add_conditional_edges(
                "check_completion",
                self._should_continue_conversation,
                {
                    "continue": "determine_message_type",
                    "complete": "finalize_conversation"
                }
            )
            workflow.add_edge("finalize_conversation", "__end__")

        workflow.set_entry_point("validate_inputs")

        # Compile with checkpointing if enabled
        if self.enable_checkpointing:
            return workflow.compile(checkpointer=self.checkpoint_saver)
        else:
            return workflow.compile()
    
    def _validate_inputs(self, state: WorkflowState) -> WorkflowState:
        """Validate required inputs"""
        start_time = time.time()
        
        try:
            logger.info("Starting message composer input validation")
            
            if not self._validate_state(state):
                raise ValueError("Invalid workflow state")
            
            if not state.customer_analysis:
                raise ValueError("Customer analysis required for message composition")
            
            if not state.conversation_params:
                # Create default parameters
                state.conversation_params = ConversationParams(
                    goal="Explore business opportunities with Talan solutions",
                    tone=ConversationTone.PROFESSIONAL,
                    channel=ConversationChannel.EMAIL,
                    exchanges=4,
                    company_representative="Talan Sales Representative",
                    customer_representative=f"{state.customer_analysis.customer_name} Representative"
                )
            
            # Update state
            state.current_step = "initialize_conversation"
            state.mark_step_completed("validate_inputs", time.time() - start_time)
            
            logger.info("Message composer inputs validated successfully")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "input validation")
    
    def _initialize_conversation(self, state: WorkflowState) -> WorkflowState:
        """Initialize or continue existing conversation"""
        start_time = time.time()
        
        try:
            logger.info("Initializing conversation")
            
            if state.conversation and state.conversation.messages:
                # Continue existing conversation
                logger.info(f"Continuing conversation with {len(state.conversation.messages)} existing messages")
            else:
                # Create new conversation
                conversation_id = str(uuid.uuid4())
                participants = {
                    "company": state.conversation_params.company_representative,
                    "customer": state.conversation_params.customer_representative
                }
                
                state.conversation = Conversation(
                    conversation_id=conversation_id,
                    goal=state.conversation_params.goal,
                    channel=state.conversation_params.channel,
                    participants=participants,
                    messages=[],
                    metadata={
                        "company_name": TALAN_COMPANY_INFO["name"],
                        "customer_name": state.customer_analysis.customer_name,
                        "tone": str(state.conversation_params.tone),
                        "channel": str(state.conversation_params.channel),
                        "target_exchanges": state.conversation_params.exchanges,
                        "created_at": datetime.now().isoformat()
                    }
                )
                
                logger.info("New conversation initialized")
            
            # Always initialize iteration_count if not present
            if "iteration_count" not in state.intermediate_results:
                state.intermediate_results["iteration_count"] = 0
            # Update state
            state.current_step = "determine_message_type"
            state.mark_step_completed("initialize_conversation", time.time() - start_time)
            return state
        except Exception as e:
            return self._handle_error(state, e, "conversation initialization")
    
    def _determine_message_type(self, state: WorkflowState) -> WorkflowState:
        """Determine next message type based on conversation flow"""
        start_time = time.time()
        
        try:
            logger.info("Determining message type")
            
            company_messages = [msg for msg in state.conversation.messages if msg.sender == "company"]
            
            if len(company_messages) == 0:
                message_type = "opening"
            elif len(company_messages) == 1:
                message_type = "follow_up"
            elif len(company_messages) == 2:
                message_type = "qualification"
            else:
                message_type = "presentation"
            
            # Store in intermediate results
            state.intermediate_results["current_message_type"] = message_type
            
            # Update state
            state.current_step = "generate_talan_message"
            state.mark_step_completed("determine_message_type", time.time() - start_time)
            
            logger.info(f"Determined message type: {message_type}")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "message type determination")
    
    def _generate_talan_message(self, state: WorkflowState) -> WorkflowState:
        """Generate Talan message using specialized prompts"""
        start_time = time.time()
        
        try:
            logger.info("Generating Talan message")
            
            message_type = state.intermediate_results.get("current_message_type", "follow_up")
            
            # Get relevant Talan services for this client
            relevant_services = self._get_talan_services_for_client(state.customer_analysis)
            
            # Build context-aware prompt
            prompt = self._build_talan_message_prompt(state, message_type, relevant_services)
            
            # Generate message
            messages = [
                SystemMessage(content=SystemPrompts.TALAN_MESSAGE_GENERATOR),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Create message object
            message = Message(
                sender="company",
                content=response.content.strip(),
                timestamp=datetime.now(),
                message_type=message_type
            )
            
            state.conversation.messages.append(message)
            
            # Update state
            state.current_step = "generate_customer_response"
            state.mark_step_completed("generate_talan_message", time.time() - start_time)
            
            logger.info(f"Generated Talan {message_type} message")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Talan message generation")
    
    def _generate_customer_response(self, state: WorkflowState) -> WorkflowState:
        """Generate customer response"""
        start_time = time.time()
        
        try:
            logger.info("Generating customer response")
            
            # Build customer response prompt
            prompt = self._build_customer_response_prompt(state)
            
            # Generate response
            messages = [
                SystemMessage(content=SystemPrompts.CUSTOMER_RESPONSE_SYSTEM),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Create message object
            message = Message(
                sender="customer",
                content=response.content.strip(),
                timestamp=datetime.now(),
                message_type="response"
            )
            
            state.conversation.messages.append(message)
            
            # Update state
            state.current_step = "check_completion"
            state.mark_step_completed("generate_customer_response", time.time() - start_time)
            
            logger.info("Generated customer response")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "customer response generation")
    
    def _check_completion(self, state: WorkflowState) -> WorkflowState:
        """Check if conversation should continue"""
        start_time = time.time()
        
        try:
            logger.info("Checking conversation completion")
            target_messages = state.conversation_params.exchanges * 2  # Company + Customer pairs
            if state.conversation and state.conversation.messages is not None:
                current_messages = len(state.conversation.messages)
            else:
                current_messages = 0
            # Track workflow iterations
            iteration_count = state.intermediate_results.get("iteration_count", 0) + 1
            state.intermediate_results["iteration_count"] = iteration_count
            logger.info(f"Iteration: {iteration_count}, Messages: {current_messages}/{target_messages}")
            # Stop if message count or iteration count exceeds limits
            if current_messages >= target_messages or iteration_count >= getattr(state, 'max_iterations', 30):
                state.intermediate_results["conversation_complete"] = True
                logger.info(f"Conversation complete: {current_messages}/{target_messages} messages or {iteration_count}/{getattr(state, 'max_iterations', 30)} iterations")
            else:
                state.intermediate_results["conversation_complete"] = False
                logger.info(f"Conversation continuing: {current_messages}/{target_messages} messages, {iteration_count}/{getattr(state, 'max_iterations', 30)} iterations")
            # Update state
            state.mark_step_completed("check_completion", time.time() - start_time)
            return state
        except Exception as e:
            return self._handle_error(state, e, "completion check")
    
    def _should_continue_conversation(self, state: WorkflowState) -> str:
        """Conditional edge function"""
        is_complete = state.intermediate_results.get("conversation_complete", False)
        return "complete" if is_complete else "continue"
    
    def _finalize_conversation(self, state: WorkflowState) -> WorkflowState:
        """Finalize conversation"""
        start_time = time.time()
        
        try:
            logger.info("Finalizing conversation")
            
            state.conversation.metadata.update({
                "total_messages": len(state.conversation.messages),
                "completion_time": datetime.now().isoformat(),
                "status": "completed"
            })
            
            state.status = "conversation_complete"
            state.current_step = "parallel_analysis"
            state.mark_step_completed("finalize_conversation", time.time() - start_time)
            
            logger.info(f"Conversation finalized with {len(state.conversation.messages)} messages")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "conversation finalization")
    
    def _get_talan_services_for_client(self, customer_analysis) -> List[str]:
        """Get relevant Talan services for client"""
        try:
            # Extract text from pain points and needs
            pain_points_text = " ".join([
                str(pp.get('issue', pp)) if isinstance(pp, dict) else str(pp) 
                for pp in customer_analysis.pain_points
            ]).lower()
            
            needs_text = " ".join([
                str(need.get('requirement', need)) if isinstance(need, dict) else str(need) 
                for need in customer_analysis.needs
            ]).lower()
            
            all_text = f"{pain_points_text} {needs_text} {customer_analysis.industry}".lower()
            
            # Service mapping
            service_keywords = {
                "transformation_digitale": ["digital", "transformation", "modernisation", "innovation"],
                "cloud": ["cloud", "infrastructure", "aws", "azure", "migration"],
                "data_ai": ["data", "analytics", "intelligence", "ai", "machine learning", "bi"],
                "erp": ["erp", "sap", "oracle", "gestion", "processus"],
                "cybersecurity": ["sécurité", "cyber", "protection", "conformité", "gdpr"]
            }
            
            relevant_services = []
            for service, keywords in service_keywords.items():
                if any(keyword in all_text for keyword in keywords):
                    relevant_services.append(service)
            
            return relevant_services or ["transformation_digitale"]
            
        except Exception as e:
            logger.warning(f"Error determining services: {e}")
            return ["transformation_digitale"]
    
    def _build_talan_message_prompt(self, state: WorkflowState, message_type: str, services: List[str]) -> str:
        """Build specialized Talan message prompt"""
        # Build services context
        services_context = []
        for service_key in services:
            service = TALAN_COMPANY_INFO.get("services", {}).get(service_key, {})
            if service:
                services_context.append(f"- {service.get('title', service_key)}: {service.get('description', '')}")
            else:
                services_context.append(f"- {service_key}: Service de transformation digitale")
        
        # Format conversation history
        history = []
        for i, msg in enumerate(state.conversation.messages, 1):
            sender_label = "TALAN" if msg.sender == "company" else "CLIENT"
            history.append(f"Message {i} ({sender_label}): {msg.content}")
        
        conversation_history = "\n\n".join(history) if history else "Nouveau contact"
        
        # Get message type info
        message_info = MESSAGE_TYPES.get(message_type, {"objective": "Développer la relation commerciale"})
        channel = str(state.conversation_params.channel).lower()
        channel_format = MESSAGE_FORMATS.get(channel, {"tone": "professionnel", "length": "moyen"})
        
        return f"""
        CONTEXTE TALAN TUNISIE :
        Société : {TALAN_COMPANY_INFO.get('name', 'Talan Tunisie')}
        Positionnement : Leader en transformation digitale
        Services pertinents pour ce client :
        {chr(10).join(services_context)}
        
        PROFIL CLIENT :
        Nom : {state.customer_analysis.customer_name}
        Industrie : {state.customer_analysis.industry}
        Taille : {state.customer_analysis.company_size}
        Pain Points : {', '.join([str(pp.get('issue', pp)) if isinstance(pp, dict) else str(pp) for pp in state.customer_analysis.pain_points])}
        Besoins : {', '.join([str(need.get('requirement', need)) if isinstance(need, dict) else str(need) for need in state.customer_analysis.needs])}
        
        PARAMÈTRES MESSAGE :
        Type : {message_type}
        Objectif : {message_info.get('objective', 'Développer la relation')}
        Channel : {channel}
        Format : {channel_format.get('tone', 'professionnel')}, {channel_format.get('length', 'moyen')}
        
        HISTORIQUE CONVERSATION :
        {conversation_history}
        
        CONSIGNES :
        1. Évitez de répéter les arguments déjà utilisés
        2. Progressez naturellement dans la relation commerciale
        3. Personnalisez selon le profil client
        4. Respectez le format {channel} et le type {message_type}
        5. Mentionnez Talan Tunisie et votre expertise locale
        6. Adressez-vous spécifiquement aux pain points identifiés
        
        Générez un message professionnel et personnalisé de Talan :
        """
    
    def _build_customer_response_prompt(self, state: WorkflowState) -> str:
        """Build customer response prompt"""
        # Get last Talan message
        last_talan_message = ""
        for msg in reversed(state.conversation.messages):
            if msg.sender == "company":
                last_talan_message = msg.content
                break
        
        # Determine conversation stage
        customer_messages = [msg for msg in state.conversation.messages if msg.sender == "customer"]
        response_stage = len(customer_messages) + 1
        
        stages = {
            1: {"name": "Initial Interest", "behavior": "Montrez une curiosité prudente"},
            2: {"name": "Problem Exploration", "behavior": "Révélez vos défis spécifiques"},
            3: {"name": "Solution Evaluation", "behavior": "Évaluez concrètement la solution"},
            4: {"name": "Decision Process", "behavior": "Impliquez les décideurs"},
            5: {"name": "Final Engagement", "behavior": "Prenez une décision finale"}
        }
        
        current_stage = stages.get(response_stage, stages[5])
        
        return f"""
        PROFIL CLIENT :
        Nom : {state.customer_analysis.customer_name}
        Industrie : {state.customer_analysis.industry}
        Taille : {state.customer_analysis.company_size}
        Pain Points : {', '.join([str(pp.get('issue', pp)) if isinstance(pp, dict) else str(pp) for pp in state.customer_analysis.pain_points])}
        Style Communication : {getattr(state.customer_analysis, 'communication_style', 'professionnel')}
        
        STAGE CONVERSATION :
        Stage : {current_stage['name']} (Réponse #{response_stage})
        Comportement : {current_stage['behavior']}
        
        DERNIER MESSAGE TALAN :
        "{last_talan_message}"
        
        CONSIGNES :
        1. Respectez votre profil d'entreprise
        2. Montrez une progression naturelle dans l'intérêt
        3. Réagissez spécifiquement au message Talan
        4. {current_stage['behavior']}
        5. Posez des questions pertinentes pour votre secteur
        
        Générez une réponse authentique du client :
        """
