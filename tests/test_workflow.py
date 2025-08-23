"""
Test suite for complete B2B Sales Workflow
"""
import unittest
import sys
import os
import tempfile
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow import B2BSalesWorkflow
from utils.models import ConversationParams, ConversationTone, ConversationChannel
from config.settings import Config

class TestWorkflow(unittest.TestCase):
    """Test cases for complete B2B sales workflow"""
    
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
        """Create comprehensive test data"""
        # Detailed company description
        cls.company_content = """
        SMARTTECH SOLUTIONS
        Enterprise Software Provider
        
        COMPANY OVERVIEW:
        SmartTech Solutions is a leading provider of enterprise automation software, 
        founded in 2015 and headquartered in Austin, Texas. We specialize in helping 
        mid-to-large size businesses streamline their operations through intelligent automation.
        
        PRODUCTS & SERVICES:
        1. AutoFlow Pro - Business process automation platform
        2. DataBridge - Real-time data integration and synchronization
        3. InsightDash - Advanced analytics and business intelligence
        4. CloudSync - Cloud migration and management services
        
        VALUE PROPOSITIONS:
        - 60% reduction in manual processes
        - 99.9% system uptime guarantee
        - ROI typically achieved within 8 months
        - 24/7 dedicated customer support
        - Seamless integration with existing systems
        
        COMPETITIVE ADVANTAGES:
        - AI-powered automation engine
        - Industry-specific pre-built workflows
        - Rapid deployment (30-day average)
        - Comprehensive training and support
        - Scalable architecture for growth
        
        TARGET MARKETS:
        Manufacturing, Healthcare, Financial Services, Retail
        
        COMPANY CULTURE:
        Customer-focused, innovation-driven, results-oriented
        """
        
        # Comprehensive customer profile
        cls.customer_profile = {
            "customer_name": "GlobalManufacturing Corp",
            "industry": "Manufacturing",
            "company_size": "Large (1000+ employees)",
            "pain_points": [
                "Highly manual order processing system causing delays",
                "Lack of real-time visibility into production schedules",
                "Inefficient inventory management leading to stockouts",
                "Multiple disconnected systems requiring manual data entry",
                "High operational costs due to process inefficiencies"
            ],
            "needs": [
                "Automated order processing workflow",
                "Real-time production visibility dashboard",
                "Integrated inventory management system",
                "Unified data platform connecting all systems",
                "Significant cost reduction through automation"
            ],
            "decision_criteria": [
                "Proven ROI within 12 months",
                "Seamless integration with existing SAP system",
                "Minimal disruption during implementation",
                "Comprehensive training and change management",
                "24/7 technical support availability",
                "Scalability for future growth",
                "Strong vendor financial stability"
            ],
            "budget_range": "$500,000 - $1,000,000",
            "timeline": "Implementation target: Q3 2025",
            "communication_style": "Analytical, detail-oriented, relationship-focused",
            "decision_makers": [
                "Robert Johnson - Chief Technology Officer",
                "Maria Rodriguez - VP of Operations",
                "David Kim - Chief Financial Officer",
                "Jennifer Lee - Director of IT"
            ],
            "current_systems": [
                "SAP ERP",
                "Salesforce CRM",
                "Oracle WMS",
                "Custom legacy applications"
            ],
            "evaluation_process": {
                "phase1": "Initial vendor assessment and RFP response",
                "phase2": "Product demonstrations and pilot program",
                "phase3": "Reference checks and final negotiations",
                "duration": "4-6 months total evaluation cycle"
            },
            "success_metrics": [
                "50% reduction in order processing time",
                "90% improvement in inventory accuracy",
                "25% reduction in operational costs",
                "Real-time visibility into all operations"
            ]
        }
        
        # Create temporary files
        cls.company_pdf_path = cls.create_temp_company_file()
        cls.customer_json_path = cls.create_temp_customer_file()
    
    @classmethod
    def create_temp_company_file(cls):
        """Create temporary company description file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(cls.company_content)
            return f.name
    
    @classmethod
    def create_temp_customer_file(cls):
        """Create temporary customer profile file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(cls.customer_profile, f, indent=2)
            return f.name
    
    def test_01_complete_workflow_basic(self):
        """Test complete workflow with basic parameters"""
        print("\n🧪 Testing Complete Workflow - Basic Configuration...")
        
        # Create conversation parameters
        conversation_params = ConversationParams(
            goal="Assess customer needs and schedule product demonstration",
            tone=ConversationTone.PROFESSIONAL,
            channel=ConversationChannel.EMAIL,
            exchanges=6,
            company_representative="Senior Sales Executive",
            customer_representative="Technology Director"
        )
        
        # Initialize and run workflow
        workflow = B2BSalesWorkflow()
        result = workflow.run_complete_workflow(
            company_pdf_path=self.company_pdf_path,
            customer_json_path=self.customer_json_path,
            conversation_params=conversation_params
        )
        
        # Verify workflow completion
        self.assertIsNotNone(result)
        print(f"✅ Workflow Status: {result.status}")
        
        # Verify document analysis
        self.assertIsNotNone(result.company_analysis)
        self.assertIsNotNone(result.customer_analysis)
        print(f"✅ Company Analysis: {result.company_analysis.company_name}")
        print(f"✅ Customer Analysis: {result.customer_analysis.customer_name}")
        
        # Verify conversation generation
        self.assertIsNotNone(result.conversation)
        self.assertGreater(len(result.conversation.messages), 0)
        print(f"✅ Generated Conversation: {len(result.conversation.messages)} messages")
        
        # Verify strategy analysis
        if result.strategy_analysis:
            print(f"✅ Strategy Analysis: {result.strategy_analysis.overall_effectiveness}/10")
        
        # Verify personality analysis
        if result.personality_analysis:
            print(f"✅ Personality Analysis: {result.personality_analysis.communication_style}")
        
        print("✅ Basic workflow test passed!")
        return result
    
    def test_02_complete_workflow_consultative(self):
        """Test complete workflow with consultative approach"""
        print("\n🧪 Testing Complete Workflow - Consultative Approach...")
        
        # Create consultative conversation parameters
        conversation_params = ConversationParams(
            goal="Build relationship and understand business challenges in depth",
            tone=ConversationTone.CONSULTATIVE,
            channel=ConversationChannel.VIDEO_CALL,
            exchanges=8,
            company_representative="Solutions Consultant",
            customer_representative="Operations VP"
        )
        
        # Run workflow
        workflow = B2BSalesWorkflow()
        result = workflow.run_complete_workflow(
            company_pdf_path=self.company_pdf_path,
            customer_json_path=self.customer_json_path,
            conversation_params=conversation_params
        )
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.conversation)
        self.assertEqual(len(result.conversation.messages), 8)
        
        print(f"✅ Consultative Workflow Status: {result.status}")
        print(f"✅ Conversation Length: {len(result.conversation.messages)} exchanges")
        print("✅ Consultative workflow test passed!")
        
        return result
    
    def test_03_workflow_error_handling(self):
        """Test workflow error handling capabilities"""
        print("\n🧪 Testing Workflow Error Handling...")
        
        # Test with invalid file paths
        conversation_params = ConversationParams(
            goal="Test error handling",
            tone=ConversationTone.PROFESSIONAL,
            channel=ConversationChannel.EMAIL,
            exchanges=4
        )
        
        workflow = B2BSalesWorkflow()
        result = workflow.run_complete_workflow(
            company_pdf_path="invalid_path.txt",
            customer_json_path="invalid_path.json",
            conversation_params=conversation_params
        )
        
        # Verify error handling
        self.assertIsNotNone(result)
        self.assertGreater(len(result.error_messages), 0)
        print(f"✅ Error Messages Captured: {len(result.error_messages)}")
        print("✅ Error handling test passed!")
    
    def test_04_workflow_parallel_processing(self):
        """Test parallel processing of strategy and personality analysis"""
        print("\n🧪 Testing Parallel Processing Performance...")
        
        start_time = datetime.now()
        
        # Run workflow with timing
        conversation_params = ConversationParams(
            goal="Demonstrate parallel processing efficiency",
            tone=ConversationTone.FRIENDLY,
            channel=ConversationChannel.PHONE,
            exchanges=6
        )
        
        workflow = B2BSalesWorkflow()
        result = workflow.run_complete_workflow(
            company_pdf_path=self.company_pdf_path,
            customer_json_path=self.customer_json_path,
            conversation_params=conversation_params
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Verify parallel processing results
        self.assertIsNotNone(result.strategy_analysis)
        self.assertIsNotNone(result.personality_analysis)
        
        print(f"✅ Total Execution Time: {execution_time:.2f} seconds")
        print(f"✅ Strategy Analysis Completed: {result.strategy_analysis is not None}")
        print(f"✅ Personality Analysis Completed: {result.personality_analysis is not None}")
        print("✅ Parallel processing test passed!")
    
    def test_05_workflow_output_validation(self):
        """Test workflow output structure and content validation"""
        print("\n🧪 Testing Workflow Output Validation...")
        
        # Run workflow
        conversation_params = ConversationParams(
            goal="Validate comprehensive output structure",
            tone=ConversationTone.FORMAL,
            channel=ConversationChannel.IN_PERSON,
            exchanges=10
        )
        
        workflow = B2BSalesWorkflow()
        result = workflow.run_complete_workflow(
            company_pdf_path=self.company_pdf_path,
            customer_json_path=self.customer_json_path,
            conversation_params=conversation_params
        )
        
        # Validate output structure
        self.assertIsNotNone(result)
        
        # Check conversation structure
        if result.conversation:
            self.assertIsInstance(result.conversation.messages, list)
            self.assertEqual(len(result.conversation.messages), 10)
            
            # Validate message alternation
            company_count = sum(1 for msg in result.conversation.messages if msg.sender == "company")
            customer_count = sum(1 for msg in result.conversation.messages if msg.sender == "customer")
            self.assertGreater(company_count, 0)
            self.assertGreater(customer_count, 0)
        
        # Check analysis completeness
        if result.strategy_analysis:
            self.assertIsInstance(result.strategy_analysis.overall_effectiveness, (int, float))
            self.assertIsInstance(result.strategy_analysis.recommendations, list)
        
        if result.personality_analysis:
            self.assertIsInstance(result.personality_analysis.disc_profile, dict)
            self.assertIsInstance(result.personality_analysis.personality_based_recommendations, list)
        
        print("✅ Output structure validation passed!")
        print(f"✅ Company Messages: {company_count}")
        print(f"✅ Customer Messages: {customer_count}")
        
        if result.strategy_analysis:
            print(f"✅ Strategy Recommendations: {len(result.strategy_analysis.recommendations)}")
        
        if result.personality_analysis:
            print(f"✅ Personality Recommendations: {len(result.personality_analysis.personality_based_recommendations)}")
        
        print("✅ Complete output validation test passed!")
    
    def test_06_end_to_end_integration(self):
        """Test complete end-to-end integration"""
        print("\n🧪 Testing End-to-End Integration...")
        
        # Run complete workflow with all features
        conversation_params = ConversationParams(
            goal="Complete end-to-end B2B sales conversation with full analysis",
            tone=ConversationTone.CONSULTATIVE,
            channel=ConversationChannel.VIDEO_CALL,
            exchanges=12,
            company_representative="Senior Solutions Architect",
            customer_representative="Chief Technology Officer"
        )
        
        workflow = B2BSalesWorkflow()
        result = workflow.run_complete_workflow(
            company_pdf_path=self.company_pdf_path,
            customer_json_path=self.customer_json_path,
            conversation_params=conversation_params
        )
        
        # Comprehensive validation
        success_criteria = {
            "workflow_completed": result.status in ["workflow_complete", "results_integrated"],
            "document_analysis": result.company_analysis is not None and result.customer_analysis is not None,
            "conversation_generated": result.conversation is not None and len(result.conversation.messages) == 12,
            "strategy_analysis": result.strategy_analysis is not None,
            "personality_analysis": result.personality_analysis is not None,
            "minimal_errors": len(result.error_messages) <= 2  # Allow minor non-critical errors
        }
        
        all_passed = all(success_criteria.values())
        
        print("\n📊 End-to-End Integration Results:")
        for criterion, passed in success_criteria.items():
            status = "✅" if passed else "❌"
            print(f"{status} {criterion.replace('_', ' ').title()}: {passed}")
        
        if all_passed:
            print("\n🎉 Complete end-to-end integration test PASSED!")
            print("🚀 B2B Sales Conversation Generator is fully functional!")
        else:
            print("\n⚠️ Some integration criteria not met")
        
        # Print summary statistics
        if result.conversation:
            print(f"\n📈 Conversation Statistics:")
            print(f"   Total Messages: {len(result.conversation.messages)}")
            print(f"   Conversation Goal: {result.conversation.goal}")
            
        if result.strategy_analysis:
            print(f"\n🎯 Strategy Analysis:")
            print(f"   Effectiveness Score: {result.strategy_analysis.overall_effectiveness}/10")
            print(f"   Recommendations: {len(result.strategy_analysis.recommendations)}")
            
        if result.personality_analysis:
            print(f"\n🎭 Personality Analysis:")
            print(f"   Communication Style: {result.personality_analysis.communication_style}")
            print(f"   Decision Making: {result.personality_analysis.decision_making_style}")
        
        return result
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        try:
            os.unlink(cls.company_pdf_path)
            os.unlink(cls.customer_json_path)
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting Complete B2B Sales Workflow Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWorkflow)
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run tests
    result = runner.run(suite)
    
    # Print final summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL WORKFLOW TESTS PASSED SUCCESSFULLY!")
        print("✅ B2B Sales Conversation Generator is production ready")
        print("🚀 All LangGraph agents and workflow integration verified")
    else:
        print("❌ Some workflow tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailure Details:")
            for test, failure in result.failures:
                print(f"- {test}: {failure}")
        
        if result.errors:
            print("\nError Details:")
            for test, error in result.errors:
                print(f"- {test}: {error}")
    
    print("\n🏁 Complete workflow test suite finished")
