#!/usr/bin/env python3
"""
Test du workflow B2B Sales dans l'ordre spécifique demandé:
1. DocumentAnalysisAgent
2. MessageComposerAgentPure  
3. PersonalityClassifierAgentPure
4. StrategyAgentPure
"""

import json
import time
from datetime import datetime
from pathlib import Path

from agents.document_analysis_agent import DocumentAnalysisAgent
from agents.message_composer_agent_pure import MessageComposerAgentPure
from agents.personality_classifier_agent_pure import PersonalityClassifierAgentPure
from agents.strategy_agent_pure import StrategyAgentPure
from utils.models import WorkflowState

def load_test_customer():
    """Charge les données client de test"""
    test_file = Path("test_real_customer.json")
    with open(test_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_agent_behavior(agent_name: str, duration: float, state) -> str:
    """Analyse le comportement de l'agent (LLM vs Fallback)"""
    if duration < 30:
        return "🤖 MODE: FALLBACK (durée courte)"
    else:
        # Vérifier les warnings pour confirmer fallback
        if hasattr(state, 'warnings') and state.warnings:
            for warning in state.warnings:
                if 'fallback' in str(warning).lower():
                    return "⚠️ FALLBACK UTILISÉ"
        return "✅ LLM SUCCESS"

def print_agent_output(agent_name: str, result):
    """Affiche les outputs formatés de chaque agent"""
    print(f"\n📋 OUTPUT {agent_name}:")
    print("----------------------------------------")
    
    if "DocumentAnalysis" in agent_name:
        if result.customer_analysis:
            print(f"👤 Client: {result.customer_analysis.customer_name}")
            print(f"🏢 Industrie: {result.customer_analysis.industry}")
            print(f"📏 Taille: {result.customer_analysis.company_size}")
            print(f"🎯 Pain points: {len(result.customer_analysis.pain_points)}")
            print(f"📝 Besoins: {len(result.customer_analysis.needs)}")
            print(f"👥 Décideurs: {len(result.customer_analysis.decision_makers)}")
            if result.customer_analysis.needs:
                print("   Besoins détaillés:")
                for need in result.customer_analysis.needs[:2]:  # Limiter à 2 pour la lisibilité
                    if isinstance(need, dict):
                        print(f"     • {need.get('need', str(need))}")
    
    elif "MessageComposer" in agent_name:
        if result.conversation:
            print(f"💬 Messages générés: {len(result.conversation.messages)}")
            if result.conversation.messages:
                first_msg = result.conversation.messages[0]
                print(f"🎯 Type premier message: {first_msg.message_type}")
                print(f"📝 Expéditeur: {first_msg.sender}")
                print(f"📏 Longueur contenu: {len(first_msg.content)} caractères")
                # Compter les messages par type
                msg_types = {}
                for msg in result.conversation.messages:
                    msg_types[msg.message_type] = msg_types.get(msg.message_type, 0) + 1
                print(f"📊 Types de messages: {', '.join([f'{k}({v})' for k,v in msg_types.items()])}")
    
    elif "PersonalityClassifier" in agent_name:
        if result.personality_analysis:
            print(f"🧠 Profil: {result.personality_analysis.communication_style}")
            print(f"💬 Style décision: {result.personality_analysis.decision_making_style}")
            print(f"🎯 Recommandations: {len(result.personality_analysis.personality_based_recommendations)}")
            print(f"🚀 Drivers: {', '.join(result.personality_analysis.motivational_drivers[:3])}")
    
    elif "Strategy" in agent_name:
        if result.strategy_analysis:
            print(f"🎯 Score efficacité: {result.strategy_analysis.overall_effectiveness}/10")
            print(f"⚡ Méthodologie: {result.strategy_analysis.methodology_assessment}")
            print(f"🏆 Positionnement: {result.strategy_analysis.competitive_positioning}")
            print(f"💡 Recommandations: {len(result.strategy_analysis.recommendations) if result.strategy_analysis.recommendations else 0}")
            print(f"💪 Points forts: {len(result.strategy_analysis.strengths) if result.strategy_analysis.strengths else 0}")

def test_custom_order_workflow():
    """Test le workflow dans l'ordre personnalisé"""
    print("🚀 TEST WORKFLOW B2B SALES - ORDRE PERSONNALISÉ")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Charger les données de test
    customer_data = load_test_customer()
    print(f"📁 Fichier test: test_real_customer.json")
    print(f"📊 Input data: {len(json.dumps(customer_data))} caractères")
    print(f"🏢 Entreprise: {customer_data.get('customer_name', 'Non spécifié')}")
    
    initial_state = WorkflowState()
    
    results = {}
    
    # AGENT 1: DocumentAnalysisAgent
    print(f"\n🔍 AGENT 1: DocumentAnalysisAgent")
    print("-" * 50)
    
    doc_agent = DocumentAnalysisAgent()
    start_time = time.time()
    
    # Préparer l'état initial avec les paramètres requis
    initial_state.customer_json_path = "test_real_customer.json"
    initial_state.company_pdf_path = None
    
    doc_result = doc_agent.execute(initial_state)
    doc_duration = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"📊 ANALYSE AGENT: DocumentAnalysisAgent")
    print(f"{'='*60}")
    print(f"⏱️  Durée d'exécution: {doc_duration:.2f} secondes")
    print(f"✅ Status: {doc_result.status}")
    if doc_result.warnings:
        print(f"⚠️  Warnings ({len(doc_result.warnings)}):")
        for warning in doc_result.warnings:
            print(f"   • {warning}")
    
    behavior_analysis = analyze_agent_behavior("DocumentAnalysisAgent", doc_duration, doc_result)
    print(f"🤖 MODE: {'LLM ACTIF (durée longue)' if doc_duration >= 30 else 'FALLBACK (durée courte)'}")
    print(f"🎯 RÉSULTAT: {behavior_analysis}")
    
    print_agent_output("DocumentAnalysisAgent", doc_result)
    results["DocumentAnalysisAgent"] = (doc_result, doc_duration, behavior_analysis)
    
    # AGENT 2: MessageComposerAgentPure
    print(f"\n💬 AGENT 2: MessageComposerAgentPure")
    print("-" * 50)
    
    message_agent = MessageComposerAgentPure()
    start_time = time.time()
    message_result = message_agent.execute(doc_result)
    message_duration = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"📊 ANALYSE AGENT: MessageComposerAgentPure")
    print(f"{'='*60}")
    print(f"⏱️  Durée d'exécution: {message_duration:.2f} secondes")
    print(f"✅ Status: {message_result.status}")
    if message_result.warnings:
        print(f"⚠️  Warnings ({len(message_result.warnings)}):")
        for warning in message_result.warnings:
            print(f"   • {warning}")
    
    behavior_analysis = analyze_agent_behavior("MessageComposerAgentPure", message_duration, message_result)
    print(f"🤖 MODE: {'LLM ACTIF (durée longue)' if message_duration >= 30 else 'FALLBACK (durée courte)'}")
    print(f"🎯 RÉSULTAT: {behavior_analysis}")
    
    print_agent_output("MessageComposerAgentPure", message_result)
    results["MessageComposerAgentPure"] = (message_result, message_duration, behavior_analysis)
    
    # AGENT 3: PersonalityClassifierAgentPure
    print(f"\n🧠 AGENT 3: PersonalityClassifierAgentPure")
    print("-" * 50)
    
    personality_agent = PersonalityClassifierAgentPure()
    start_time = time.time()
    personality_result = personality_agent.execute(message_result)
    personality_duration = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"📊 ANALYSE AGENT: PersonalityClassifierAgentPure")
    print(f"{'='*60}")
    print(f"⏱️  Durée d'exécution: {personality_duration:.2f} secondes")
    print(f"✅ Status: {personality_result.status}")
    if personality_result.warnings:
        print(f"⚠️  Warnings ({len(personality_result.warnings)}):")
        for warning in personality_result.warnings:
            print(f"   • {warning}")
    
    behavior_analysis = analyze_agent_behavior("PersonalityClassifierAgentPure", personality_duration, personality_result)
    print(f"🤖 MODE: {'LLM ACTIF (durée longue)' if personality_duration >= 30 else 'FALLBACK (durée courte)'}")
    print(f"🎯 RÉSULTAT: {behavior_analysis}")
    
    print_agent_output("PersonalityClassifierAgentPure", personality_result)
    results["PersonalityClassifierAgentPure"] = (personality_result, personality_duration, behavior_analysis)
    
    # AGENT 4: StrategyAgentPure
    print(f"\n🎯 AGENT 4: StrategyAgentPure")
    print("-" * 50)
    
    strategy_agent = StrategyAgentPure()
    start_time = time.time()
    strategy_result = strategy_agent.execute(personality_result)
    strategy_duration = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"📊 ANALYSE AGENT: StrategyAgentPure")
    print(f"{'='*60}")
    print(f"⏱️  Durée d'exécution: {strategy_duration:.2f} secondes")
    print(f"✅ Status: {strategy_result.status}")
    if strategy_result.warnings:
        print(f"⚠️  Warnings ({len(strategy_result.warnings)}):")
        for warning in strategy_result.warnings:
            print(f"   • {warning}")
    
    behavior_analysis = analyze_agent_behavior("StrategyAgentPure", strategy_duration, strategy_result)
    print(f"🤖 MODE: {'LLM ACTIF (durée longue)' if strategy_duration >= 30 else 'FALLBACK (durée courte)'}")
    print(f"🎯 RÉSULTAT: {behavior_analysis}")
    
    print_agent_output("StrategyAgentPure", strategy_result)
    results["StrategyAgentPure"] = (strategy_result, strategy_duration, behavior_analysis)
    
    # Résumé final
    print(f"\n{'='*70}")
    print("📊 RÉSUMÉ DU WORKFLOW COMPLET")
    print(f"{'='*70}")
    
    total_duration = sum(duration for _, duration, _ in results.values())
    print(f"⏱️  Durée totale: {total_duration:.2f} secondes")
    
    for agent_name, (result, duration, behavior) in results.items():
        status_icon = "✅" if "SUCCESS" in behavior else "⚠️" if "FALLBACK" in behavior else "❌"
        print(f"{status_icon} {agent_name}: {duration:.2f}s - {behavior}")
    
    return strategy_result, results

if __name__ == "__main__":
    try:
        final_state, results = test_custom_order_workflow()
        print(f"\n🎉 TEST TERMINÉ AVEC SUCCÈS!")
        print(f"🔗 État final disponible pour analyse approfondie")
        
    except Exception as e:
        print(f"\n❌ Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()
