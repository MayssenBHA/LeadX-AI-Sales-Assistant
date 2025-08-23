# LeadX-AI-Sales-Assistant

*An intelligent, multi-agent B2B sales platform powered by LangGraph and advanced language models*

> **Note**: This project is integrated as a feature of LeadX – AI-Powered Sales Intelligence Platform.

## 🌟 Overview

An AI-powered B2B sales assistant that transforms how sales teams engage with prospects. Built on a **pure LangGraph multi-agent architecture**, it analyzes customer profiles, generates personalized sales conversations, and provides strategic insights through an intuitive Streamlit interface.

## 🎥 Video Demo

Watch the B2B AI Sales Assistant in action:

👉 [Click here to watch the demo](https://drive.google.com/file/d/1XCULUAZbuw-JpYPYSF90a2d3E63cjTC_/view?usp=sharing)

### 🎯 Key Capabilities
- **🧠 Intelligent Customer Analysis**: Extracts insights from customer profiles and documents
- **💬 Dynamic Message Generation**: Creates tailored sales messages based on customer context
- **📊 Strategy Assessment**: Evaluates conversation effectiveness with scoring and recommendations  
- **🎭 Personality Profiling**: Analyzes communication styles using advanced psychological frameworks
- **🌐 Interactive Dashboard**: Modern, responsive UI for seamless workflow management

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Pure LangGraph Architecture** | 100% LangGraph-based multi-agent system with state management |
| 🔄 **Workflow Orchestration** | Advanced state persistence and checkpointing capabilities |
| 🎯 **Multi-Agent Coordination** | Specialized agents for analysis, generation, and insights |
| 🌐 **Modern Web Interface** | Streamlit-powered dashboard with real-time visualization |
| 🏢 **Enterprise Ready** | Pre-configured for business use with customizable profiles |
| 📊 **Comprehensive Analytics** | Deep customer profiling and conversation analysis |
| 🛠️ **Modular Design** | Easily extensible architecture for new agents and features |

## 🏗️ Architecture

### Multi-Agent Workflow Pipeline
```
Customer Profile → Document Analysis Agent → Message Composer Agent → [Strategy Agent + Personality Agent] → Insights Dashboard
```

### High-Level Architecture Diagram

```
+-------------------+      +---------------------+      +---------------------+      +---------------------+      +-------------------+
|                   |      |                     |      |                     |      |                     |      |                   |
|  Customer JSON    +----->+ Document Analysis   +----->+ Message Generation  +----->+  [Strategy/         +----->+   Results &       |
|   Upload          |      |   Agent             |      |   Agent             |      |   Personality]      |      |   Insights        |
|                   |      |                     |      |                     |      |   Analysis Agents   |      |                   |
+-------------------+      +---------------------+      +---------------------+      +---------------------+      +-------------------+
```

### Core Agents
1. **📄 Document Analysis Agent**: Extracts structured insights from customer data
2. **💬 Message Composer Agent**: Generates context-aware sales messages
3. **🎯 Strategy Agent**: Analyzes conversation effectiveness and provides recommendations
4. **🎭 Personality Classifier Agent**: Profiles customer communication patterns using DISC methodology

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Groq API key (for LLM access)

### Installation

#### Option 1: Automated Setup
```bash
git clone https://github.com/yourusername/leadx-b2b-ai-sales-assistant.git
cd leadx-b2b-ai-sales-assistant
python setup.py
```

#### Option 2: Manual Setup
```bash
# Clone repository
git clone https://github.com/yourusername/leadx-b2b-ai-sales-assistant.git
cd leadx-b2b-ai-sales-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama3-70b-8192
TEMPERATURE=0.7
```

### Launch Application
```bash
streamlit run enhanced_app_styled.py
```
Navigate to [http://localhost:8501](http://localhost:8501)

## 🎮 Usage Guide

### Step-by-Step Workflow
1. **📁 Upload Customer Profile**: Start by uploading a JSON customer profile in the sidebar
2. **⚙️ Configure Message Settings**: Select message type, channel, and business objective
3. **🔮 Generate AI Message**: Let the system create a tailored sales message
4. **✏️ Review & Refine**: Edit the generated message or regenerate as needed
5. **📨 Simulate Response**: Get an AI-generated customer response for practice
6. **📊 Analyze Results**: Review strategy effectiveness and personality insights

### Sample Customer Profile Format
```json
{
  "company_name": "TechCorp Solutions",
  "industry": "Software Development",
  "company_size": "50-200 employees",
  "pain_points": [
    {
      "issue": "Manual processes",
      "description": "Time-consuming manual workflows affecting productivity"
    }
  ],
  "business_needs": [
    {
      "requirement": "Automation tools",
      "description": "Need to streamline repetitive tasks"
    }
  ],
  "decision_makers": ["CTO", "Operations Manager"],
  "communication_style": "direct and data-driven"
}
```

## 📁 Project Structure

```
leadx-b2b-ai-sales-assistant/
│
├── 📱 enhanced_app_styled.py      # Streamlit web interface
├── 🔄 pure_langgraph_workflow.py # Main workflow orchestrator
├── ⚙️ setup.py                   # Automated setup script
├── 📋 requirements.txt           # Python dependencies
│
├── 🤖 agents/                    # AI Agent Modules
│   ├── base_agent.py             # Abstract base class
│   ├── document_analysis_agent.py
│   ├── message_composer_agent_pure.py
│   ├── strategy_agent_pure.py
│   └── personality_classifier_agent_pure.py
│
├── ⚙️ config/                    # Configuration Management
│   ├── settings.py               # Application settings
│   ├── prompts.py               # AI prompts and templates
│   └── talan_config.py          # Company-specific config
│
├── 🛠️ utils/                     # Helper Utilities
│   ├── models.py                # Pydantic data models
│   └── helpers.py               # File processing utilities
│
├── 📊 data/                     # Sample Data & Outputs
│   ├── test_customer.json       # Sample customer profiles
│   └── outputs/                 # Generated results
│
└── 🧪 tests/                    # Unit Tests
    ├── test_agents.py
    └── test_workflow.py
```

## 🔧 Technical Details

### Technology Stack
- **🐍 Python 3.10+**: Core programming language
- **🕷️ LangGraph**: Multi-agent workflow orchestration
- **🤖 Groq API**: High-performance LLM inference
- **🌐 Streamlit**: Interactive web interface
- **📊 Pydantic**: Data validation and modeling
- **📝 OpenAI API**: Alternative LLM support

### Key Dependencies
```python
# Core AI/ML
langgraph==0.2.50
langchain==0.3.7
langchain-groq==0.2.1
pydantic==2.9.2

# Web Interface
streamlit==1.39.0
plotly==5.24.1

# Data Processing
pandas==2.2.3
pdfplumber==0.11.4
```

## 🧠 AI Agent Details

### Document Analysis Agent
- **Purpose**: Extracts structured insights from customer profiles
- **Capabilities**: Entity recognition, pain point identification, needs analysis
- **Output**: Structured customer analysis with decision maker mapping

### Message Composer Agent
- **Purpose**: Generates personalized B2B sales messages
- **Capabilities**: Context-aware content generation, tone adaptation
- **Output**: Tailored messages with company-specific positioning

### Strategy Agent  
- **Purpose**: Evaluates conversation effectiveness
- **Capabilities**: Scoring methodology, competitive positioning analysis
- **Output**: Strategic recommendations with improvement suggestions

### Personality Classifier Agent
- **Purpose**: Profiles customer communication styles
- **Capabilities**: DISC personality analysis, communication preference mapping
- **Output**: Personality insights with optimal engagement strategies

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make changes and test**
4. **Submit a pull request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black . --line-length 100
```
---
