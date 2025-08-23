"""
Enhanced B2B Sales Conversation Generator with Modern UI Design
Following LeadX template styling with blue theme
"""
import streamlit as st
import json
import tempfile
import os
from datetime import datetime
from pure_langgraph_workflow import PureLangGraphB2BWorkflow
from utils.models import ConversationParams, WorkflowState, MessageType, ConversationChannel, ConversationTone
from config.settings import Config

# Configure Streamlit page
st.set_page_config(
    page_title="LeadX - B2B Sales Conversation Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS following the LeadX template
def load_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-blue: #4258dc;
        --secondary-blue: #5c6bc0;
        --light-blue: #7986cb;
        --accent-blue: #9fa8da;
        --background-gray: #f8f9fa;
        --card-blue: #3f51b5;
        --success-green: #28a745;
        --warning-orange: #ff9800;
        --danger-red: #dc3545;
        --info-cyan: #17a2b8;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: var(--background-gray);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: white;
        border-radius: 0;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Dashboard title */
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 15px;
        background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Metric containers */
    .metric-container {
        background: var(--card-blue);
        padding: 25px 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 20px rgba(63, 81, 181, 0.2);
        transition: transform 0.3s ease;
        margin-bottom: 20px;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 8px;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Card styling */
    .stContainer > div {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
        margin-bottom: 20px;
    }
    
    .stContainer > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.12);
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--primary-blue);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(66, 88, 220, 0.3);
    }
    
    .stButton > button:hover {
        background: var(--secondary-blue);
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(66, 88, 220, 0.4);
    }
    
    /* Success button variant */
    .success-button > button {
        background: var(--success-green) !important;
        color: white !important;
    }
    
    .success-button > button:hover {
        background: #218838 !important;
    }
    
    /* Warning button variant */
    .warning-button > button {
        background: var(--warning-orange) !important;
        color: white !important;
    }
    
    /* Danger button variant */
    .danger-button > button {
        background: var(--danger-red) !important;
        color: white !important;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e9ecef;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 0.2rem rgba(66, 88, 220, 0.25);
    }
    
    /* Select box styling */
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e9ecef;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border-radius: 12px;
        border: 2px dashed var(--accent-blue);
        background: rgba(66, 88, 220, 0.05);
    }
    
    /* Message containers */
    .company-message {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid var(--primary-blue);
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(66, 88, 220, 0.1);
    }
    
    .customer-message {
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #9c27b0;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(156, 39, 176, 0.1);
    }
    
    /* Analysis tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: var(--background-gray);
        border-radius: 8px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 6px;
        color: var(--primary-blue);
        font-weight: 500;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-blue);
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue));
        color: white;
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar logo */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    
    /* Usage guide */
    .usage-guide {
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid var(--primary-blue);
        margin: 20px 0;
    }
    
    /* Floating action elements */
    .floating-element {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        background: var(--primary-blue);
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(66, 88, 220, 0.4);
        animation: pulse 3s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 20px rgba(66, 88, 220, 0.4); }
        50% { box-shadow: 0 4px 30px rgba(66, 88, 220, 0.8); transform: scale(1.05); }
        100% { box-shadow: 0 4px 20px rgba(66, 88, 220, 0.4); }
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-blue), var(--accent-blue));
    }
    
    /* Metrics styling */
    .css-1629p8f {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--primary-blue);
    }
    
    /* Custom spacing */
    .section-spacing {
        margin: 2rem 0;
    }
    
    /* Icon styling */
    .icon {
        color: var(--primary-blue);
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'conversation_messages' not in st.session_state:
        st.session_state.conversation_messages = []
    if 'customer_info' not in st.session_state:
        st.session_state.customer_info = None
    if 'current_company_message' not in st.session_state:
        st.session_state.current_company_message = ""
    if 'message_config' not in st.session_state:
        st.session_state.message_config = {}
    if 'show_edit_mode' not in st.session_state:
        st.session_state.show_edit_mode = False
    if 'personality_analysis' not in st.session_state:
        st.session_state.personality_analysis = None
    if 'strategy_analysis' not in st.session_state:
        st.session_state.strategy_analysis = None
    if 'pending_talan_message' not in st.session_state:
        st.session_state.pending_talan_message = None
    if 'pending_message_config' not in st.session_state:
        st.session_state.pending_message_config = None

def display_sidebar():
    """Display the styled sidebar"""
    with st.sidebar:
        # Logo section
        st.markdown("""
        <div class="sidebar-logo">
            <h2 style="color: var(--primary-blue); font-weight: bold; margin: 0;">
                🚀 LeadX
            </h2>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">B2B Sales Generator</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # API Key validation
        if not Config.GROQ_API_KEY:
            st.error("❌ Groq API Key not configured!")
            st.info("Please set GROQ_API_KEY in your .env file")
            st.stop()
        else:
            st.success("✅ API Connected")
        
        st.markdown("---")
        
        # File upload section
        st.markdown("### 📁 Customer Data")
        customer_json = st.file_uploader(
            "Upload Customer Profile",
            type=['json'],
            help="Upload customer profile JSON data"
        )
        
        if customer_json and st.session_state.customer_info is None:
            process_customer_data(customer_json)
        
        st.markdown("---")
        
        # Message configuration
        st.markdown("### ⚙️ Message Settings")
        
        message_type = st.selectbox(
            "Message Type",
            options=[t.value for t in MessageType],
            index=0,
            help="Select the type of sales message"
        )
        
        channel = st.selectbox(
            "Channel",
            options=[c.value for c in ConversationChannel],
            index=0,
            help="Select communication channel"
        )
        
        goal = st.text_input(
            "Goal",
            value="Schedule a product demo and assess customer needs",
            help="What do you want to achieve?"
        )
        
        st.markdown("---")
        
        # Conversation controls
        st.markdown("### 🔄 Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", help="Start fresh", key="clear_btn"):
                clear_conversation()
        
        with col2:
            if st.session_state.conversation_history:
                st.metric("Exchanges", len(st.session_state.conversation_history))
        
        # Usage guide
        with st.expander("📖 Quick Guide", expanded=False):
            st.markdown("""
            **How to use:**
            
            1. **📁 Upload** customer JSON
            2. **⚙️ Configure** message settings  
            3. **🚀 Generate** company message
            4. **✏️ Review** and edit message
            5. **💾 Save** & get response
            6. **📊 Analyze** strategy insights
            7. **🔄 Continue** conversation
            
            **Features:**
            - 🧵 Threaded conversations
            - ✏️ Message editing
            - 📊 Smart analysis
            - 🎯 Strategy insights
            """)
        
        return customer_json, message_type, channel, goal

def display_dashboard_header():
    """Display the main dashboard header"""
    st.markdown("""
    <h1 class="dashboard-title">
        🤖 B2B Sales Conversation Generator
    </h1>
    <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
        Generate intelligent sales conversations with AI-powered strategy analysis
    </p>
    """, unsafe_allow_html=True)

def display_metrics_row():
    """Display key metrics"""
    if st.session_state.customer_info:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-value">{}</div>
                <div class="metric-label">Exchanges</div>
            </div>
            """.format(len(st.session_state.conversation_history)), unsafe_allow_html=True)
        
        with col2:
            company_name = st.session_state.customer_info.get("company_name", "Unknown")[:10]
            st.markdown("""
            <div class="metric-container">
                <div class="metric-value" style="font-size: 1.5rem;">{}</div>
                <div class="metric-label">Customer</div>
            </div>
            """.format(company_name), unsafe_allow_html=True)
        
        with col3:
            industry = st.session_state.customer_info.get("industry", "Unknown")[:12]
            st.markdown("""
            <div class="metric-container">
                <div class="metric-value" style="font-size: 1.5rem;">{}</div>
                <div class="metric-label">Industry</div>
            </div>
            """.format(industry), unsafe_allow_html=True)
        
        with col4:
            status = "Active" if st.session_state.show_edit_mode else "Ready"
            st.markdown("""
            <div class="metric-container">
                <div class="metric-value" style="font-size: 1.8rem;">{}</div>
                <div class="metric-label">Status</div>
            </div>
            """.format(status), unsafe_allow_html=True)

def display_conversation_history():
    """Display conversation history with enhanced styling"""
    if st.session_state.conversation_history:
        st.markdown("### 💬 Conversation History")
        
        for i, entry in enumerate(st.session_state.conversation_history, 1):
            is_latest = (i == len(st.session_state.conversation_history))
            title_prefix = "🆕 " if is_latest else ""
            
            with st.expander(f"{title_prefix}Exchange {i} - {entry.get('message_type', 'Unknown')} via {entry.get('channel', 'Unknown')}", expanded=is_latest):
                
                # Company message
                st.markdown("**🏢 Your Message:**")
                st.markdown(f"""
                <div class="company-message">
                    {entry.get('company_message', '')}
                </div>
                """, unsafe_allow_html=True)
                
                # Customer response
                st.markdown("**👤 Customer Response:**")
                st.markdown(f"""
                <div class="customer-message">
                    {entry.get('customer_response', '')}
                </div>
                """, unsafe_allow_html=True)
                
                # Analysis tabs
                if entry.get('strategy_analysis') or entry.get('personality_analysis'):
                    tab1, tab2 = st.tabs(["🎯 Personality Analysis", "📈 Strategy Analysis"])
                    
                    with tab1:
                        if entry.get('personality_analysis'):
                            personality = entry['personality_analysis']
                            # Use the proper display function for full 5-profile classification
                            display_personality_analysis(personality)
                        else:
                            st.info("Personality analysis not available")
                    
                    with tab2:
                        if entry.get('strategy_analysis'):
                            strategy = entry['strategy_analysis']
                            # Use the proper display function for comprehensive strategy analysis
                            display_strategy_analysis(strategy)
                        else:
                            st.info("Strategy analysis not available")
                
                # Timestamp
                timestamp = entry.get('timestamp', '')
                if timestamp:
                    st.caption(f"📅 {timestamp}")

def display_message_generation_section(message_type, channel, goal):
    """Display message generation section"""
    st.markdown("### 📝 Generate New Message")
    
    if st.session_state.customer_info:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            exchange_num = len(st.session_state.conversation_history) + 1
            st.info(f"**Exchange {exchange_num}:** {message_type} message via {channel}")
        
        with col2:
            if st.button("🚀 Generate Message", use_container_width=True, type="primary"):
                generate_company_message(message_type, channel, goal)
        
        # Show message review section if needed
        if st.session_state.current_company_message:
            display_message_review_section(message_type, channel, goal)
    else:
        st.warning("⏳ Please upload a customer JSON file to get started")

def display_message_review_section(message_type, channel, goal):
    """Display message review and editing section"""
    st.markdown("---")
    st.markdown("### ✏️ Review & Edit Message")
    
    edited_message = st.text_area(
        "Edit your message:",
        value=st.session_state.current_company_message,
        height=200,
        help="Review and modify the generated message as needed"
    )
    
    if edited_message != st.session_state.current_company_message:
        st.session_state.current_company_message = edited_message
    
    # Action buttons with custom styling
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="warning-button">', unsafe_allow_html=True)
        if st.button("🔄 Regenerate", help="Generate new version", use_container_width=True):
            generate_company_message(message_type, channel, goal)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="success-button">', unsafe_allow_html=True)
        if st.button("💾 Save & Send", help="Finalize and get response", use_container_width=True):
            finalize_message_and_generate_response(message_type, channel, goal)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="danger-button">', unsafe_allow_html=True)
        if st.button("❌ Cancel", help="Discard message", use_container_width=True):
            st.session_state.current_company_message = ""
            st.session_state.show_edit_mode = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def display_strategy_analysis(strategy_analysis):
    """Display strategy analysis with enhanced styling"""
    if not strategy_analysis:
        st.warning("No strategy analysis available")
        return
    
    # Handle both object and dict formats
    if hasattr(strategy_analysis, 'overall_effectiveness'):
        # Object format
        overall_effectiveness = strategy_analysis.overall_effectiveness
        methodology_assessment = getattr(strategy_analysis, 'methodology_assessment', {})
        competitive_positioning = getattr(strategy_analysis, 'competitive_positioning', {})
        objection_handling = getattr(strategy_analysis, 'objection_handling', {})
        value_proposition_delivery = getattr(strategy_analysis, 'value_proposition_delivery', {})
        recommendations = strategy_analysis.recommendations
        improvement_areas = strategy_analysis.improvement_areas
        strengths = strategy_analysis.strengths
        next_steps = strategy_analysis.next_steps
        raw_details = getattr(strategy_analysis, 'raw_details', {})
    else:
        # Dict format
        overall_effectiveness = strategy_analysis.get('overall_effectiveness', 0)
        methodology_assessment = strategy_analysis.get('methodology_assessment', {})
        competitive_positioning = strategy_analysis.get('competitive_positioning', {})
        objection_handling = strategy_analysis.get('objection_handling', {})
        value_proposition_delivery = strategy_analysis.get('value_proposition_delivery', {})
        recommendations = strategy_analysis.get('recommendations', [])
        improvement_areas = strategy_analysis.get('improvement_areas', [])
        strengths = strategy_analysis.get('strengths', [])
        next_steps = strategy_analysis.get('next_steps', [])
        raw_details = strategy_analysis.get('raw_details', {})
    # 📝 Full LLM Step Outputs (Raw Details)
    if raw_details:
        with st.expander("🔍 Show Full LLM Step Outputs (Raw Details)"):
            import json
            st.code(json.dumps(raw_details, indent=2, ensure_ascii=False), language="json")

    # 📊 Key Effectiveness Metrics
    st.markdown("### 📊 Sales Strategy Assessment")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Effectiveness", f"{overall_effectiveness:.1f}/10")
    
    with col2:
        methodology_score = methodology_assessment.get('score', 0) if isinstance(methodology_assessment, dict) else 0
        st.metric("Methodology Score", f"{methodology_score:.1f}/10" if methodology_score else "N/A")
    
    with col3:
        positioning_score = competitive_positioning.get('score', 0) if isinstance(competitive_positioning, dict) else 0
        st.metric("Positioning Score", f"{positioning_score:.1f}/10" if positioning_score else "N/A")
    
    with col4:
        value_prop_score = value_proposition_delivery.get('score', 0) if isinstance(value_proposition_delivery, dict) else 0
        st.metric("Value Prop Score", f"{value_prop_score:.1f}/10" if value_prop_score else "N/A")

    # 🎯 Detailed Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Strengths
        st.markdown("### ✅ Conversation Strengths")
        if strengths:
            for strength in strengths:
                st.markdown(f"• {strength}")
        else:
            st.info("No specific strengths identified")
        
        # Methodology Assessment
        if methodology_assessment and isinstance(methodology_assessment, dict):
            st.markdown("### 🔄 Sales Methodology")
            for key, value in methodology_assessment.items():
                if key != 'score':
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    
    with col2:
        # Improvement Areas
        st.markdown("### 🔧 Areas for Improvement")
        if improvement_areas:
            for area in improvement_areas:
                st.markdown(f"• {area}")
        else:
            st.info("No major improvement areas identified")
        
        # Competitive Positioning
        if competitive_positioning and isinstance(competitive_positioning, dict):
            st.markdown("### 🏆 Competitive Position")
            for key, value in competitive_positioning.items():
                if key != 'score':
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

    # 💡 Strategic Recommendations
    st.markdown("### 💡 Strategic Recommendations")
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.info("No specific recommendations available")

    # 👉 Next Steps  
    st.markdown("### � Recommended Next Steps")
    if next_steps:
        for i, step in enumerate(next_steps, 1):
            st.markdown(f"{i}. {step}")
    else:
        st.info("No specific next steps defined")

    # 🎤 Objection Handling Assessment
    if objection_handling and isinstance(objection_handling, dict):
        st.markdown("### 🎤 Objection Handling Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            for key, value in list(objection_handling.items())[:len(objection_handling)//2]:
                if key != 'score':
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        
        with col2:
            for key, value in list(objection_handling.items())[len(objection_handling)//2:]:
                if key != 'score':
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

    # 📈 Value Proposition Delivery
    if value_proposition_delivery and isinstance(value_proposition_delivery, dict):
        st.markdown("### 📈 Value Proposition Delivery")
        for key, value in value_proposition_delivery.items():
            if key != 'score':
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

def display_personality_analysis(personality_analysis):
    """Display personality analysis with enhanced styling - Updated for 5-profile B2B system"""
    # DEBUG: Show what the frontend is actually receiving
    st.write("## [DEBUG] Raw personality_analysis received by UI:")
    st.write(personality_analysis)
    if not personality_analysis:
        st.warning("No personality analysis available")
        return
    
    # Check if we have the new format with personality_profile
    if hasattr(personality_analysis, 'personality_profile'):
        personality_profile = personality_analysis.personality_profile
        profile_confidence = getattr(personality_analysis, 'profile_confidence', 'N/A')
        disc_profile = personality_analysis.disc_profile
        communication_style = personality_analysis.communication_style
        decision_making_style = personality_analysis.decision_making_style
        relationship_orientation = getattr(personality_analysis, 'relationship_orientation', 'N/A')
        risk_tolerance = personality_analysis.risk_tolerance
        information_processing = personality_analysis.information_processing
        motivational_drivers = getattr(personality_analysis, 'motivational_drivers', [])
        personality_based_recommendations = personality_analysis.personality_based_recommendations
        optimal_communication_approach = getattr(personality_analysis, 'optimal_communication_approach', {})
        objection_handling_style = getattr(personality_analysis, 'objection_handling_style', 'N/A')
    elif isinstance(personality_analysis, dict):
        personality_profile = personality_analysis.get('personality_profile', 'Unknown')
        profile_confidence = personality_analysis.get('profile_confidence', 'N/A')
        disc_profile = personality_analysis.get('disc_profile', {})
        communication_style = personality_analysis.get('communication_style', 'Unknown')
        decision_making_style = personality_analysis.get('decision_making_style', 'Unknown')
        relationship_orientation = personality_analysis.get('relationship_orientation', 'N/A')
        risk_tolerance = personality_analysis.get('risk_tolerance', 'Unknown')
        information_processing = personality_analysis.get('information_processing', 'Unknown')
        motivational_drivers = personality_analysis.get('motivational_drivers', [])
        personality_based_recommendations = personality_analysis.get('personality_based_recommendations', [])
        optimal_communication_approach = personality_analysis.get('optimal_communication_approach', {})
        objection_handling_style = personality_analysis.get('objection_handling_style', 'N/A')
    else:
        # Fallback for old format
        disc_profile = getattr(personality_analysis, "disc_profile", {})
        personality_profile = "Unknown"
        profile_confidence = "N/A"
        communication_style = getattr(personality_analysis, "communication_style", "Unknown")
        decision_making_style = getattr(personality_analysis, "decision_making_style", "Unknown")
        relationship_orientation = getattr(personality_analysis, "relationship_orientation", "N/A")
        risk_tolerance = getattr(personality_analysis, "risk_tolerance", "Unknown")
        information_processing = getattr(personality_analysis, "information_processing", "Unknown")
        motivational_drivers = getattr(personality_analysis, "motivational_drivers", [])
        personality_based_recommendations = getattr(personality_analysis, "personality_based_recommendations", [])
        optimal_communication_approach = {}
        objection_handling_style = "N/A"

    # 🎯 B2B Personality Profile Header
    st.markdown("### 🎯 B2B Personality Profile Classification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Profile classification with confidence
        profile_color = {
            "Tech-Savvy Innovator": "🔧",
            "Business-Oriented Decision Maker": "📊", 
            "Cost-Conscious Pragmatist": "💰",
            "Early Adopter Innovator": "🚀",
            "Relationship-Driven Connector": "🤝"
        }.get(personality_profile, "🎯")
        
        st.markdown(f"**{profile_color} Primary Profile: {personality_profile}**")
        st.markdown(f"**Confidence: {profile_confidence}**")
        
        # Relationship orientation
        st.markdown(f"**Focus: {relationship_orientation}**")
        
    with col2:
        # Communication and decision making style
        st.markdown("**Communication Profile:**")
        st.markdown(f"• Style: {communication_style}")
        st.markdown(f"• Decision Making: {decision_making_style}")
        st.markdown(f"• Risk Tolerance: {risk_tolerance}")
        st.markdown(f"• Info Processing: {information_processing}")

    # DISC Profile
    if disc_profile:
        st.markdown("### 📊 DISC Profile Breakdown")
        col1, col2, col3, col4 = st.columns(4)
        
        disc_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
        disc_traits = ["D", "I", "S", "C"]
        disc_names = ["Dominance", "Influence", "Steadiness", "Compliance"]
        
        for i, (trait, name, color) in enumerate(zip(disc_traits, disc_names, disc_colors)):
            with [col1, col2, col3, col4][i]:
                score = disc_profile.get(trait, 0)
                st.metric(label=f"{trait} - {name}", value=f"{score}%")
    
    # Motivational Drivers
    if motivational_drivers:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Key Motivational Drivers")
            for driver in motivational_drivers:
                st.markdown(f"• {driver}")
        
        with col2:
            st.markdown("### 📋 Sales Approach Recommendations")
            for rec in personality_based_recommendations[:3]:  # Show first 3
                st.markdown(f"• {rec}")
    
    # Optimal Communication Approach
    if optimal_communication_approach:
        st.markdown("### 📞 Optimal Communication Strategy")
        col1, col2 = st.columns(2)
        
        with col1:
            if isinstance(optimal_communication_approach, dict):
                for key, value in optimal_communication_approach.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        
        with col2:
            st.markdown(f"**Objection Handling Style:** {objection_handling_style}")

# Utility functions
def process_customer_data(customer_json):
    """
    Process and store customer data - ONLY document analysis at this stage.
    Args:
        customer_json: Uploaded file-like object containing customer profile JSON.
    Returns:
        True if processing is successful, False otherwise.
    """
    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_json:
            tmp_json.write(customer_json.getvalue())
            customer_json_path = tmp_json.name
        
        # Use the Pure LangGraph B2B Sales Workflow - ONLY document analysis step
        workflow = PureLangGraphB2BWorkflow()
        
        # Run ONLY the document analysis step (not the complete workflow)
        result = workflow.run_document_analysis_only(customer_json_path)
        
        st.write(f"🔍 Debug: Workflow status: {result.status}")  # Debug info
        st.write(f"🔍 Debug: Customer analysis exists: {hasattr(result, 'customer_analysis')}")
        st.write(f"🔍 Debug: Customer analysis value: {getattr(result, 'customer_analysis', 'NOT_FOUND')}")
        st.write(f"🔍 Debug: Customer analysis type: {type(getattr(result, 'customer_analysis', None))}")
        if hasattr(result, 'customer_analysis') and result.customer_analysis:
            st.write(f"🔍 Debug: Customer name: {getattr(result.customer_analysis, 'customer_name', 'NO_NAME')}")
        st.write(f"🔍 Debug: Result type: {type(result)}")
        st.write(f"🔍 Debug: Errors: {getattr(result, 'errors', 'NO_ERRORS')}")
        
        # Check the exact condition that's failing
        condition_result = result.status in ["document_analysis_complete", "awaiting_channel_selection"] and result.customer_analysis
        st.write(f"🔍 Debug: Condition result: {condition_result}")
        st.write(f"🔍 Debug: Status check: {result.status in ['document_analysis_complete', 'awaiting_channel_selection']}")
        st.write(f"🔍 Debug: Customer analysis bool: {bool(result.customer_analysis) if hasattr(result, 'customer_analysis') else 'NO_ATTR'}")
        
        # Check for successful document analysis
        if result.status in ["document_analysis_complete", "awaiting_channel_selection"] and result.customer_analysis:
            # Extract customer information from the workflow result
            customer_info = {
                "company_name": result.customer_analysis.customer_name,
                "industry": result.customer_analysis.industry,
                "company_size": result.customer_analysis.company_size,
                "pain_points": [{"title": pp.get("issue", ""), "description": pp.get("description", "")} for pp in result.customer_analysis.pain_points],
                "business_needs": [{"title": need.get("requirement", ""), "description": need.get("description", "")} for need in result.customer_analysis.needs],
                "decision_makers": result.customer_analysis.decision_makers,
                "communication_style": result.customer_analysis.communication_style
            }
            st.session_state.customer_info = customer_info
            st.session_state.workflow_state = result  # Store partial workflow state for later completion
            
            # Show success message
            st.success(f"✅ Customer data analyzed: {customer_info['company_name']}")
            st.info("📋 **Next Step**: Select message channel and type below to generate conversation")
            
            # Display ONLY customer profile analysis (no personality/strategy yet)
            st.subheader("🧠 Customer Profile Analysis")
            
            st.write("**Company Information:**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Company", customer_info['company_name'])
                st.metric("Industry", customer_info['industry'])
            with col2:
                st.metric("Company Size", customer_info['company_size'])
                st.metric("Communication Style", customer_info['communication_style'])
            
            if customer_info['pain_points']:
                st.write("**Pain Points:**")
                for pp in customer_info['pain_points']:
                    st.write(f"• **{pp['title']}**: {pp['description']}")
            
            if customer_info['business_needs']:
                st.write("**Business Needs:**")
                for need in customer_info['business_needs']:
                    st.write(f"• **{need['title']}**: {need['description']}")
                    
            # Show decision makers if available
            if customer_info.get('decision_makers'):
                st.write("**Decision Makers:**")
                for dm in customer_info['decision_makers']:
                    st.write(f"• **{dm.get('name', 'N/A')}** - {dm.get('role', 'N/A')}")
                    
            # Return True to indicate successful processing
            return True
        
        else:
            # Handle error case
            st.error(f"❌ Error processing customer data: {result.status}")
            if result.errors:
                for error in result.errors:
                    st.error(f"• {error}")
            return False
            
    except Exception as e:
        st.error(f"❌ Critical error: {str(e)}")
        return False

def generate_conversation_with_parameters(conversation_params):
    """Generate conversation using selected channel and message parameters"""
    try:
        # Get the stored workflow state from document analysis
        if 'workflow_state' not in st.session_state:
            st.error("❌ No customer data available. Please upload customer JSON first.")
            return None
        
        workflow_state = st.session_state.workflow_state
        workflow = PureLangGraphB2BWorkflow()
        
        # Run conversation generation with selected parameters
        result = workflow.run_conversation_generation(workflow_state, conversation_params)
        
        return result
        
    except Exception as e:
        st.error(f"❌ Error generating conversation: {str(e)}")
        return None

def display_conversation_results(result):
    """Display the complete conversation results with analysis"""
    st.markdown("---")
    st.subheader("💬 Generated Conversation")
    
    if result.conversation and result.conversation.messages:
        messages = result.conversation.messages
        
        # Show conversation overview
        st.info(f"📊 **Conversation Overview**: {len(messages)} messages generated")
        
        # Display messages
        for i, msg in enumerate(messages, 1):
            with st.container():
                if msg.sender == "company":
                    st.markdown(f"**🏢 TALAN TUNISIE - Message {i}** ({msg.message_type})")
                    st.markdown(f"""
                    <div style="background: #e8f4f8; padding: 1rem; border-radius: 8px; border-left: 4px solid #4258dc; margin: 0.5rem 0;">
                        {msg.content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"**👤 CLIENT - Message {i}** ({msg.message_type})")
                    st.markdown(f"""
                    <div style="background: #f0f8f0; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 0.5rem 0;">
                        {msg.content}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Show analysis results if available
        if result.personality_analysis or result.strategy_analysis:
            st.markdown("---")
            st.subheader("🧠 Analysis Results")
            
            analysis_tabs = st.tabs(["🎯 Personality Analysis", "📈 Strategy Analysis"])
            
            with analysis_tabs[0]:
                if result.personality_analysis:
                    # Use the proper display function for full 5-profile classification
                    display_personality_analysis(result.personality_analysis)
                else:
                    st.info("Personality analysis not available")
            
            with analysis_tabs[1]:
                if result.strategy_analysis:
                    # Use the proper display function for comprehensive strategy analysis
                    display_strategy_analysis(result.strategy_analysis)
                else:
                    st.info("Strategy analysis not available")
    
    else:
        st.error("❌ No conversation messages available")

def generate_single_message(message_type, channel, goal):
    """Generate a single Talan message for review"""
    try:
        # Get the stored workflow state from document analysis
        if 'workflow_state' not in st.session_state:
            st.error("❌ No customer data available. Please upload customer JSON first.")
            return
        
        # Check if we're already in review mode
        if hasattr(st.session_state, 'pending_talan_message') and st.session_state.pending_talan_message:
            display_message_review(message_type, channel, goal)
            return
        
        workflow_state = st.session_state.workflow_state
        workflow = PureLangGraphB2BWorkflow()
        
        # Create conversation parameters for this single Talan message
        conversation_params = ConversationParams(
            goal=goal,
            tone=ConversationTone.PROFESSIONAL,
            channel=getattr(ConversationChannel, channel),
            exchanges=1,  # Single exchange
            company_representative="Consultant Senior Talan Tunisie",
            customer_representative=f"Decision Maker at {st.session_state.customer_info['company_name']}"
        )
        
        # Update workflow state with current conversation history
        if hasattr(st.session_state, 'conversation_messages') and st.session_state.conversation_messages:
            # Create a conversation object with existing messages for context
            from utils.models import Conversation, Message
            
            existing_messages = []
            for msg in st.session_state.conversation_messages:
                existing_messages.append(Message(
                    sender=msg['sender'],
                    content=msg['content'],
                    message_type=msg.get('message_type', 'unknown'),
                    timestamp=datetime.now()
                ))
            
            workflow_state.conversation = Conversation(
                messages=existing_messages,
                conversation_id=f"talan_conv_{len(existing_messages)}",
                goal=goal,
                participants={"company": "Talan Tunisie", "customer": st.session_state.customer_info['company_name']},
                status="in_progress",
                channel=getattr(ConversationChannel, channel)
            )
        
        with st.spinner("🔄 Generating Talan message for your review..."):
            # Generate only the Talan message first
            result = generate_talan_message_only(workflow_state, conversation_params, message_type, channel)
            
            if result:
                # Store the generated message for review
                st.session_state.pending_talan_message = result
                st.session_state.pending_message_config = {
                    "message_type": message_type,
                    "channel": channel,
                    "goal": goal
                }
                st.success("✅ Talan message generated! Please review below.")
                st.rerun()
            else:
                st.error("❌ Failed to generate Talan message")
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def generate_talan_message_only(workflow_state, conversation_params, message_type, channel):
    """Generate only the Talan message for review"""
    try:
        from agents.message_composer_agent_pure import MessageComposerAgentPure

        # Use the message composer in talan_only mode to generate just the Talan message
        message_composer = MessageComposerAgentPure(mode="talan_only")
        result = message_composer.execute(workflow_state)

        if result.conversation and result.conversation.messages:
            # Find the Talan message (company sender)
            talan_messages = [msg for msg in result.conversation.messages if msg.sender == "company"]
            if talan_messages:
                return talan_messages[-1].content  # Get the last Talan message

        return None
    except Exception as e:
        st.error(f"❌ Error generating Talan message: {str(e)}")
        return None

def display_message_review(message_type, channel, goal):
    """Display the message review interface"""
    st.markdown("---")
    st.subheader("✏️ Review Talan Message")
    st.info("Please review the generated message. You can edit it, regenerate it, or approve it to get the customer response.")
    
    # Display the message for editing
    edited_message = st.text_area(
        "🏢 Talan Message:",
        value=st.session_state.pending_talan_message,
        height=150,
        help="Review and modify the generated Talan message as needed"
    )
    
    # Update the pending message if edited
    if edited_message != st.session_state.pending_talan_message:
        st.session_state.pending_talan_message = edited_message
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Regenerate", help="Generate a new version", use_container_width=True):
            # Clear the pending message and regenerate
            st.session_state.pending_talan_message = None
            st.session_state.pending_message_config = None
            generate_single_message(message_type, channel, goal)
    
    with col2:
        if st.button("✅ Approve & Get Response", help="Finalize message and generate customer response", use_container_width=True, type="primary"):
            finalize_talan_message_and_generate_response(message_type, channel, goal)
    
    with col3:
        if st.button("❌ Cancel", help="Discard this message", use_container_width=True):
            st.session_state.pending_talan_message = None
            st.session_state.pending_message_config = None
            st.rerun()

def finalize_talan_message_and_generate_response(message_type, channel, goal):
    """Finalize the Talan message and generate customer response"""
    try:
        if not st.session_state.pending_talan_message:
            st.error("❌ No pending message to finalize")
            return
        
        with st.spinner("🎭 Generating customer response..."):
            # Add the approved Talan message to conversation
            talan_message = {
                'sender': 'company',
                'content': st.session_state.pending_talan_message,
                'message_type': message_type,
                'channel': channel,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Generate customer response
            customer_response = generate_customer_response(talan_message, goal)
            
            if customer_response:
                # Add both messages to conversation history
                st.session_state.conversation_messages.append(talan_message)
                st.session_state.conversation_messages.append({
                    'sender': 'customer',
                    'content': customer_response,
                    'message_type': 'response',
                    'channel': channel,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Clear pending message
                st.session_state.pending_talan_message = None
                st.session_state.pending_message_config = None
                
                # Show success
                exchange_num = len(st.session_state.conversation_messages) // 2
                st.success(f"✅ Exchange {exchange_num} completed! Both Talan message and customer response added.")
                
                # Display the new exchange
                st.rerun()
            else:
                st.error("❌ Failed to generate customer response")
                
    except Exception as e:
        st.error(f"❌ Error finalizing message: {str(e)}")

def generate_customer_response(talan_message, goal):
    """Generate customer response to the approved Talan message"""
    try:
        from agents.message_composer_agent_pure import MessageComposerAgentPure
        from utils.models import Conversation, Message

        # Create a temporary conversation with just the Talan message
        temp_messages = []

        # Add existing conversation messages
        for msg in st.session_state.conversation_messages:
            temp_messages.append(Message(
                sender=msg['sender'],
                content=msg['content'],
                message_type=msg.get('message_type', 'unknown'),
                timestamp=datetime.now()
            ))

        # Add the new Talan message
        temp_messages.append(Message(
            sender=talan_message['sender'],
            content=talan_message['content'],
            message_type=talan_message['message_type'],
            timestamp=datetime.now()
        ))

        # Create workflow state for customer response generation
        workflow_state = st.session_state.workflow_state
        workflow_state.conversation = Conversation(
            messages=temp_messages,
            conversation_id=f"response_conv_{len(temp_messages)}",
            goal=goal,
            participants={"company": "Talan Tunisie", "customer": st.session_state.customer_info['company_name']},
            status="in_progress"
        )

        # Generate customer response using message composer in customer_only mode
        message_composer = MessageComposerAgentPure(mode="customer_only")
        result = message_composer.execute(workflow_state)

        if result.conversation and result.conversation.messages:
            # Find the customer response (last message from customer)
            customer_messages = [msg for msg in result.conversation.messages if msg.sender == "customer"]
            if customer_messages:
                return customer_messages[-1].content

        return None
    except Exception as e:
        st.error(f"❌ Error generating customer response: {str(e)}")
        return None

def clear_conversation():
    """Clear conversation history and reset state"""
    st.session_state.conversation_history = []
    st.session_state.current_company_message = ""
    st.session_state.show_edit_mode = False
    st.success("🗑️ Conversation cleared!")

def generate_company_message(message_type, channel, goal):
    """Generate the initial company message using the workflow"""
    if not st.session_state.customer_info:
        st.error("❌ No customer data available")
        return
    
    with st.spinner("🤖 Generating company message..."):
        try:
            # Check if we have a workflow result from the initial processing
            if hasattr(st.session_state, 'workflow_result') and st.session_state.workflow_result:
                workflow_result = st.session_state.workflow_result
                
                st.write(f"🔍 Debug: Workflow status in message generation: {workflow_result.status}")  # Debug info
                
                # Extract the generated conversation from the workflow result
                if workflow_result.conversation and len(workflow_result.conversation.messages) > 0:
                    st.write(f"🔍 Debug: Found {len(workflow_result.conversation.messages)} messages in conversation")  # Debug info
                    # Get the first company message
                    company_messages = [msg for msg in workflow_result.conversation.messages if msg.sender.lower() == "company"]
                    if company_messages:
                        st.write(f"🔍 Debug: Found {len(company_messages)} company messages")  # Debug info
                        st.session_state.current_company_message = company_messages[0].content
                        st.session_state.message_config = {
                            "type": message_type,
                            "channel": channel,
                            "goal": goal
                        }
                        st.session_state.show_edit_mode = True
                        st.success("✅ Message generated from workflow! Review below.")
                        st.rerun()
                        return
                    else:
                        st.write("🔍 Debug: No company messages found in conversation")  # Debug info
                else:
                    st.write("🔍 Debug: No conversation or messages found in workflow result")  # Debug info
                
                # If no pre-generated message, create a new one based on the analyses
                if workflow_result.strategy_analysis and workflow_result.personality_analysis:
                    st.write("🔍 Debug: Using strategy and personality analysis to create message")  # Debug info
                    # Use the strategy and personality analysis to craft a message
                    message_content = f"""
Dear {st.session_state.customer_info['company_name']} team,

{workflow_result.strategy_analysis.recommendations[0] if workflow_result.strategy_analysis.recommendations else 'I hope this message finds you well.'}

Based on our research, I understand that {st.session_state.customer_info['company_name']} operates in the {st.session_state.customer_info['industry']} industry. 

{workflow_result.personality_analysis.personality_based_recommendations[0] if workflow_result.personality_analysis.personality_based_recommendations else 'I would love to discuss how our solutions can help address your business challenges.'}

Would you be available for a brief conversation to explore how we might be able to support your goals?

Best regards,
Sales Representative
                    """.strip()
                    
                    st.session_state.current_company_message = message_content
                    st.session_state.message_config = {
                        "type": message_type,
                        "channel": channel,
                        "goal": goal
                    }
                    st.session_state.show_edit_mode = True
                    st.success("✅ Message generated based on analysis! Review below.")
                    st.rerun()
                    return
                else:
                    st.write("🔍 Debug: No strategy or personality analysis available")  # Debug info
            else:
                st.write("🔍 Debug: No workflow result available in session state")  # Debug info
            
            # Fallback: Generate a basic message
            st.write("🔍 Debug: Using fallback message generation")  # Debug info
            basic_message = f"""
Dear {st.session_state.customer_info['company_name']} team,

I hope this message finds you well. I'm reaching out because I believe our solutions could be valuable for {st.session_state.customer_info['company_name']} in the {st.session_state.customer_info['industry']} industry.

{goal}

Would you be interested in a brief conversation to explore potential opportunities?

Best regards,
Sales Representative
            """.strip()
            
            st.session_state.current_company_message = basic_message
            st.session_state.message_config = {
                "type": message_type,
                "channel": channel,
                "goal": goal
            }
            st.session_state.show_edit_mode = True
            st.success("✅ Basic message generated! Review below.")
            st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error generating message: {str(e)}")
            import traceback
            st.error(f"Details: {traceback.format_exc()}")

def finalize_message_and_generate_response(message_type, channel, goal):
    """Finalize the company message and generate customer response using workflow analysis"""
    if not st.session_state.current_company_message.strip():
        st.error("❌ Please provide a company message")
        return
    
    with st.spinner("🎭 Generating customer response using personality analysis..."):
        try:
            # Use the personality analysis from the workflow result to generate a response
            if hasattr(st.session_state, 'workflow_result') and st.session_state.workflow_result:
                workflow_result = st.session_state.workflow_result
                
                # Generate customer response based on personality analysis
                if workflow_result.personality_analysis:
                    personality = workflow_result.personality_analysis
                    
                    # Create a customer response based on the communication style
                    communication_style = personality.communication_style.lower()
                    if "analytical" in communication_style or "data" in communication_style:
                        response = f"""Thank you for reaching out. I'd like to understand more about your solution's specific capabilities and ROI metrics. Could you provide detailed information about how your solution addresses our industry challenges? I'd also need to see case studies with quantifiable results before proceeding."""
                    elif "direct" in communication_style or "driver" in communication_style:
                        response = f"""Interesting. What's the bottom line value proposition? I need to see clear business impact and timeline. If you can demonstrate concrete results, let's set up a brief call. Keep it focused - I have limited time."""
                    elif "expressive" in communication_style or "enthusiastic" in communication_style:
                        response = f"""This sounds promising! I'm always excited about innovative solutions that can help our team. I'd love to hear more about how this has helped other companies in our space. Can we schedule a call to discuss the possibilities?"""
                    elif "amiable" in communication_style or "supportive" in communication_style:
                        response = f"""Thank you for the thoughtful message. I appreciate you taking the time to research our company. I'd be happy to learn more about your solution, but I'll need to discuss this with my team first. Could you provide some initial information I can share with them?"""
                    else:
                        response = f"""Thank you for reaching out. I'm interested in learning more about your solution and how it might benefit {st.session_state.customer_info['company_name']}. Could you provide more details about your offering and perhaps schedule a brief introductory call?"""
                else:
                    # Fallback generic response
                    response = f"""Thank you for your message. I'm interested in learning more about how your solution might help {st.session_state.customer_info['company_name']}. Could you provide additional information about your offering?"""
                
                # Create the conversation entry
                new_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "company_message": st.session_state.current_company_message,
                    "customer_response": response,
                    "message_config": st.session_state.get("message_config", {}),
                    "message_type": message_type,
                    "channel": channel,
                    "goal": goal,
                    "personality_analysis": workflow_result.personality_analysis,
                    "strategy_analysis": workflow_result.strategy_analysis,
                    "analysis": {
                        "communication_style": workflow_result.personality_analysis.communication_style if workflow_result.personality_analysis else "Professional",
                        "decision_making_style": workflow_result.personality_analysis.decision_making_style if workflow_result.personality_analysis else "Unknown",
                        "motivational_drivers": workflow_result.personality_analysis.motivational_drivers if workflow_result.personality_analysis else [],
                        "strategy_recommendations": workflow_result.strategy_analysis.recommendations if workflow_result.strategy_analysis else []
                    }
                }
                
                st.session_state.conversation_history.append(new_entry)
                st.session_state.current_company_message = ""
                st.session_state.show_edit_mode = False
                
                st.success("🎉 Exchange completed! Check conversation history below.")
                st.rerun()
            else:
                st.error("❌ No workflow analysis available. Please reload customer data.")
                
        except Exception as e:
            st.error(f"❌ Error generating response: {str(e)}")
            import traceback
            st.error(f"Details: {traceback.format_exc()}")

def main():
    """Main application function"""
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Display sidebar and get configuration
    customer_json, message_type, channel, goal = display_sidebar()
    
    # Main content area
    display_dashboard_header()
    
    # Display metrics if customer is loaded
    if st.session_state.customer_info:
        display_metrics_row()
        st.markdown("---")
        
        # Show current conversation history if exists
        if hasattr(st.session_state, 'conversation_messages') and st.session_state.conversation_messages:
            st.subheader("� Current Conversation")
            
            for i, msg in enumerate(st.session_state.conversation_messages, 1):
                if msg['sender'] == "company":
                    st.markdown(f"**🏢 TALAN - Exchange {i}** ({msg.get('message_type', 'N/A')} - {msg.get('channel', 'N/A')})")
                    st.markdown(f"""
                    <div style="background: #e8f4f8; padding: 1rem; border-radius: 8px; border-left: 4px solid #4258dc; margin: 0.5rem 0;">
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"**👤 CLIENT - Exchange {i}** ({msg.get('message_type', 'N/A')})")
                    st.markdown(f"""
                    <div style="background: #f0f8f0; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 0.5rem 0;">
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Show next message generation section
        st.subheader("📝 Generate Next Message")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            message_type = st.selectbox(
                "� Message Type",
                ["opening", "follow_up", "qualification", "presentation", "objection_handling", "closing"],
                help="Choose the type of message to generate"
            )
        
        with col2:
            selected_channel = st.selectbox(
                "📡 Communication Channel", 
                ["EMAIL", "LINKEDIN", "PHONE", "MEETING"],
                help="Choose the communication channel for this message"
            )
        
        with col3:
            exchange_count = len(st.session_state.get('conversation_messages', [])) + 1
            st.metric("Next Exchange #", exchange_count)
        
        # Goal input
        selected_goal = st.text_input(
            "🎯 Message Goal",
            value="Présenter les solutions Talan et développer la relation client",
            help="Define the objective of this specific message"
        )
        
        # Enforce step-by-step message generation: only Talan message, then review/approve, then customer response
        if hasattr(st.session_state, 'pending_talan_message') and st.session_state.pending_talan_message:
            # Show message review interface (edit/approve/regenerate)
            display_message_review(message_type, selected_channel, selected_goal)
        else:
            # Show generate button for Talan message only
            col_center = st.columns([1, 2, 1])[1]
            with col_center:
                if st.button("🚀 Generate Next Message", type="primary", use_container_width=True):
                    generate_single_message(message_type, selected_channel, selected_goal)
        
        # Clear conversation button
        if hasattr(st.session_state, 'conversation_messages') and st.session_state.conversation_messages:
            col_clear = st.columns([3, 1])[1]
            with col_clear:
                if st.button("🗑️ Clear Conversation", use_container_width=True):
                    st.session_state.conversation_messages = []
                    if hasattr(st.session_state, 'conversation_result'):
                        delattr(st.session_state, 'conversation_result')
                    st.rerun()
        
        # Analysis buttons - show if we have conversation messages
        if hasattr(st.session_state, 'conversation_messages') and st.session_state.conversation_messages:
            st.markdown("---")
            st.subheader("📊 Conversation Analysis")
            st.write("Analyze the conversation exchange above:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🧠 Personality Analysis", key="personality_btn_main", use_container_width=True):
                    run_personality_analysis()
            
            with col2:
                if st.button("🎯 Strategy Analysis", key="strategy_btn_main", use_container_width=True):
                    run_strategy_analysis()
            
            with col3:
                if st.button("🗑️ Clear Analysis", key="clear_analysis_btn_main", use_container_width=True):
                    st.session_state.personality_analysis = None
                    st.session_state.strategy_analysis = None
                    st.success("🗑️ Analysis cleared!")
                    st.rerun()
            
            # Display stored analysis if available
            if hasattr(st.session_state, 'personality_analysis') and st.session_state.personality_analysis:
                with st.expander("🧠 Personality Analysis Results", expanded=True):
                    # Use the proper display function for full 5-profile classification
                    display_personality_analysis(st.session_state.personality_analysis)
            
            if hasattr(st.session_state, 'strategy_analysis') and st.session_state.strategy_analysis:
                with st.expander("🎯 Strategy Analysis Results", expanded=True):
                    # Use the proper display function for comprehensive strategy analysis
                    display_strategy_analysis(st.session_state.strategy_analysis)
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: white; border-radius: 12px; box-shadow: 0 2px 20px rgba(0,0,0,0.08);">
            <h3 style="color: var(--primary-blue);">🚀 Welcome to LeadX</h3>
            <p style="color: #666; font-size: 1.1rem;">Upload a customer JSON file to start generating intelligent B2B sales conversations</p>
        </div>
        """, unsafe_allow_html=True)

def run_personality_analysis():
    """Run personality analysis on the current conversation"""
    try:
        with st.spinner("🧠 Analyzing customer personality from conversation..."):
            from agents.personality_classifier_agent_pure import PersonalityClassifierAgentPure
            from utils.models import Message, Conversation, WorkflowState
            
            # Convert session messages to Message objects
            conversation_messages = []
            for msg_data in st.session_state.conversation_messages:
                conversation_messages.append(Message(
                    sender=msg_data['sender'],
                    content=msg_data['content'],
                    message_type=msg_data.get('message_type', 'unknown'),
                    timestamp=datetime.now()
                ))
            
            # Create conversation object
            conversation = Conversation(
                messages=conversation_messages,
                conversation_id=f"analysis_conv_{len(conversation_messages)}",
                goal="Analysis",
                participants={"company": "Talan Tunisie", "customer": st.session_state.customer_info['company_name']},
                status="completed"
            )
            
            # Create workflow state with conversation and customer analysis
            workflow_state = WorkflowState()
            workflow_state.conversation = conversation
            
            # Convert customer_info to proper CustomerAnalysis object
            from utils.models import CustomerAnalysis
            workflow_state.customer_analysis = CustomerAnalysis(
                customer_name=st.session_state.customer_info['company_name'],
                industry=st.session_state.customer_info['industry'],
                company_size=st.session_state.customer_info['company_size'],
                pain_points=st.session_state.customer_info.get('pain_points', []),
                needs=st.session_state.customer_info.get('business_needs', []),
                communication_style=st.session_state.customer_info.get('communication_style', 'professional'),
                decision_makers=st.session_state.customer_info.get('decision_makers', [])
            )
            
            # Run personality analysis using run_simple method
            personality_agent = PersonalityClassifierAgentPure()
            result_state = personality_agent.execute(workflow_state)
            
            if result_state.personality_analysis:
                st.session_state.personality_analysis = result_state.personality_analysis
                st.success("✅ Personality analysis completed!")
                st.rerun()
            else:
                st.error("❌ Failed to generate personality analysis")
                
    except Exception as e:
        st.error(f"❌ Personality analysis error: {str(e)}")

def run_strategy_analysis():
    """Run strategy analysis on the current conversation"""
    try:
        with st.spinner("🎯 Analyzing conversation strategy..."):
            from agents.strategy_agent_pure import StrategyAgentPure
            from utils.models import Message, Conversation, WorkflowState
            
            # Convert session messages to Message objects
            conversation_messages = []
            for msg_data in st.session_state.conversation_messages:
                conversation_messages.append(Message(
                    sender=msg_data['sender'],
                    content=msg_data['content'],
                    message_type=msg_data.get('message_type', 'unknown'),
                    timestamp=datetime.now()
                ))
            
            # Create conversation object
            conversation = Conversation(
                messages=conversation_messages,
                conversation_id=f"analysis_conv_{len(conversation_messages)}",
                goal="Analysis",
                participants={"company": "Talan Tunisie", "customer": st.session_state.customer_info['company_name']},
                status="completed"
            )
            
            # Create workflow state with conversation and customer analysis
            workflow_state = WorkflowState()
            workflow_state.conversation = conversation
            
            # Convert customer_info to proper CustomerAnalysis object
            from utils.models import CustomerAnalysis
            workflow_state.customer_analysis = CustomerAnalysis(
                customer_name=st.session_state.customer_info['company_name'],
                industry=st.session_state.customer_info['industry'],
                company_size=st.session_state.customer_info['company_size'],
                pain_points=st.session_state.customer_info.get('pain_points', []),
                needs=st.session_state.customer_info.get('business_needs', []),
                communication_style=st.session_state.customer_info.get('communication_style', 'professional'),
                decision_makers=st.session_state.customer_info.get('decision_makers', [])
            )
            
            # Run strategy analysis using run_simple method
            strategy_agent = StrategyAgentPure()
            result_state = strategy_agent.execute(workflow_state)
            
            if result_state.strategy_analysis:
                st.session_state.strategy_analysis = result_state.strategy_analysis
                st.success("✅ Strategy analysis completed!")
                st.rerun()
            else:
                st.error("❌ Failed to generate strategy analysis")
                
    except Exception as e:
        st.error(f"❌ Strategy analysis error: {str(e)}")