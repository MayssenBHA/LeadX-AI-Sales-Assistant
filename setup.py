#!/usr/bin/env python3
"""
Setup script for B2B Sales Conversation Generator
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10 or higher"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("🔧 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def get_activation_command():
    """Get the activation command for the current OS"""
    if os.name == 'nt':  # Windows
        return "venv\\Scripts\\activate"
    else:  # Unix-like (Linux, macOS)
        return "source venv/bin/activate"

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine pip executable
    if os.name == 'nt':  # Windows
        pip_executable = "venv\\Scripts\\pip"
    else:  # Unix-like
        pip_executable = "venv/bin/pip"
    
    try:
        # Upgrade pip first
        subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating project directories...")
    
    directories = [
        "data/outputs",
        "data/outputs/conversations", 
        "data/outputs/analyses",
        "data/temp",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Project directories created")

def setup_environment_file():
    """Setup environment file"""
    print("⚙️ Setting up environment configuration...")
    
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("✅ Environment file created from template")
        print("📝 Please edit .env file and add your Groq API key")
    else:
        print("✅ Environment file already exists")

def run_tests():
    """Run basic tests to verify setup"""
    print("🧪 Running basic tests...")
    
    # Determine python executable
    if os.name == 'nt':  # Windows
        python_executable = "venv\\Scripts\\python"
    else:  # Unix-like
        python_executable = "venv/bin/python"
    
    try:
        # Test imports
        import_test = f"""
import sys
sys.path.append('.')
try:
    from config.settings import Config
    from utils.models import WorkflowState
    from agents.document_analysis_agent import DocumentAnalysisAgent
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {{e}}")
    sys.exit(1)
"""
        
        result = subprocess.run([python_executable, "-c", import_test], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Import tests passed")
            return True
        else:
            print(f"❌ Import tests failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 B2B Sales Conversation Generator Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment
    if not os.path.exists("venv"):
        if not create_virtual_environment():
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create directories
    create_directories()
    
    # Setup environment file
    setup_environment_file()
    
    # Run basic tests
    if not run_tests():
        print("⚠️ Some tests failed, but setup may still be functional")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print(f"1. Activate virtual environment: {get_activation_command()}")
    print("2. Edit .env file and add your Groq API key")
    print("3. Run tests: python tests/test_agents.py")
    print("4. Start application: streamlit run app.py")
    print("\n✨ Enjoy your B2B Sales Conversation Generator!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
