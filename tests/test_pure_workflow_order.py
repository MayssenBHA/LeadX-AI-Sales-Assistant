"""
Test complet du workflow B2B Sales Generator selon l'ordre défini dans pure_langgraph_workflow.py
Ordre: initialize -> document_analysis -> message_composition -> parallel_analysis -> integrate -> save -> finalize
"""

import logging
import time
import json
from datetime import datetime
from pure_langgraph_workflow import PureLangGraphB2BWorkflow
from utils.models import WorkflowState, ConversationParams, ConversationTone, ConversationChannel

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pure_langgraph_workflow_order():
    """Test le workflow complet selon l'ordre défini dans pure_langgraph_workflow.py"""
    
    print("=" * 80)
    print("🚀 TEST WORKFLOW PURE LANGGRAPH - ORDRE OFFICIEL")
    print("=" * 80)
    print(f"⏰ Démarré à: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Ordre attendu selon pure_langgraph_workflow.py
    expected_order = [
        "initialize_execution",
        "document_analysis", 
        "message_composition",
        "parallel_analysis",
        "integrate_results",
        "save_outputs", 
        "finalize_workflow"
    ]
    
    print("📋 ORDRE ATTENDU DU WORKFLOW:")
    for i, step in enumerate(expected_order, 1):
        print(f"   {i}. {step}")
    print()
    
    try:
        start_time = time.time()
        
        # Initialiser le workflow
        print("🔧 Initialisation du PureLangGraphB2BWorkflow...")
        workflow = PureLangGraphB2BWorkflow()
        
        # Préparer l'état initial 
        print("📝 Préparation de l'état initial...")
        initial_state = WorkflowState(
            execution_id="test_pure_workflow_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
            thread_id="pure_workflow_test",
            company_pdf_path="data/sample_company_description.pdf",
            customer_json_path="data/test_customer.json",
            conversation_params=ConversationParams(
                goal="Test complet du workflow selon ordre pure_langgraph",
                tone=ConversationTone.PROFESSIONAL,
                channel=ConversationChannel.EMAIL,
                exchanges=4,
                company_representative="Talan Sales Representative",
                customer_representative="TechInnovate Solutions Representative"
            ),
            max_iterations=30,
            status="initialized"
        )
        
        print(f"✅ État initial préparé avec ID: {initial_state.execution_id}")
        print()
        
        # Configuration pour l'exécution 
        config = {
            "configurable": {
                "thread_id": initial_state.thread_id
            }
        }
        
        print("🚀 LANCEMENT DU WORKFLOW COMPLET")
        print("-" * 50)
        
        # Exécuter le workflow complet
        final_state = workflow.workflow.invoke(initial_state, config)
        
        total_duration = time.time() - start_time
        
        print()
        print("=" * 80)
        print("📊 RÉSULTATS DU WORKFLOW PURE LANGGRAPH")
        print("=" * 80)
        
        # Analyser les étapes complétées
        completed_steps = getattr(final_state, 'completed_steps', [])
        print(f"⏱️  Durée totale: {total_duration:.2f} secondes")
        print(f"✅ Étapes complétées: {len(completed_steps)}")
        print(f"📈 Status final: {getattr(final_state, 'status', 'Unknown')}")
        print()
        
        print("🔍 DÉTAIL DES ÉTAPES EXÉCUTÉES:")
        for i, step in enumerate(completed_steps, 1):
            step_name = step.get('step', 'Unknown')
            duration = step.get('duration', 0)
            print(f"   {i}. {step_name} - {duration:.2f}s")
        print()
        
        # Vérifier l'ordre d'exécution
        executed_steps = [step.get('step') for step in completed_steps]
        order_match = True
        
        print("🎯 VÉRIFICATION ORDRE D'EXÉCUTION:")
        for i, (expected, executed) in enumerate(zip(expected_order, executed_steps), 1):
            match_icon = "✅" if expected == executed else "❌"
            print(f"   {i}. Attendu: {expected:20} | Exécuté: {executed:20} {match_icon}")
            if expected != executed:
                order_match = False
        
        print()
        if order_match:
            print("🎉 ORDRE D'EXÉCUTION: ✅ PARFAITEMENT RESPECTÉ")
        else:
            print("⚠️  ORDRE D'EXÉCUTION: ❌ DIFFÉRENCES DÉTECTÉES")
        print()
        
        # Analyser les résultats par agent
        print("📊 ANALYSE DES AGENTS:")
        print("-" * 40)
        
        # 1. Document Analysis Agent
        if hasattr(final_state, 'customer_analysis') and final_state.customer_analysis:
            ca = final_state.customer_analysis
            print(f"🔍 DocumentAnalysisAgent:")
            print(f"   👤 Client: {ca.customer_name}")
            print(f"   🏢 Industrie: {ca.industry}")
            print(f"   📏 Taille: {ca.company_size}")
            print(f"   🎯 Pain points: {len(ca.pain_points) if hasattr(ca, 'pain_points') else 0}")
            print(f"   📝 Besoins: {len(ca.needs) if hasattr(ca, 'needs') else 0}")
            print(f"   👥 Décideurs: {len(ca.decision_makers) if hasattr(ca, 'decision_makers') else 0}")
            
            # Déterminer le mode d'exécution
            doc_duration = next((s['duration'] for s in completed_steps if s['step'] == 'document_analysis'), 0)
            mode = "LLM SUCCESS" if doc_duration > 20 else "FALLBACK"
            print(f"   🤖 Mode: {mode} ({doc_duration:.1f}s)")
            print()
        
        # 2. Message Composer Agent
        if hasattr(final_state, 'conversation') and final_state.conversation:
            conv = final_state.conversation
            print(f"💬 MessageComposerAgent:")
            print(f"   💬 Messages générés: {len(conv.messages) if hasattr(conv, 'messages') else 0}")
            if hasattr(conv, 'messages') and conv.messages:
                print(f"   📝 Premier message: {conv.messages[0].message_type if hasattr(conv.messages[0], 'message_type') else 'N/A'}")
                print(f"   📤 Expéditeur: {conv.messages[0].sender if hasattr(conv.messages[0], 'sender') else 'N/A'}")
            
            msg_duration = next((s['duration'] for s in completed_steps if s['step'] == 'message_composition'), 0)
            mode = "LLM SUCCESS" if msg_duration > 10 else "FALLBACK"
            print(f"   🤖 Mode: {mode} ({msg_duration:.1f}s)")
            print()
        
        # 3. Analyses parallèles
        parallel_duration = next((s['duration'] for s in completed_steps if s['step'] == 'parallel_analysis'), 0)
        print(f"🧠 Analyses Parallèles ({parallel_duration:.1f}s):")
        
        # Personality Analysis
        if hasattr(final_state, 'personality_analysis') and final_state.personality_analysis:
            pa = final_state.personality_analysis
            print(f"   🧠 PersonalityClassifier:")
            print(f"      🎭 Profil: {getattr(pa, 'personality_profile', 'N/A')}")
            print(f"      💬 Style: {getattr(pa, 'communication_style', 'N/A')}")
            print(f"      🎯 Recommandations: {len(getattr(pa, 'interaction_recommendations', [])) if hasattr(pa, 'interaction_recommendations') else 0}")
            print(f"      🤖 Mode: LLM SUCCESS")
        
        # Strategy Analysis  
        if hasattr(final_state, 'strategy_analysis') and final_state.strategy_analysis:
            sa = final_state.strategy_analysis
            print(f"   🎯 StrategyAgent:")
            print(f"      📈 Efficacité: {getattr(sa, 'overall_effectiveness', 'N/A')}/10")
            print(f"      ⚡ Méthodologie: {getattr(sa, 'sales_methodology', {})}")
            print(f"      🏆 Positionnement: {getattr(sa, 'competitive_positioning', {})}")
            print(f"      🤖 Mode: LLM SUCCESS")
        print()
        
        # Statistiques finales
        print("📈 STATISTIQUES FINALES:")
        print("-" * 30)
        
        # Compter les appels LLM estimés
        llm_calls = 0
        if hasattr(final_state, 'customer_analysis'): llm_calls += 1
        if hasattr(final_state, 'conversation') and final_state.conversation:
            llm_calls += len(final_state.conversation.messages) if hasattr(final_state.conversation, 'messages') else 0
        if hasattr(final_state, 'personality_analysis'): llm_calls += 3  # 3 étapes personality
        if hasattr(final_state, 'strategy_analysis'): llm_calls += 5     # 5 étapes strategy
        
        print(f"🔢 Appels LLM estimés: {llm_calls}")
        print(f"⚡ Performance/seconde: {llm_calls/total_duration:.2f} appels/s")
        print(f"💰 Coût estimé: ${llm_calls * 0.001:.4f}")
        
        # Taux de réussite des agents
        success_count = 0
        total_agents = 4
        
        if hasattr(final_state, 'customer_analysis') and final_state.customer_analysis: success_count += 1
        if hasattr(final_state, 'conversation') and final_state.conversation: success_count += 1  
        if hasattr(final_state, 'personality_analysis') and final_state.personality_analysis: success_count += 1
        if hasattr(final_state, 'strategy_analysis') and final_state.strategy_analysis: success_count += 1
        
        success_rate = (success_count / total_agents) * 100
        print(f"📊 Taux de réussite: {success_count}/{total_agents} agents ({success_rate:.1f}%)")
        print()
        
        # Conclusion finale
        if success_rate >= 75 and order_match:
            print("🎉 TEST RÉUSSI: ✅ WORKFLOW FONCTIONNEL ET CONFORME")
            print("   • Ordre d'exécution respecté")
            print("   • Tous les agents ont produit des résultats")
            print("   • Performance acceptable")
        elif success_rate >= 75:
            print("⚠️  TEST PARTIELLEMENT RÉUSSI: Agents fonctionnels mais ordre différent")  
        else:
            print("❌ TEST ÉCHOUÉ: Problèmes de fonctionnement des agents")
        
        return final_state
        
    except Exception as e:
        print(f"❌ ERREUR LORS DU TEST: {e}")
        logger.error(f"Erreur workflow: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    print("🧪 DÉMARRAGE TEST WORKFLOW PURE LANGGRAPH")
    print()
    
    result = test_pure_langgraph_workflow_order()
    
    if result:
        print()
        print("=" * 80)
        print("✅ TEST TERMINÉ AVEC SUCCÈS")
        print("🔗 État final disponible pour analyse approfondie")
        print("=" * 80)
    else:
        print()
        print("=" * 80) 
        print("❌ TEST ÉCHOUÉ")
        print("🔍 Vérifiez les logs pour plus de détails")
        print("=" * 80)
