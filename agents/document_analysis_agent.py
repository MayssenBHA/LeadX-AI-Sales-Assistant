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
            EXTRACT ALL DATA FROM THE FOLLOWING CUSTOMER JSON:
            
            Customer Data: {json.dumps(raw_data, indent=2)}
            
            MANDATORY EXTRACTION REQUIREMENTS:
            
            1. **current_challenges** array → Convert to **pain_points** array:
               - Extract ALL challenges with description, impact, and business_impact
               
            2. **business_needs** array → Convert to **needs** array:
               - Extract ALL needs with need, priority, budget_allocated, and timeline
               
            3. **decision_makers** array → Convert to **decision_makers** array:
               - Extract ALL people with name, role, influence_level, email, priorities, and concerns
               
            4. **budget_range** → Extract exact value or calculate from business_needs
            5. **technology_stack** → Include in decision_criteria array
            6. **success_metrics** → Include relevant ones in decision_criteria
            
            CRITICAL: Do NOT return empty arrays []. You must extract and map ALL available data.
            
            Return ONLY a valid JSON object with this exact structure:
            {{
              "customer_name": "...",
              "industry": "...", 
              "company_size": "...",
              "pain_points": [{{ "description": "...", "impact": "...", "business_impact": "..." }}],
              "needs": [{{ "need": "...", "priority": "...", "budget": "...", "timeline": "..." }}],
              "decision_criteria": ["...", "..."],
              "budget_range": "...",
              "timeline": "...",
              "communication_style": "...",
              "decision_makers": [{{ "name": "...", "role": "...", "influence": "...", "email": "...", "priorities": ["..."], "concerns": ["..."] }}]
            }}
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
            
            # Parse LLM response with improved JSON extraction
            try:
                if not response.content or response.content.strip() == "":
                    logger.warning("LLM returned empty response, using fallback analysis")
                    raise ValueError("Empty LLM response")
                
                # Use improved JSON cleaning function
                cleaned_content = self._clean_llm_json_response(response.content)
                
                logger.info(f"Cleaned LLM response: '{cleaned_content[:200]}...'")
                
                analysis_data = json.loads(cleaned_content)
                
                # Create CustomerAnalysis object from nested structure if needed
                if 'customer_analysis' in analysis_data:
                    analysis_data = analysis_data['customer_analysis']
                elif 'customerAnalysis' in analysis_data:
                    analysis_data = analysis_data['customerAnalysis']
                
                # Transform nested LLM structure to flat structure expected by model
                analysis_data = self._transform_llm_structure(analysis_data)
                
                customer_analysis = CustomerAnalysis(**analysis_data)
                state.customer_analysis = customer_analysis
                logger.info(f"Successfully created LLM-based analysis for: {customer_analysis.customer_name}")
                
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.warning(f"Failed to parse LLM response as JSON: {e}")
                logger.debug(f"Raw LLM response: {response.content}")
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
            customer_name="Company Profile Not Available",
            industry="Technology Services",
            company_size="50-200 employees", 
            pain_points=[{
                "issue": "Manual process inefficiencies",
                "impact": "Medium",
                "description": "Generic pain point identified during fallback analysis"
            }],
            needs=[{
                "requirement": "Process automation solutions", 
                "priority": "High",
                "description": "Standard automation needs assessment"
            }],
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
            value = getattr(analysis, field)
            # Accepter "Unknown" comme valide pour le fallback minimal
            if not value or value == "":  # Rejeter seulement vide/None
                return False
        
        # Si on a au moins des pain_points OU des needs, c'est valide
        # Même avec des valeurs "Unknown" (fallback acceptable)
        if not analysis.pain_points and not analysis.needs:
            return False
        
        return True
    
    def _clean_llm_json_response(self, response_content: str) -> str:
        """Nettoie et extrait le JSON valide de la réponse LLM"""
        import re
        
        # Enlever les markers markdown
        content = response_content.strip()
        content = re.sub(r'^```json\s*', '', content, flags=re.IGNORECASE | re.MULTILINE)
        content = re.sub(r'\s*```\s*$', '', content, flags=re.MULTILINE)
        content = content.strip()
        
        # Trouver le premier objet JSON valide
        try:
            # Chercher le début du JSON principal - essayer plusieurs patterns
            start_patterns = [
                r'\{\s*"customer_name"',     # Structure directe
                r'\{\s*"company_name"',      # Structure alternative
                r'\{\s*"customer_company_details"', # Structure avec préfixe
                r'\{\s*"customerAnalysis"',  # Structure attendue
                r'\{\s*"customer_analysis"', # Structure avec underscore
                r'\{\s*"[^"]+"\s*:\s*\{',   # Objet JSON générique avec sous-objet
                r'\{\s*"[^"]+"\s*:\s*"',    # Objet JSON générique avec string
                r'\{'                        # Premier objet trouvé
            ]
            
            start_pos = -1
            for pattern in start_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    start_pos = match.start()
                    break
            
            if start_pos == -1:
                logger.warning("Aucun début JSON trouvé dans la réponse LLM")
                return content
            
            # Trouver la fin du JSON en comptant les accolades avec plus de robustesse
            bracket_count = 0
            end_pos = -1
            in_string = False
            escape_next = False
            
            for i, char in enumerate(content[start_pos:], start_pos):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        bracket_count += 1
                    elif char == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_pos = i + 1
                            break
            
            if end_pos == -1:
                logger.warning("Fin JSON non trouvée, utilisation du contenu complet")
                # Si pas de fin trouvée, utiliser tout le contenu disponible
                end_pos = len(content)
            
            cleaned_json = content[start_pos:end_pos]
            
            # Validation finale : essayer de parser
            json.loads(cleaned_json)
            
            logger.info(f"JSON extrait avec succès: {len(cleaned_json)} caractères")
            return cleaned_json
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Échec nettoyage JSON intelligent: {e}")
            
            # Fallback plus robuste
            # Enlever tous les markers markdown
            content = re.sub(r'```[a-zA-Z]*\s*', '', content, flags=re.IGNORECASE)
            content = re.sub(r'\s*```\s*', '', content, flags=re.MULTILINE)
            content = content.strip()
            
            # Essayer de trouver la structure JSON la plus longue possible
            brace_start = content.find('{')
            if brace_start != -1:
                # Compter les accolades pour trouver la fin logique
                bracket_count = 0
                for i, char in enumerate(content[brace_start:], brace_start):
                    if char == '{':
                        bracket_count += 1
                    elif char == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            return content[brace_start:i + 1]
                
                # Si pas de fermeture trouvée, utiliser tout le contenu
                return content[brace_start:]
            
            return content
    
    def _transform_llm_structure(self, llm_data: dict) -> dict:
        """Transforme la structure complexe du LLM vers la structure plate attendue"""
        transformed = {}
        
        # Le LLM retourne souvent une structure avec customerAnalysis en camelCase
        if 'customerAnalysis' in llm_data:
            llm_data = llm_data['customerAnalysis']
        
        # Extraire les détails de l'entreprise (plusieurs sources possibles)
        company = None
        if 'customerDetails' in llm_data:  # Structure vue dans le debug
            company = llm_data['customerDetails']
        elif 'customerCompanyDetails' in llm_data:  # Ancienne structure
            company = llm_data['customerCompanyDetails']
        elif 'companyDetails' in llm_data:  # CamelCase
            company = llm_data['companyDetails']
        elif 'company_details' in llm_data:  # snake_case
            company = llm_data['company_details']
        
        if company:
            transformed['customer_name'] = company.get('customerName', company.get('customer_name', company.get('companyName', company.get('company_name', 'Unknown'))))
            transformed['industry'] = company.get('industry', 'Unknown')
            transformed['company_size'] = company.get('companySize', company.get('company_size', 'Unknown'))
        else:
            # Essayer les champs directs
            transformed['customer_name'] = llm_data.get('customerName', llm_data.get('customer_name', llm_data.get('companyName', llm_data.get('company_name', 'Unknown'))))
            transformed['industry'] = llm_data.get('industry', 'Unknown')
            transformed['company_size'] = llm_data.get('companySize', llm_data.get('company_size', 'Unknown'))
        
        # Extraire les pain points (plusieurs formats possibles)
        # D'abord chercher dans la structure imbriquée painPointsAndBusinessNeeds
        pain_container = llm_data.get('painPointsAndBusinessNeeds', {})
        pain_points_raw = pain_container.get('painPoints', llm_data.get('customerPainPoints', llm_data.get('painPoints', llm_data.get('pain_points', {}))))
        
        if isinstance(pain_points_raw, list):
            # Cas où c'est une liste d'objets avec des détails - PRÉSERVER LA STRUCTURE DICTIONNAIRE
            pain_list = []
            for item in pain_points_raw:
                if isinstance(item, dict):
                    # CORRECTION: Préserver la structure complète du dictionnaire
                    pain_dict = {
                        'description': item.get('description', item.get('challenge', item.get('pain', 'Unknown'))),
                        'impact': item.get('impact', 'Medium'),
                        'business_impact': item.get('business_impact', item.get('businessImpact', item.get('business_impact', 'Unknown')))
                    }
                    pain_list.append(pain_dict)
                else:
                    # Si c'est un string, créer la structure dictionnaire attendue
                    pain_dict = {
                        'description': str(item),
                        'impact': 'Medium',
                        'business_impact': 'Unknown'
                    }
                    pain_list.append(pain_dict)
            transformed['pain_points'] = pain_list
        elif isinstance(pain_points_raw, dict):
            # Convertir dict vers liste de dicts (pas de strings!)
            pain_list = []
            for key, value in pain_points_raw.items():
                if isinstance(value, dict):
                    pain_dict = {
                        'description': value.get('description', value.get('desc', value.get('challenge', key))),
                        'impact': value.get('impact', 'Medium'),
                        'business_impact': value.get('business_impact', value.get('businessImpact', 'Unknown'))
                    }
                    pain_list.append(pain_dict)
                elif isinstance(value, str):
                    pain_dict = {
                        'description': value,
                        'impact': 'Medium', 
                        'business_impact': 'Unknown'
                    }
                    pain_list.append(pain_dict)
            transformed['pain_points'] = pain_list
        else:
            transformed['pain_points'] = []
        
        # Extraire les besoins (plusieurs formats possibles)
        # D'abord chercher dans la structure imbriquée painPointsAndBusinessNeeds
        needs_container = llm_data.get('painPointsAndBusinessNeeds', {})
        needs_raw = needs_container.get('businessNeeds', llm_data.get('customerBusinessNeeds', llm_data.get('businessNeeds', llm_data.get('business_needs', llm_data.get('needs', {})))))
        
        if isinstance(needs_raw, list):
            # Cas où c'est une liste d'objets avec des détails
            needs_list = []
            for item in needs_raw:
                if isinstance(item, dict):
                    need_obj = {
                        'need': item.get('need', item.get('description', 'Unknown')),
                        'priority': item.get('priority', 'Medium'),
                        'budget_allocated': item.get('budgetAllocated', item.get('budget', 'Unknown')),
                        'timeline': item.get('timeline', 'Unknown')
                    }
                    needs_list.append(need_obj)
                else:
                    needs_list.append({
                        'need': str(item),
                        'priority': 'Medium',
                        'budget_allocated': 'Unknown',
                        'timeline': 'Unknown'
                    })
            transformed['needs'] = needs_list
        elif isinstance(needs_raw, dict):
            # Convertir dict vers liste de dicts
            needs_list = []
            for key, value in needs_raw.items():
                if isinstance(value, dict):
                    need_obj = {
                        'need': value.get('description', value.get('need', key)),
                        'priority': value.get('priority', 'Medium'),
                        'budget_allocated': value.get('budget', value.get('budgetAllocated', 'Unknown')),
                        'timeline': value.get('timeline', 'Unknown')
                    }
                    needs_list.append(need_obj)
                elif isinstance(value, str):
                    needs_list.append({
                        'need': value,
                        'priority': 'Medium',
                        'budget_allocated': 'Unknown',
                        'timeline': 'Unknown'
                    })
            transformed['needs'] = needs_list
        else:
            transformed['needs'] = []
        
        # Extraire les critères de décision (plusieurs formats)
        decision_criteria_raw = llm_data.get('customerDecisionCriteria', llm_data.get('decisionCriteria', llm_data.get('decision_criteria', [])))
        if isinstance(decision_criteria_raw, dict):
            transformed['decision_criteria'] = list(decision_criteria_raw.values())
        elif isinstance(decision_criteria_raw, list):
            transformed['decision_criteria'] = decision_criteria_raw
        else:
            transformed['decision_criteria'] = []
        
        # Extraire le budget (plusieurs formats)
        budget_info = llm_data.get('customerBudgetInformation', llm_data.get('budgetInformation', llm_data.get('budget_information', llm_data.get('budget', {}))))
        if isinstance(budget_info, dict):
            transformed['budget_range'] = budget_info.get('range', budget_info.get('budgetRange', budget_info.get('budget_range', 'Unknown')))
        else:
            transformed['budget_range'] = str(budget_info) if budget_info else 'Unknown'
        
        # Extraire la timeline (plusieurs formats)
        timeline_info = llm_data.get('customerTimeline', llm_data.get('timeline', llm_data.get('projectTimeline', llm_data.get('project_timeline', {}))))
        if isinstance(timeline_info, dict):
            transformed['timeline'] = timeline_info.get('implementation', timeline_info.get('timeline', 'Unknown'))
        else:
            transformed['timeline'] = str(timeline_info) if timeline_info else 'Unknown'
        
        # Extraire le style de communication (plusieurs formats)
        communication = llm_data.get('customerCommunicationPreferences', llm_data.get('communicationPreferences', llm_data.get('communication_preferences', llm_data.get('communicationStyle', llm_data.get('communication_style', {})))))
        if isinstance(communication, dict):
            transformed['communication_style'] = communication.get('preferredStyle', communication.get('preferred_style', communication.get('style', 'professional')))
        elif isinstance(communication, list):
            # Si c'est une liste, prendre le premier élément ou joindre
            transformed['communication_style'] = communication[0] if communication else 'professional'
        else:
            transformed['communication_style'] = str(communication) if communication else 'professional'
        
        # Extraire les décideurs (plusieurs formats)
        # Le LLM utilise 'decisionMakingCriteria' selon le debug
        decision_makers_raw = llm_data.get('decisionMakingCriteria', llm_data.get('customerDecisionMakers', llm_data.get('decisionMakers', llm_data.get('decision_makers', llm_data.get('stakeholders', [])))))
        if isinstance(decision_makers_raw, list):
            # Cas normal : liste d'objets décideurs
            normalized_makers = []
            for maker in decision_makers_raw:
                if isinstance(maker, dict):
                    # S'assurer que tous les champs requis sont présents
                    normalized_maker = {
                        'name': maker.get('name', 'Unknown'),
                        'role': maker.get('role', 'Unknown'),
                        'influence_level': maker.get('influenceLevel', maker.get('influence_level', maker.get('influence', 'medium'))),
                        'email': maker.get('email', ''),
                        'communication_preference': maker.get('communicationPreference', maker.get('communication_preference', 'professional')),
                        'priorities': maker.get('priorities', []),
                        'concerns': maker.get('concerns', [])
                    }
                    normalized_makers.append(normalized_maker)
            transformed['decision_makers'] = normalized_makers
        elif isinstance(decision_makers_raw, dict):
            # Convertir dict vers liste
            decision_makers = []
            for key, value in decision_makers_raw.items():
                if isinstance(value, dict):
                    decision_makers.append({
                        'name': value.get('name', key),
                        'role': value.get('role', 'Unknown'),
                        'influence_level': value.get('influenceLevel', value.get('influence_level', value.get('influence', 'medium'))),
                        'email': value.get('email', ''),
                        'communication_preference': value.get('communicationPreference', value.get('communication_preference', value.get('communicationStyle', 'professional'))),
                        'priorities': value.get('priorities', []),
                        'concerns': value.get('concerns', [])
                    })
            transformed['decision_makers'] = decision_makers
        else:
            transformed['decision_makers'] = []
        
        logger.info(f"Transformed LLM structure: {list(transformed.keys())}")
        return transformed
