"""
Pure LangGraph Personality Classifier Agent Implementation
Analyzes customer communication patterns and behavioral cues for personality insights
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
from utils.models import WorkflowState, PersonalityAnalysis

logger = logging.getLogger(__name__)

class PersonalityClassifierAgentPure(BaseAgent):

    def __init__(self, enable_checkpointing: bool = True):
        super().__init__(agent_name="PersonalityClassifierAgentPure", enable_checkpointing=enable_checkpointing)

    def _build_workflow(self) -> StateGraph:
        """Builds the workflow graph for the personality classifier agent."""
        workflow = StateGraph(WorkflowState)
        # Add workflow nodes
        workflow.add_node("assess_decision_patterns", self._assess_decision_patterns)
        workflow.add_node("determine_personality_profile", self._determine_personality_profile)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("finalize_analysis", self._finalize_analysis)
        # Define workflow edges
        workflow.add_edge("assess_decision_patterns", "determine_personality_profile")
        workflow.add_edge("determine_personality_profile", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "finalize_analysis")
        workflow.add_edge("finalize_analysis", END)
        # Set entry point
        workflow.set_entry_point("assess_decision_patterns")
        return workflow.compile()
            
    # All code at the top of the class must be inside methods. No executable code should be present here.
    
    def _assess_decision_patterns(self, state: WorkflowState) -> WorkflowState:
        """Assess customer decision-making patterns and preferences"""
        try:
            logger.info(f"[{state.execution_id}] Assessing decision patterns")
            
            analysis_mode = getattr(state, '_analysis_mode', None)
            if not hasattr(state, 'personality_components') or state.personality_components is None:
                state.personality_components = {}
            if analysis_mode == "conversation":
                customer_messages = [msg.content for msg in state.conversation.messages if msg.sender == "customer"]
                customer_text = "\n".join(customer_messages)
                # Robust role extraction
                role = "Unknown"
                if hasattr(state.customer_analysis, 'decision_makers') and state.customer_analysis.decision_makers:
                    first_dm = state.customer_analysis.decision_makers[0]
                    if isinstance(first_dm, dict):
                        role = first_dm.get('role', 'Unknown')
                    else:
                        role = getattr(first_dm, 'role', 'Unknown')
                decision_prompt = f"""
                Analyze decision-making patterns from customer communication:
                
                CUSTOMER MESSAGES:
                {customer_text}
                
                DISC PROFILE:
                {json.dumps(state.personality_components.get('disc_profile', {}), indent=2)}
                
                CUSTOMER CONTEXT:
                - Decision Criteria: {', '.join(state.customer_analysis.decision_criteria) if state.customer_analysis.decision_criteria else 'Unknown'}
                - Role: {role}
                
                Analyze decision-making patterns:
                
                1. DECISION STYLE
                   - Analytical vs. Intuitive approach
                   - Individual vs. Consensus-based
                   - Fast vs. Deliberate pacing
                   - Risk-taking vs. Risk-averse
                
                2. INFORMATION PROCESSING
                   - Detail vs. Big picture preference
                   - Data vs. Relationship focus
                   - Sequential vs. Holistic processing
                   - Verification vs. Trust-based approach
                
                3. RELATIONSHIP ORIENTATION
                   - Task-focused vs. People-focused
                   - Transactional vs. Relationship-based
                   - Individual vs. Team orientation
                   - Formal vs. Informal preference
                
                4. RISK AND CHANGE TOLERANCE
                   - Innovation adoption rate
                   - Change comfort level
                   - Risk tolerance indicators
                   - Security vs. Growth focus
                
                Return analysis in JSON format:
                {{
                    "decision_style": "string",
                    "decision_speed": "fast/moderate/deliberate",
                    "information_preference": "data/relationship/mixed",
                    "processing_style": "sequential/holistic/mixed",
                    "relationship_orientation": "task/people/balanced",
                    "risk_tolerance": "high/moderate/low",
                    "change_adoption": "early/mainstream/late",
                    "verification_approach": "high/moderate/low",
                    "decision_factors": ["factor1", "factor2"],
                    "pattern_indicators": ["indicator1", "indicator2"],
                    "decision_notes": "detailed analysis"
                }}
                """
            else:
                # Profile-based decision pattern analysis
                decision_prompt = f"""
                Analyze decision patterns based on customer profile:
                
                CUSTOMER PROFILE:
                - Role: {getattr(state.customer_analysis, 'role', 'Unknown')}
                - Industry: {getattr(state.customer_analysis, 'industry', 'Unknown')}
                - Decision Criteria: {', '.join(getattr(state.customer_analysis, 'decision_criteria', []) or ['Unknown'])}
                
                Infer decision patterns based on role and industry context.
                Return analysis with the same JSON structure.
                """
            
            messages = [
                SystemMessage(content=SystemPrompts.PERSONALITY_CLASSIFIER_AGENT),
                HumanMessage(content=decision_prompt)
            ]
            
            response = self.llm.invoke(messages)
            decision_analysis = self._parse_json_response(
                response.content,
                fallback={
                    "decision_style": "Analytical",
                    "decision_speed": "moderate",
                    "information_preference": "data",
                    "processing_style": "sequential",
                    "relationship_orientation": "balanced",
                    "risk_tolerance": "moderate",
                    "change_adoption": "mainstream",
                    "verification_approach": "moderate",
                    "decision_factors": ["ROI", "Quality", "Support"],
                    "pattern_indicators": ["Methodical approach", "Data-driven"],
                    "decision_notes": "Decision pattern analysis completed"
                }
            )
            
            state.personality_components['decision_patterns'] = decision_analysis
            logger.info(f"[DEBUG] Set personality_components['decision_patterns']: {decision_analysis}")
            state.status = "decision_assessment_complete"
            
            logger.info(f"[{state.execution_id}] Decision pattern assessment completed")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Decision pattern assessment error")
    
    def _determine_personality_profile(self, state: WorkflowState) -> WorkflowState:
        """Determine overall personality profile classification"""
        try:
            logger.info(f"[{state.execution_id}] Determining personality profile")
            
            # Combine all analysis components
            if not hasattr(state, 'personality_components'):
                state.personality_components = {}
            all_components = state.personality_components
            
            profile_prompt = f"""
            Determine the overall B2B personality profile based on comprehensive analysis:
            
            ANALYSIS COMPONENTS:
            {json.dumps(all_components, indent=2)}
            
            CUSTOMER CONTEXT:
            - Industry: {getattr(state.customer_analysis, 'industry', 'Unknown')}
            - Role: {getattr(state.customer_analysis, 'role', 'Unknown')}
            - Company Size: {getattr(state.customer_analysis, 'company_size', 'Unknown')}
            
            Classify into one of these 5 B2B personality profiles:
            
            1. **Tech-Savvy Innovator**: Early adopters who love cutting-edge technology, value innovation and efficiency
            2. **Business-Oriented Decision Maker**: Focus on ROI, business impact, and strategic alignment
            3. **Cost-Conscious Pragmatist**: Prioritize value for money, cost-effectiveness, and practical solutions
            4. **Early Adopter Innovator**: Embrace new technologies quickly, willing to take calculated risks
            5. **Relationship-Driven Connector**: Value personal relationships, trust, and long-term partnerships
            
            Based on the comprehensive analysis, determine:
            
            1. PRIMARY PERSONALITY PROFILE (one of the 5 types above)
            2. PROFILE CONFIDENCE (1-10 scale)
            3. SECONDARY TRAITS (influences from other profiles)
            4. KEY PERSONALITY CHARACTERISTICS
            5. MOTIVATIONAL DRIVERS
            
            Return classification in JSON format:
            {{
                "personality_profile": "string",
                "profile_confidence": float,
                "secondary_traits": ["trait1", "trait2"],
                "key_characteristics": ["char1", "char2", "char3"],
                "motivational_drivers": ["driver1", "driver2", "driver3"],
                "profile_rationale": "explanation of classification",
                "classification_notes": "detailed analysis"
            }}
            """
            
            messages = [
                SystemMessage(content=SystemPrompts.PERSONALITY_CLASSIFIER_AGENT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_analysis = self._parse_json_response(
                response.content,
                fallback={
                    "personality_profile": "Business-Oriented Decision Maker",
                    "profile_confidence": 7.5,
                    "secondary_traits": ["Analytical", "Professional"],
                    "key_characteristics": ["Data-driven", "Results-focused", "Professional"],
                    "motivational_drivers": ["ROI", "Efficiency", "Quality"],
                    "profile_rationale": "Professional communication style and analytical approach",
                    "classification_notes": "Personality profile classification completed"
                }
            )
            
            state.personality_components['profile_classification'] = profile_analysis
            logger.info(f"[DEBUG] Set personality_components['profile_classification']: {profile_analysis}")
            state.status = "profile_determination_complete"
            
            logger.info(f"[{state.execution_id}] Personality profile determination completed")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Personality profile determination error")
    
    def _generate_recommendations(self, state: WorkflowState) -> WorkflowState:
        """Generate personality-based interaction recommendations"""
        try:
            logger.info(f"[{state.execution_id}] Generating personality-based recommendations")
            
            # Combine all analysis components
            all_components = getattr(state, 'personality_components', {})
            
            recommendations_prompt = f"""
            Generate personality-based interaction recommendations:
            
            COMPLETE PERSONALITY ANALYSIS:
            {json.dumps(all_components, indent=2)}
            
            CONVERSATION GOAL: {state.conversation.goal if state.conversation else "Business development"}
            
            Generate comprehensive recommendations:
            
            1. OPTIMAL COMMUNICATION APPROACH
               - Preferred communication channels
               - Meeting style preferences
               - Presentation format recommendations
               - Information delivery style
            
            2. PERSONALITY-BASED SALES STRATEGY
               - Key interaction principles
               - Engagement approach
               - Information packaging
               - Relationship building tactics
            
            3. OBJECTION HANDLING APPROACH
               - Optimal response style
               - Evidence and proof preferences
               - Concern addressing method
               - Follow-up approach
            
            4. MOTIVATIONAL TRIGGERS
               - Primary motivators
               - Value proposition alignment
               - Decision triggers
               - Success factors
            
            5. INTERACTION RECOMMENDATIONS
               - Do's and don'ts
               - Best practices
               - Communication timing
               - Follow-up preferences
            
            Return recommendations in JSON format:
            {{
                "optimal_communication_approach": {{
                    "preferred_channel": "string",
                    "meeting_style": "string",
                    "presentation_format": "string",
                    "information_delivery": "string"
                }},
                "sales_strategy": {{
                    "engagement_approach": "string",
                    "key_principles": ["principle1", "principle2"],
                    "relationship_tactics": ["tactic1", "tactic2"],
                    "information_packaging": "string"
                }},
                "objection_handling_style": "string",
                "objection_approach": {{
                    "response_style": "string",
                    "evidence_preference": "string",
                    "addressing_method": "string"
                }},
                "motivational_triggers": ["trigger1", "trigger2", "trigger3"],
                "interaction_recommendations": ["rec1", "rec2", "rec3"],
                "dos_and_donts": {{
                    "dos": ["do1", "do2"],
                    "donts": ["dont1", "dont2"]
                }},
                "follow_up_preferences": "string",
                "recommendations_notes": "detailed summary"
            }}
            """
            
            messages = [
                SystemMessage(content=SystemPrompts.PERSONALITY_CLASSIFIER_AGENT),
                HumanMessage(content=recommendations_prompt)
            ]
            
            response = self.llm.invoke(messages)
            recommendations = self._parse_json_response(
                response.content,
                fallback={
                    "optimal_communication_approach": {
                        "preferred_channel": "Email with detailed attachments",
                        "meeting_style": "Structured with agenda",
                        "presentation_format": "Data-rich with clear structure",
                        "information_delivery": "Sequential and thorough"
                    },
                    "sales_strategy": {
                        "engagement_approach": "Professional and consultative",
                        "key_principles": ["Build credibility", "Provide evidence"],
                        "relationship_tactics": ["Demonstrate expertise", "Be reliable"],
                        "information_packaging": "Detailed and organized"
                    },
                    "objection_handling_style": "Data-driven and collaborative",
                    "objection_approach": {
                        "response_style": "Analytical and thorough",
                        "evidence_preference": "Data and case studies",
                        "addressing_method": "Direct with supporting evidence"
                    },
                    "motivational_triggers": ["Quality", "ROI", "Reliability"],
                    "interaction_recommendations": [
                        "Provide detailed documentation",
                        "Be prepared with data",
                        "Follow structured approach"
                    ],
                    "dos_and_donts": {
                        "dos": ["Be thorough", "Provide evidence"],
                        "donts": ["Rush decisions", "Oversell"]
                    },
                    "follow_up_preferences": "Structured follow-up with clear next steps",
                    "recommendations_notes": "Personality-based recommendations generated"
                }
            )
            
            state.personality_recommendations = recommendations
            logger.info(f"[DEBUG] Set personality_recommendations: {recommendations}")
            state.status = "recommendations_generated"
            
            logger.info(f"[{state.execution_id}] Personality-based recommendations generated")
            return state
            
        except Exception as e:
            return self._handle_error(state, e, "Recommendations generation error")
    
    def _finalize_analysis(self, state: WorkflowState) -> WorkflowState:
        """Aggregate all parsed LLM output and map to PersonalityAnalysis fields for UI, searching all nested dicts for best values."""
        try:
            logger.info(f"[{state.execution_id}] Finalizing personality analysis")
            components = getattr(state, 'personality_components', {})
            recommendations = getattr(state, 'personality_recommendations', {})
            logger.info(f"[DEBUG FINALIZE] personality_components: {components}")
            logger.info(f"[DEBUG FINALIZE] personality_recommendations: {recommendations}")

            # Helper to recursively search for a key in nested dicts
            def find_in_dicts(dicts, keys):
                if isinstance(keys, str):
                    keys = [keys]
                for d in dicts:
                    if not isinstance(d, dict):
                        continue
                    for k in keys:
                        if k in d and d[k] not in [None, '', [], {}]:
                            return d[k]
                    # Search nested dicts
                    for v in d.values():
                        if isinstance(v, dict):
                            result = find_in_dicts([v], keys)
                            if result not in [None, '', [], {}]:
                                return result
                        elif isinstance(v, list):
                            for item in v:
                                if isinstance(item, dict):
                                    result = find_in_dicts([item], keys)
                                    if result not in [None, '', [], {}]:
                                        return result
                return None

            # Gather all dicts to search
            dicts_to_search = []
            if isinstance(components, dict):
                dicts_to_search.append(components)
                dicts_to_search.extend([v for v in components.values() if isinstance(v, dict)])
            if isinstance(recommendations, dict):
                dicts_to_search.append(recommendations)
                dicts_to_search.extend([v for v in recommendations.values() if isinstance(v, dict)])

            # Extract fields robustly
            personality_profile = find_in_dicts(dicts_to_search, ['personality_profile', 'profile']) or 'Unknown'
            profile_confidence = find_in_dicts(dicts_to_search, ['profile_confidence', 'confidence']) or 'N/A'
            secondary_traits = find_in_dicts(dicts_to_search, 'secondary_traits') or []
            key_characteristics = find_in_dicts(dicts_to_search, 'key_characteristics') or []
            profile_rationale = find_in_dicts(dicts_to_search, 'profile_rationale') or ''
            classification_notes = find_in_dicts(dicts_to_search, 'classification_notes') or ''
            motivational_drivers = find_in_dicts(dicts_to_search, ['motivational_drivers', 'key_motivational_drivers', 'motivational_triggers']) or []
            personality_based_recommendations = find_in_dicts(dicts_to_search, ['interaction_recommendations', 'recommendations', 'best_practices']) or []
            optimal_communication_approach = find_in_dicts(dicts_to_search, ['optimal_communication_approach', 'communication_approach']) or {}
            objection_handling_style = find_in_dicts(dicts_to_search, ['objection_handling_style', 'objection_handling_approach', 'Objection Handling']) or 'Unknown'
            recommendations_notes = find_in_dicts(dicts_to_search, 'recommendations_notes') or ''

            # DISC profile (robust extraction and validation)
            disc_profile = find_in_dicts(
                dicts_to_search,
                ['disc_profile', 'DISC_profile', 'DISC', 'DISC_Personality_Assessment']
            ) or {'D': 25.0, 'I': 25.0, 'S': 25.0, 'C': 25.0}
            if not isinstance(disc_profile, dict):
                logger.warning(f"DISC profile not a dict: {disc_profile}")
                disc_profile = {'D': 25.0, 'I': 25.0, 'S': 25.0, 'C': 25.0}
            for k in ['D', 'I', 'S', 'C']:
                try:
                    v = float(disc_profile.get(k, 25.0))
                    if not (0 <= v <= 100):
                        logger.warning(f"DISC value for {k} out of range: {v}")
                        v = 25.0
                    disc_profile[k] = v
                except Exception as e:
                    logger.warning(f"DISC value for {k} invalid: {e}")
                    disc_profile[k] = 25.0
            # Normalize if sum is way off
            total_disc = sum(disc_profile.values())
            if total_disc > 0 and abs(total_disc - 100) > 5:
                for k in disc_profile:
                    disc_profile[k] = round(disc_profile[k] * 100.0 / total_disc, 2)

            # Communication style
            communication_style = find_in_dicts(
                dicts_to_search,
                [
                    'communication_style', 'Communication Style',
                    'communication_approach', 'primary_communication_style',
                    'style', 'approach', 'preferred_communication',
                    'preferred_style', 'interaction_style'
                ]
            ) or 'Unknown'
            # Decision making style
            decision_making_style = find_in_dicts(
                dicts_to_search,
                [
                    'decision-making_patterns', 'decision_making_style', 'Decision-Making Patterns',
                    'decision_making', 'decision_style', 'decision_approach',
                    'decision_pattern', 'decision_process', 'decision_method'
                ]
            ) or 'Unknown'
            # Relationship orientation
            relationship_orientation = find_in_dicts(
                dicts_to_search,
                [
                    'relationship_orientation', 'Relationship Orientation',
                    'relationship_focus', 'relationship_type', 'relationship',
                    'orientation', 'relationship_approach', 'relationship_mode'
                ]
            ) or 'Unknown'
            # Risk tolerance
            risk_tolerance = find_in_dicts(
                dicts_to_search,
                [
                    'risk_tolerance', 'Risk Tolerance',
                    'risk_level', 'risk_profile', 'tolerance', 'risk_attitude',
                    'risk', 'riskiness'
                ]
            ) or 'Unknown'
            # Information processing
            information_processing = find_in_dicts(
                dicts_to_search,
                [
                    'information_processing_preferences', 'information_processing', 'Information Processing Preferences',
                    'info_processing', 'processing_style', 'processing_mode',
                    'information_style', 'information_mode', 'info_mode'
                ]
            ) or 'Unknown'

            # Validate and fallback for motivational_drivers
            if not isinstance(motivational_drivers, list):
                motivational_drivers = [str(motivational_drivers)] if motivational_drivers else []
            motivational_drivers = [str(x) for x in motivational_drivers if x]

            # Validate and fallback for personality_based_recommendations
            recs = personality_based_recommendations
            if isinstance(recs, dict):
                recs = list(recs.values())
            if not isinstance(recs, list):
                recs = [str(recs)] if recs else []
            personality_based_recommendations = [str(x) for x in recs if x]

            # Validate optimal_communication_approach
            if not isinstance(optimal_communication_approach, dict):
                optimal_communication_approach = {}

            # Validate objection_handling_style
            if not isinstance(objection_handling_style, str):
                objection_handling_style = str(objection_handling_style) if objection_handling_style else 'Unknown'

            # Validate profile_confidence
            try:
                profile_confidence = int(profile_confidence)
                if not (0 <= profile_confidence <= 100):
                    logger.warning(f"Profile confidence out of range: {profile_confidence}")
                    profile_confidence = 50
            except Exception as e:
                logger.warning(f"Profile confidence invalid: {e}")
                profile_confidence = 50

            pa_dict = {
                'conversation_id': getattr(state, 'execution_id', 'analysis_conv_2'),
                'communication_style': communication_style,
                'disc_profile': disc_profile,
                'decision_making_style': decision_making_style,
                'relationship_orientation': relationship_orientation,
                'risk_tolerance': risk_tolerance,
                'information_processing': information_processing,
                'motivational_drivers': motivational_drivers,
                'personality_based_recommendations': personality_based_recommendations,
                'optimal_communication_approach': optimal_communication_approach,
                'objection_handling_style': objection_handling_style,
                'personality_profile': personality_profile,
                'profile_confidence': profile_confidence,
                'secondary_traits': secondary_traits,
                'key_characteristics': key_characteristics,
                'profile_rationale': profile_rationale,
                'classification_notes': classification_notes,
                'recommendations_notes': recommendations_notes
            }
            logger.info(f"[FINAL PersonalityAnalysis for UI] {pa_dict}")
            state.personality_analysis = PersonalityAnalysis(**pa_dict)
            state.status = "personality_analysis_complete"
            for attr in ['personality_components', 'personality_recommendations', '_analysis_mode']:
                if hasattr(state, attr):
                    delattr(state, attr)
            logger.info(f"[{state.execution_id}] Personality analysis completed successfully")
            return state
        except Exception as e:
            return self._handle_error(state, e, "Personality finalization error")
    
    def _parse_json_response(self, response_text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        import re, json
        logger.info(f"[LLM RAW RESPONSE] {response_text}")

        # 1. Try parsing the whole response as JSON first
        try:
            parsed = json.loads(response_text)
            logger.info(f"[LLM PARSED DICT] {parsed}")
            return parsed
        except Exception as e:
            logger.warning(f"Whole response JSON parsing failed: {e}")

        # 2. Fallback: Try to extract JSON after 'JSON Output:' or '```json'
        json_candidates = []
        match = re.search(r'JSON Output:.*?({[\s\S]+?})', response_text)
        if match:
            json_candidates.append(match.group(1))
        for m in re.finditer(r'```json\s*({[\s\S]+?})\s*```', response_text):
            json_candidates.append(m.group(1))
        json_blocks = re.findall(r'\{[\s\S]*?\}', response_text)
        json_candidates.extend(json_blocks)

        for js in sorted(json_candidates, key=len, reverse=True):
            try:
                parsed = json.loads(js)
                logger.info(f"[LLM PARSED DICT] {parsed}")
                return parsed
            except Exception as e:
                logger.warning(f"JSON parsing failed for block: {e}")
        logger.warning("No valid JSON object found in response, using fallback")
        return fallback
        """Parse LLM response into structured JSON with fallback. Collect and merge all valid JSON blocks."""
        try:
            logger.info(f"[LLM RAW RESPONSE] {response_text}")
            import re
            json_blocks = re.findall(r'\{[\s\S]*?\}', response_text)
            parsed_blocks = []
            for json_str in json_blocks:
                try:
                    parsed = json.loads(json_str)
                    logger.info(f"[LLM PARSED DICT] {parsed}")
                    parsed_blocks.append(parsed)
                except Exception as e:
                    logger.warning(f"JSON parsing failed for block: {e}")
            if not parsed_blocks:
                logger.warning("No valid JSON object found in response, using fallback")
                return fallback
        # If only one block, return as dict; if multiple, merge all dicts
            if len(parsed_blocks) == 1:
                return parsed_blocks[0]
            def deep_merge(a, b):
                for k, v in b.items():
                    if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                        a[k] = deep_merge(a[k], v)
                    elif k in a and isinstance(a[k], list) and isinstance(v, list):
                        a[k] = a[k] + v
                    else:
                        a[k] = v
                return a
            merged = {}
            for d in parsed_blocks:
                if isinstance(d, dict):
                    merged = deep_merge(merged, d)
            return merged if merged else fallback
        except Exception as e:
            logger.warning(f"Exception in JSON extraction: {e}, using fallback")
            return fallback
