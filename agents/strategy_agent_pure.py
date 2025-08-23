"""
Pure LangGraph Strategy Agent Implementation
Analyzes B2B sales conversation effectiveness and strategic approach using only LangGraph patterns
"""
import json
import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage

from agents.base_agent import BaseAgent
from config.settings import Config
from config.prompts import SystemPrompts
from utils.models import WorkflowState, StrategyAnalysis

logger = logging.getLogger(__name__)

class StrategyAgentPure(BaseAgent):
    """Pure LangGraph agent for strategic conversation analysis"""
    
    def __init__(self):
        """Initialize the pure LangGraph Strategy Agent"""
        super().__init__("StrategyAgent")
    
    def _build_workflow(self) -> StateGraph:
        """Build pure LangGraph workflow for strategy analysis"""
        workflow = StateGraph(WorkflowState)
        
        # Add workflow nodes
        workflow.add_node("validate_inputs", self._validate_inputs)
        workflow.add_node("analyze_methodology", self._analyze_methodology)
        workflow.add_node("evaluate_positioning", self._evaluate_positioning)
        workflow.add_node("assess_objection_handling", self._assess_objection_handling)
        workflow.add_node("evaluate_value_delivery", self._evaluate_value_delivery)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("finalize_analysis", self._finalize_analysis)
        
        # Define workflow edges
        workflow.add_edge("validate_inputs", "analyze_methodology")
        workflow.add_edge("analyze_methodology", "evaluate_positioning")
        workflow.add_edge("evaluate_positioning", "assess_objection_handling")
        workflow.add_edge("assess_objection_handling", "evaluate_value_delivery")
        workflow.add_edge("evaluate_value_delivery", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "finalize_analysis")
        workflow.add_edge("finalize_analysis", END)
        
        # Set entry point
        workflow.set_entry_point("validate_inputs")
        
        return workflow.compile()
    
    def _validate_inputs(self, state: WorkflowState) -> WorkflowState:
        """Validate inputs for strategy analysis"""
        try:
            logger.info(f"[{state.execution_id}] Validating strategy analysis inputs")
            
            # Check required data
            if not state.customer_analysis:
                raise ValueError("Customer analysis not available for strategy analysis")
            
            # Initialize strategy components storage
            if not hasattr(state, '_strategy_components'):
                state._strategy_components = {}
            
            # Check conversation availability
            has_conversation = (
                state.conversation and 
                state.conversation.messages and 
                len(state.conversation.messages) >= 2
            )
            
            if has_conversation:
                state._analysis_mode = "conversation"
                logger.info(f"[{state.execution_id}] Strategy analysis mode: conversation")
            else:
                state._analysis_mode = "customer_profile"
                logger.info(f"[{state.execution_id}] Strategy analysis mode: customer profile only")
            
            state.status = "strategy_validation_complete"
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Strategy validation error")
    
    def _analyze_methodology(self, state: WorkflowState) -> WorkflowState:
        if not hasattr(state, '_strategy_components') or state._strategy_components is None:
            state._strategy_components = {}
        """Analyze sales methodology and approach"""
        try:
            logger.info(f"[{state.execution_id}] Analyzing sales methodology")
            
            analysis_mode = getattr(state, '_analysis_mode', None)
            if analysis_mode == "conversation":
                # Analyze conversation methodology
                conversation_text = self._format_conversation(state.conversation)
                
                methodology_prompt = f"""
                Analyze the sales methodology and approach in this B2B conversation:
                
                CONVERSATION:
                {conversation_text}
                
                CUSTOMER PROFILE:
                - Company: {state.customer_analysis.customer_name}
                - Industry: {state.customer_analysis.industry}
                - Pain Points: {self._format_pain_points(state.customer_analysis)}
                - Needs: {self._format_needs(state.customer_analysis)}
                
                COMPANY CONTEXT:
                - Company: {state.company_analysis.company_name if state.company_analysis else 'Unknown'}
                - Value Props: {', '.join(state.company_analysis.value_propositions) if state.company_analysis else 'Unknown'}
                
                Evaluate the sales methodology used:
                
                1. APPROACH ASSESSMENT
                   - Consultative vs. transactional approach
                   - Discovery question quality and depth
                   - Active listening demonstration
                   - Customer-centric vs. product-centric focus
                
                2. CONVERSATION FLOW
                   - Opening and rapport building
                   - Needs discovery effectiveness
                   - Solution presentation quality
                   - Closing and next steps clarity
                
                3. METHODOLOGY SCORING
                   - Overall approach effectiveness (1-10)
                   - Discovery quality score (1-10)
                   - Solution alignment score (1-10)
                   - Relationship building score (1-10)
                
                Return detailed analysis in JSON format with these exact keys:
                {{
                    "approach_type": "string",
                    "effectiveness_score": float,
                    "discovery_quality": float,
                    "solution_alignment": float,
                    "relationship_building": float,
                    "strengths": ["strength1", "strength2"],
                    "areas_for_improvement": ["area1", "area2"],
                    "methodology_notes": "detailed analysis"
                }}
                """
            else:
                # Customer profile only analysis
                methodology_prompt = f"""
                Create a sales methodology recommendation based on customer analysis:
                
                CUSTOMER PROFILE:
                - Company: {state.customer_analysis.customer_name}
                - Industry: {state.customer_analysis.industry}
                - Pain Points: {self._format_pain_points(state.customer_analysis)}
                - Needs: {self._format_needs(state.customer_analysis)}
                
                Recommend the optimal sales methodology:
                
                1. RECOMMENDED APPROACH
                   - Best methodology for this customer type
                   - Optimal conversation flow
                   - Key discovery areas to focus on
                   - Relationship building strategy
                
                2. SUCCESS FACTORS
                   - Critical elements for success
                   - Potential challenges to anticipate
                   - Measurement criteria
                
                Return analysis in JSON format with the same structure.
                """
            
            # Ajout d'une instruction stricte pour le JSON
            strict_json_instruction = "IMPORTANT : Réponds uniquement avec un objet JSON valide, sans texte ou explication supplémentaire."
            messages = [
                SystemMessage(content=SystemPrompts.STRATEGY_AGENT),
                HumanMessage(content=methodology_prompt + "\n" + strict_json_instruction)
            ]
            
            response = self.llm.invoke(messages)
            methodology_analysis = self._parse_json_response(
                response.content, 
                fallback={
                    "approach_type": "Consultative",
                    "effectiveness_score": 7.0,
                    "discovery_quality": 7.0,
                    "solution_alignment": 7.0,
                    "relationship_building": 7.0,
                    "strengths": ["Professional approach"],
                    "areas_for_improvement": ["Need more discovery"],
                    "methodology_notes": "Analysis completed with basic scoring"
                }
            )
            
            state._strategy_components['methodology'] = methodology_analysis
            state.status = "methodology_analysis_complete"
            
            logger.info(f"[{state.execution_id}] Sales methodology analysis completed")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Methodology analysis error")
    
    def _evaluate_positioning(self, state: WorkflowState) -> WorkflowState:
        if not hasattr(state, '_strategy_components') or state._strategy_components is None:
            state._strategy_components = {}
        """Evaluate competitive positioning and differentiation"""
        try:
            logger.info(f"[{state.execution_id}] Evaluating competitive positioning")
            
            analysis_mode = getattr(state, '_analysis_mode', None)
            if analysis_mode == "conversation":
                conversation_text = self._format_conversation(state.conversation)
                
                positioning_prompt = f"""
                Analyze the competitive positioning and differentiation strategy:
                
                CONVERSATION:
                {conversation_text}
                
                COMPANY COMPETITIVE ADVANTAGES:
                {', '.join(state.company_analysis.competitive_advantages) if state.company_analysis else 'Unknown'}
                
                CUSTOMER CONTEXT:
                - Decision Criteria: {', '.join(state.customer_analysis.decision_criteria) if state.customer_analysis else 'Unknown'}
                
                Evaluate positioning effectiveness:
                
                1. DIFFERENTIATION CLARITY
                   - Unique value proposition communication
                   - Competitive advantage articulation
                   - Market positioning effectiveness
                   - ROI and benefit justification
                
                2. COMPETITIVE STANCE
                   - Indirect competitive references
                   - Advantage demonstration
                   - Value differentiation
                   - Market leadership positioning
                
                3. POSITIONING SCORES
                   - Differentiation clarity (1-10)
                   - Competitive advantage communication (1-10)
                   - Value proposition strength (1-10)
                   - Market positioning effectiveness (1-10)
                
                Return analysis in JSON format:
                {{
                    "differentiation_clarity": float,
                    "competitive_advantage_score": float,
                    "value_proposition_strength": float,
                    "positioning_effectiveness": float,
                    "key_differentiators": ["diff1", "diff2"],
                    "positioning_strengths": ["strength1", "strength2"],
                    "positioning_gaps": ["gap1", "gap2"],
                    "positioning_notes": "detailed analysis"
                }}
                """
            else:
                positioning_prompt = f"""
                Create competitive positioning strategy for customer:
                
                CUSTOMER PROFILE:
                - Company: {state.customer_analysis.customer_name}
                - Industry: {state.customer_analysis.industry}
                - Decision Criteria: {', '.join(state.customer_analysis.decision_criteria) if state.customer_analysis else 'Unknown'}
                
                COMPANY ADVANTAGES:
                {', '.join(state.company_analysis.competitive_advantages) if state.company_analysis else 'Standard competitive advantages'}
                
                Recommend positioning strategy with the same JSON structure.
                """
            
            strict_json_instruction = "IMPORTANT : Réponds uniquement avec un objet JSON valide, sans texte ou explication supplémentaire."
            messages = [
                SystemMessage(content=SystemPrompts.STRATEGY_AGENT),
                HumanMessage(content=positioning_prompt + "\n" + strict_json_instruction)
            ]
            
            response = self.llm.invoke(messages)
            positioning_analysis = self._parse_json_response(
                response.content,
                fallback={
                    "differentiation_clarity": 7.0,
                    "competitive_advantage_score": 7.0,
                    "value_proposition_strength": 7.0,
                    "positioning_effectiveness": 7.0,
                    "key_differentiators": ["Quality solution", "Expert support"],
                    "positioning_strengths": ["Clear messaging"],
                    "positioning_gaps": ["Need more competitive comparison"],
                    "positioning_notes": "Positioning analysis completed"
                }
            )
            
            state._strategy_components['positioning'] = positioning_analysis
            state.status = "positioning_evaluation_complete"
            
            logger.info(f"[{state.execution_id}] Competitive positioning evaluation completed")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Positioning evaluation error")
    
    def _assess_objection_handling(self, state: WorkflowState) -> WorkflowState:
        if not hasattr(state, '_strategy_components') or state._strategy_components is None:
            state._strategy_components = {}
        """Assess objection handling and response effectiveness"""
        try:
            logger.info(f"[{state.execution_id}] Assessing objection handling")
            
            analysis_mode = getattr(state, '_analysis_mode', None)
            if analysis_mode == "conversation":
                conversation_text = self._format_conversation(state.conversation)
                
                objection_prompt = f"""
                Analyze objection handling effectiveness in the conversation:
                
                CONVERSATION:
                {conversation_text}
                
                CUSTOMER CONCERNS/CRITERIA:
                {', '.join(state.customer_analysis.decision_criteria) if state.customer_analysis else 'Unknown'}
                
                Evaluate objection handling:
                
                1. OBJECTION IDENTIFICATION
                   - Recognition of concerns and hesitations
                   - Understanding of underlying issues
                   - Proactive concern addressing
                   - Question interpretation accuracy
                
                2. RESPONSE EFFECTIVENESS
                   - Objection acknowledgment and validation
                   - Evidence and proof provision
                   - Alternative solution offering
                   - Follow-up question quality
                
                3. RESOLUTION APPROACH
                   - Collaborative problem-solving
                   - Trust building through transparency
                   - Next step clarity
                   - Commitment seeking appropriateness
                
                4. SCORING
                   - Objection recognition score (1-10)
                   - Response effectiveness score (1-10)
                   - Resolution approach score (1-10)
                   - Overall handling score (1-10)
                
                Return analysis in JSON format:
                {{
                    "recognition_score": float,
                    "response_effectiveness": float,
                    "resolution_approach": float,
                    "overall_handling_score": float,
                    "handled_objections": ["objection1", "objection2"],
                    "unaddressed_concerns": ["concern1", "concern2"],
                    "handling_strengths": ["strength1", "strength2"],
                    "improvement_opportunities": ["opp1", "opp2"],
                    "handling_notes": "detailed analysis"
                }}
                """
            else:
                objection_prompt = f"""
                Predict potential objections and handling strategy for customer:
                
                CUSTOMER PROFILE:
                - Company: {state.customer_analysis.customer_name}
                - Industry: {state.customer_analysis.industry}
                - Pain Points: {self._format_pain_points(state.customer_analysis)}
                
                Predict likely objections and optimal handling approaches.
                Return analysis with the same JSON structure.
                """
            
            strict_json_instruction = "IMPORTANT : Réponds uniquement avec un objet JSON valide, sans texte ou explication supplémentaire."
            messages = [
                SystemMessage(content=SystemPrompts.STRATEGY_AGENT),
                HumanMessage(content=objection_prompt + "\n" + strict_json_instruction)
            ]
            
            response = self.llm.invoke(messages)
            objection_analysis = self._parse_json_response(
                response.content,
                fallback={
                    "recognition_score": 7.0,
                    "response_effectiveness": 7.0,
                    "resolution_approach": 7.0,
                    "overall_handling_score": 7.0,
                    "handled_objections": ["Budget concerns"],
                    "unaddressed_concerns": ["Implementation timeline"],
                    "handling_strengths": ["Professional response"],
                    "improvement_opportunities": ["More proactive addressing"],
                    "handling_notes": "Objection handling analysis completed"
                }
            )
            
            state._strategy_components['objection_handling'] = objection_analysis
            state.status = "objection_assessment_complete"
            
            logger.info(f"[{state.execution_id}] Objection handling assessment completed")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Objection handling assessment error")
    
    def _evaluate_value_delivery(self, state: WorkflowState) -> WorkflowState:
        if not hasattr(state, '_strategy_components') or state._strategy_components is None:
            state._strategy_components = {}
        """Evaluate value proposition delivery effectiveness"""
        try:
            logger.info(f"[{state.execution_id}] Evaluating value delivery")
            
            analysis_mode = getattr(state, '_analysis_mode', None)
            if analysis_mode == "conversation":
                conversation_text = self._format_conversation(state.conversation)
                
                value_prompt = f"""
                Analyze value proposition delivery in the conversation:
                
                CONVERSATION:
                {conversation_text}
                
                COMPANY VALUE PROPOSITIONS:
                {', '.join(state.company_analysis.value_propositions) if state.company_analysis else 'Standard value propositions'}
                
                CUSTOMER NEEDS:
                {self._format_needs(state.customer_analysis)}
                
                Evaluate value delivery:
                
                1. VALUE COMMUNICATION
                   - Clarity of value proposition
                   - Relevance to customer needs
                   - Quantified benefits presentation
                   - ROI demonstration
                
                2. CUSTOMER ALIGNMENT
                   - Value-to-need matching
                   - Priority alignment
                   - Pain point addressing
                   - Solution fit demonstration
                
                3. DELIVERY EFFECTIVENESS
                   - Message clarity score (1-10)
                   - Relevance score (1-10)
                   - Impact demonstration score (1-10)
                   - Overall delivery score (1-10)
                
                Return analysis in JSON format:
                {{
                    "clarity_score": float,
                    "relevance_score": float,
                    "impact_score": float,
                    "overall_delivery_score": float,
                    "key_messages_delivered": ["message1", "message2"],
                    "value_delivery_strengths": ["strength1", "strength2"],
                    "delivery_gaps": ["gap1", "gap2"],
                    "value_notes": "detailed analysis"
                }}
                """
            else:
                value_prompt = f"""
                Create value delivery strategy for customer:
                
                CUSTOMER NEEDS:
                {self._format_needs(state.customer_analysis)}
                
                COMPANY VALUE PROPOSITIONS:
                {', '.join(state.company_analysis.value_propositions) if state.company_analysis else 'Standard value propositions'}
                
                Design optimal value delivery approach with the same JSON structure.
                """
            
            strict_json_instruction = "IMPORTANT : Réponds uniquement avec un objet JSON valide, sans texte ou explication supplémentaire."
            messages = [
                SystemMessage(content=SystemPrompts.STRATEGY_AGENT),
                HumanMessage(content=value_prompt + "\n" + strict_json_instruction)
            ]
            
            response = self.llm.invoke(messages)
            value_analysis = self._parse_json_response(
                response.content,
                fallback={
                    "clarity_score": 7.0,
                    "relevance_score": 7.0,
                    "impact_score": 7.0,
                    "overall_delivery_score": 7.0,
                    "key_messages_delivered": ["Cost savings", "Efficiency gains"],
                    "value_delivery_strengths": ["Clear messaging"],
                    "delivery_gaps": ["Need more ROI examples"],
                    "value_notes": "Value delivery analysis completed"
                }
            )
            
            state._strategy_components['value_delivery'] = value_analysis
            state.status = "value_evaluation_complete"
            
            logger.info(f"[{state.execution_id}] Value delivery evaluation completed")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Value delivery evaluation error")
    
    def _generate_recommendations(self, state: WorkflowState) -> WorkflowState:
        """Generate strategic recommendations based on all analyses"""
        try:
            logger.info(f"[{state.execution_id}] Generating strategic recommendations")
            
            # Combine all analysis components
            all_components = getattr(state, '_strategy_components', {})
            
            goal = state.conversation.goal if state.conversation else "Business development"
            
            recommendations_prompt = f"""
            Based on comprehensive strategic analysis, generate actionable recommendations:
            
            ANALYSIS RESULTS:
            {json.dumps(all_components, indent=2)}
            
            CONVERSATION GOAL: {goal}
            ANALYSIS MODE: {getattr(state, '_analysis_mode', 'Unknown')}
            
            Generate strategic recommendations:
            
            1. OVERALL EFFECTIVENESS ASSESSMENT
               - Calculate overall effectiveness score (1-10)
               - Identify top 3-5 strengths
               - Identify top 3-5 improvement areas
            
            2. STRATEGIC RECOMMENDATIONS
               - 5-8 specific, actionable recommendations
               - Prioritized by impact and feasibility
               - Address key weaknesses identified
               - Leverage identified strengths
            
            3. NEXT STEPS
               - 3-5 immediate action items
               - Timeline for each action
               - Success metrics to track
            
            4. ALTERNATIVE APPROACHES
               - 2-3 different strategic approaches
               - Pros and cons of each approach
               - Situational recommendations
            
            Return comprehensive recommendations in JSON format:
            {{
                "overall_effectiveness": float,
                "key_strengths": ["strength1", "strength2", "strength3"],
                "improvement_areas": ["area1", "area2", "area3"],
                "strategic_recommendations": [
                    {{"recommendation": "text", "priority": "high/medium/low", "impact": "high/medium/low"}},
                    ...
                ],
                "next_steps": [
                    {{"action": "text", "timeline": "text", "success_metric": "text"}},
                    ...
                ],
                "alternative_approaches": [
                    {{"approach": "text", "pros": ["pro1", "pro2"], "cons": ["con1", "con2"], "best_for": "situation"}},
                    ...
                ],
                "recommendations_notes": "detailed analysis summary"
            }}
            """
            
            strict_json_instruction = "IMPORTANT : Réponds uniquement avec un objet JSON valide, sans texte ou explication supplémentaire."
            messages = [
                SystemMessage(content=SystemPrompts.STRATEGY_AGENT),
                HumanMessage(content=recommendations_prompt + "\n" + strict_json_instruction)
            ]
            
            response = self.llm.invoke(messages)
            recommendations = self._parse_json_response(
                response.content,
                fallback={
                    "overall_effectiveness": 7.0,
                    "key_strengths": ["Professional communication", "Clear value proposition", "Good customer understanding"],
                    "improvement_areas": ["More specific examples needed", "Better objection handling", "Stronger competitive positioning"],
                    "strategic_recommendations": [
                        {"recommendation": "Provide detailed case studies", "priority": "high", "impact": "high"},
                        {"recommendation": "Improve discovery questions", "priority": "medium", "impact": "medium"}
                    ],
                    "next_steps": [
                        {"action": "Send follow-up proposal", "timeline": "48 hours", "success_metric": "Customer response rate"},
                        {"action": "Schedule stakeholder meeting", "timeline": "1 week", "success_metric": "Meeting completion"}
                    ],
                    "alternative_approaches": [
                        {"approach": "Consultative selling", "pros": ["Trust building"], "cons": ["Longer cycle"], "best_for": "Complex sales"}
                    ],
                    "recommendations_notes": "Strategic recommendations generated successfully"
                }
            )
            
            state._strategy_recommendations = recommendations
            state.status = "recommendations_generated"
            
            logger.info(f"[{state.execution_id}] Strategic recommendations generated")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Recommendations generation error")
    
    def _finalize_analysis(self, state: WorkflowState) -> WorkflowState:
        """Finalize strategy analysis and create StrategyAnalysis object with robust field extraction for UI"""
        try:
            logger.info(f"[{state.execution_id}] Finalizing strategy analysis")

            # Get all components
            components = getattr(state, '_strategy_components', {})
            recommendations = getattr(state, '_strategy_recommendations', {})
            raw_details = {}
            if components:
                raw_details.update(components)
            if recommendations:
                raw_details['recommendations'] = recommendations

            # --- Robust extraction for UI fields ---
            def get_first(*paths, default=None):
                for path in paths:
                    d = components
                    try:
                        for p in path:
                            d = d.get(p, {}) if isinstance(d, dict) else {}
                        if d and d != {}:
                            return d
                    except Exception:
                        continue
                return default

            # Methodology scores
            methodology = components.get('methodology', {})
            methodology_score = methodology.get('effectiveness_score')
            # Positioning scores
            positioning = components.get('positioning', {})
            positioning_score = positioning.get('positioning_effectiveness')
            # Value prop scores
            value_delivery = components.get('value_delivery', {})
            value_prop_score = value_delivery.get('overall_delivery_score')

            # Strengths and improvement areas
            strengths = (
                recommendations.get('key_strengths')
                or methodology.get('strengths')
                or positioning.get('positioning_strengths')
                or value_delivery.get('value_delivery_strengths')
                or []
            )
            improvement_areas = (
                recommendations.get('improvement_areas')
                or methodology.get('areas_for_improvement')
                or positioning.get('positioning_gaps')
                or value_delivery.get('delivery_gaps')
                or []
            )

            # Recommendations and next steps
            recs = recommendations.get('strategic_recommendations', [])
            if not recs:
                recs = [r for r in (
                    methodology.get('methodology_notes', ''),
                    positioning.get('positioning_notes', ''),
                    value_delivery.get('value_notes', '')
                ) if r]
            recommendations_list = [
                rec.get('recommendation', str(rec)) if isinstance(rec, dict) else str(rec)
                for rec in recs
            ]
            next_steps = [
                step.get('action', str(step)) if isinstance(step, dict) else str(step)
                for step in recommendations.get('next_steps', [])
            ]

            # Fallbacks for UI
            if not strengths:
                strengths = ["No specific strengths identified"]
            if not improvement_areas:
                improvement_areas = ["No major improvement areas identified"]
            if not recommendations_list:
                recommendations_list = ["No specific recommendations available"]
            if not next_steps:
                next_steps = ["No specific next steps defined"]

            # Create StrategyAnalysis object with top-level scores for UI
            strategy_analysis = StrategyAnalysis(
                conversation_id=state.conversation.conversation_id if state.conversation else "customer_profile_analysis",
                overall_effectiveness=recommendations.get('overall_effectiveness', 7.0),
                methodology_score=methodology_score if methodology_score is not None else None,
                positioning_score=positioning_score if positioning_score is not None else None,
                value_prop_score=value_prop_score if value_prop_score is not None else None,
                methodology_assessment=methodology,
                competitive_positioning=positioning,
                objection_handling=components.get('objection_handling', {}),
                value_proposition_delivery=value_delivery,
                strengths=strengths,
                improvement_areas=improvement_areas,
                recommendations=recommendations_list,
                next_steps=next_steps,
                raw_details=raw_details
            )

            state.strategy_analysis = strategy_analysis
            state.status = "strategy_analysis_complete"

            # Clean up temporary data
            if hasattr(state, '_strategy_components'):
                delattr(state, '_strategy_components')
            if hasattr(state, '_strategy_recommendations'):
                delattr(state, '_strategy_recommendations')
            if hasattr(state, '_analysis_mode'):
                delattr(state, '_analysis_mode')

            logger.info(f"[{state.execution_id}] Strategy analysis completed successfully")
            return state

        except Exception as e:
            return self._handle_error(state, e, "Strategy finalization error")
    
    def _format_conversation(self, conversation) -> str:
        """Format conversation for analysis"""
        if not conversation or not conversation.messages:
            return "No conversation available"
        
        formatted_messages = []
        for msg in conversation.messages:
            sender_label = "Company Representative" if msg.sender == "company" else "Customer"
            formatted_messages.append(f"{sender_label}: {msg.content}")
        
        return "\n\n".join(formatted_messages)
    
    def _format_pain_points(self, customer_analysis) -> str:
        """Format customer pain points for prompts"""
        if not customer_analysis.pain_points:
            return "No specific pain points identified"
        
        pain_points_text = []
        for pp in customer_analysis.pain_points:
            if isinstance(pp, dict):
                pain_points_text.append(pp.get("issue", str(pp)))
            else:
                pain_points_text.append(str(pp))
        
        return ', '.join(pain_points_text)
    
    def _format_needs(self, customer_analysis) -> str:
        """Format customer needs for prompts"""
        if not customer_analysis.needs:
            return "No specific needs identified"
        
        needs_text = []
        for need in customer_analysis.needs:
            if isinstance(need, dict):
                needs_text.append(need.get("requirement", str(need)))
            else:
                needs_text.append(str(need))
        
        return ', '.join(needs_text)
    
    def _parse_json_response(self, response_text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured JSON with fallback"""
        try:
            # Log the raw LLM response for debugging
            logger.info(f"Raw LLM response: {response_text}")
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                return parsed
            else:
                logger.warning(f"No JSON structure found in response, using fallback. Raw response: {response_text}")
                return fallback
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {str(e)}. Raw response: {response_text}. Using fallback.")
            return fallback
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {str(e)}. Raw response: {response_text}. Using fallback.")
            return fallback
