"""
Test suite for individual LangGraph agents
"""
import unittest
import sys
import os
import tempfile
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.document_analysis_agent import DocumentAnalysisAgent
from agents.message_composer_agent import MessageComposerAgent
from agents.strategy_agent import StrategyAgent
from agents.personality_classifier_agent import PersonalityClassifierAgent
from utils.models import WorkflowState, ConversationParams, ConversationTone, ConversationChannel
from config.settings import Config

class TestAgents(unittest.TestCase):
    """Test cases for individual LangGraph agents"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            print(f"Configuration error: {e}")
            print("Please ensure GROQ_API_KEY is set in your .env file")
            sys.exit(1)
        
        # Create sample data files
        cls.setup_test_data()
    
    @classmethod
    def setup_test_data(cls):
        """Create temporary test data files"""
        # Sample company text (simulating PDF content)
        cls.company_text = """
        TechSolutions Inc.
        Leading Provider of Business Automation Software
        
        Our company specializes in workflow automation and business process optimization.
        We offer cloud-based solutions that help companies reduce manual work by 60%.
        
        Key Products:
        - WorkflowPro: Automated business process management
        - DataSync: Real-time data integration platform
        - Analytics Plus: Business intelligence and reporting
        
        Value Propositions:
        - 50% reduction in operational costs
        - 99.9% uptime guarantee
        - 24/7 customer support
        - ROI within 6 months
        
        Target Markets: Mid-size businesses, Manufacturing, Healthcare
        """
        
        # Sample customer profile
        cls.customer_data = {
            "customer_name": "Manufacturing Corp",
            "industry": "Manufacturing",
            "company_size": "Medium (200-500 employees)",
            "pain_points": [
                "Manual data entry processes",
                "Lack of real-time visibility",
                "High operational costs"
            ],
            "needs": [
                "Process automation",
                "Real-time reporting",
                "Cost reduction"
            ],
            "decision_criteria": [
                "ROI within 12 months",
                "Easy integration",
                "Reliable support"
            ],
            "communication_style": "Direct and analytical",
            "decision_makers": ["John Smith - CTO", "Jane Doe - Operations Manager"]
        }
        
        # Create temporary files
        cls.company_pdf_path = cls.create_temp_pdf()
        cls.customer_json_path = cls.create_temp_json()
    
    @classmethod
    def create_temp_pdf(cls):
        """Create a temporary text file simulating PDF content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(cls.company_text)
            return f.name
    
    @classmethod
    def create_temp_json(cls):
        """Create a temporary JSON file with customer data"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(cls.customer_data, f, indent=2)
            return f.name
    
    def test_01_document_analysis_agent(self):
        """Test Document Analysis Agent"""
        print("\n🧪 Testing Document Analysis Agent...")
        
        agent = DocumentAnalysisAgent()
        
        # Test with sample data
        result = agent.run(
            company_pdf_path=self.company_pdf_path,
            customer_json_path=self.customer_json_path
        )
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "analysis_complete")
        self.assertIsNotNone(result.company_analysis)
        self.assertIsNotNone(result.customer_analysis)
        
        print(f"✅ Company Analysis: {result.company_analysis.company_name}")
        print(f"✅ Customer Analysis: {result.customer_analysis.customer_name}")
        print("✅ Document Analysis Agent test passed!")
        
        return result
    
    def test_02_message_composer_agent(self):
        """Test Message Composer Agent"""
        print("\n🧪 Testing Message Composer Agent...")
        
        # First run document analysis
        doc_result = self.test_01_document_analysis_agent()
        
        # Set up conversation parameters
        conversation_params = ConversationParams(
            goal="Schedule a product demo",
            tone=ConversationTone.PROFESSIONAL,
            channel=ConversationChannel.EMAIL,
            exchanges=4
        )
        
        # Create state with analysis results
        state = WorkflowState(
            company_analysis=doc_result.company_analysis,
            customer_analysis=doc_result.customer_analysis,
            conversation_params=conversation_params
        )
        
        # Test message composer
        agent = MessageComposerAgent()
        result = agent.run(state)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "conversation_complete")
        self.assertIsNotNone(result.conversation)
        self.assertGreater(len(result.conversation.messages), 0)
        
        print(f"✅ Generated {len(result.conversation.messages)} messages")
        print("✅ Message Composer Agent test passed!")
        
        return result
    
    def test_03_strategy_agent(self):
        """Test Strategy Agent"""
        print("\n🧪 Testing Strategy Agent...")
        
        # First run message composition
        compose_result = self.test_02_message_composer_agent()
        
        # Test strategy agent
        agent = StrategyAgent()
        result = agent.run(compose_result)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.strategy_analysis)
        self.assertIsInstance(result.strategy_analysis.overall_effectiveness, (int, float))
        
        print(f"✅ Strategy Score: {result.strategy_analysis.overall_effectiveness}/10")
        print(f"✅ Recommendations: {len(result.strategy_analysis.recommendations)}")
        print("✅ Strategy Agent test passed!")
        
        return result
    
    def test_04_personality_classifier_agent(self):
        """Test Personality Classifier Agent"""
        print("\n🧪 Testing Personality Classifier Agent...")
        
        # First run message composition
        compose_result = self.test_02_message_composer_agent()
        
        # Test personality agent
        agent = PersonalityClassifierAgent()
        result = agent.run(compose_result)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.personality_analysis)
        self.assertIsInstance(result.personality_analysis.disc_profile, dict)
        
        print(f"✅ Communication Style: {result.personality_analysis.communication_style}")
        print(f"✅ DISC Profile: {result.personality_analysis.disc_profile}")
        print("✅ Personality Classifier Agent test passed!")
        
        return result
    
    def test_05_all_agents_integration(self):
        """Test all agents working together"""
        print("\n🧪 Testing All Agents Integration...")
        
        # Run complete workflow simulation
        doc_result = self.test_01_document_analysis_agent()
        compose_result = self.test_02_message_composer_agent()
        strategy_result = self.test_03_strategy_agent()
        personality_result = self.test_04_personality_classifier_agent()
        
        # Verify all components are present
        self.assertIsNotNone(doc_result.company_analysis)
        self.assertIsNotNone(doc_result.customer_analysis)
        self.assertIsNotNone(compose_result.conversation)
        self.assertIsNotNone(strategy_result.strategy_analysis)
        self.assertIsNotNone(personality_result.personality_analysis)
        
        print("✅ All agents integration test passed!")
        print("\n🎉 All individual agent tests completed successfully!")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        try:
            os.unlink(cls.company_pdf_path)
            os.unlink(cls.customer_json_path)
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting LangGraph Agents Test Suite")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAgents)
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run tests
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
        print("✅ All LangGraph agents are working correctly")
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    print("🏁 Test suite completed")
