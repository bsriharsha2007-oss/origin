"""
SwarmForge Quick Start Script
Verification and setup helper
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Verify Python 3.10+"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} found")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor} found (need 3.10+)")
        return False


def check_venv():
    """Check if we're in a virtual environment"""
    print("\n🔍 Checking virtual environment...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"   ✓ Virtual environment active: {sys.prefix}")
        return True
    else:
        print("   ⚠️  No virtual environment detected")
        print("   Run: python -m venv venv")
        print("   Then: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")
    required = [
        "langchain",
        "langgraph",
        "langchain_openai",
        "dotenv"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True


def check_env_file():
    """Check if .env file exists and has API key"""
    print("\n🔍 Checking environment configuration...")
    
    if os.path.exists(".env"):
        print("   ✓ .env file found")
        
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" in content or "GROQ_API_KEY" in content:
                print("   ✓ API key found in .env")
                return True
            else:
                print("   ⚠️  No OPENAI_API_KEY or GROQ_API_KEY in .env")
                return False
    else:
        print("   ⚠️  .env file not found")
        print("   Run: cp .env.example .env")
        print("   Then edit .env with your API keys")
        return False


def check_project_files():
    """Verify all project files exist"""
    print("\n🔍 Checking project files...")
    
    required_files = [
        "agents.py",
        "graph.py",
        "tools.py",
        "main.py",
        "requirements.txt",
        ".env.example",
        "README.md"
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file}")
            missing.append(file)
    
    return len(missing) == 0


def test_imports():
    """Test that core modules can be imported"""
    print("\n🔍 Testing core imports...")
    
    try:
        from agents import Agent, AgentPool, SwarmOrchestrator
        print("   ✓ agents module")
    except Exception as e:
        print(f"   ✗ agents module: {e}")
        return False
    
    try:
        from graph import SwarmGraph, MemoryManager, EvaluationEngine
        print("   ✓ graph module")
    except Exception as e:
        print(f"   ✗ graph module: {e}")
        return False
    
    try:
        from tools import get_tools, web_search
        print("   ✓ tools module")
    except Exception as e:
        print(f"   ✗ tools module: {e}")
        return False
    
    return True


def show_quick_start():
    """Show quick start commands"""
    print("\n" + "="*60)
    print("🚀 QUICK START COMMANDS")
    print("="*60)
    print("\n1. Run the interactive demo:")
    print("   python main.py")
    
    print("\n2. Run tests:")
    print("   pytest tests.py -v")
    
    print("\n3. View build guide:")
    print("   cat BUILD_GUIDE.md")
    print("   # or open in your editor")
    
    print("\n4. Create your first swarm:")
    print("   python")
    print("   >>> from main import get_llm")
    print("   >>> from agents import AgentPool, AgentConfig, AgentRole")
    print("   >>> llm = get_llm()")
    print("   >>> pool = AgentPool(llm)")
    print("   >>> pool.add_agent(AgentConfig('researcher', AgentRole.RESEARCHER))")


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("🐝 SwarmForge Setup Verification")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Virtual Environment", check_venv()),
        ("Dependencies", check_dependencies()),
        ("Project Files", check_project_files()),
        ("Environment Config", check_env_file()),
        ("Core Imports", test_imports()),
    ]
    
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    passed = 0
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("\n✅ All systems ready! SwarmForge is ready to run.")
        show_quick_start()
    elif passed >= len(checks) - 1:
        print("\n⚠️  Almost ready! Address the issues above and run again.")
        show_quick_start()
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. pip install -r requirements.txt")
        print("2. cp .env.example .env && edit .env")
        print("3. source venv/bin/activate (Mac/Linux) or venv\\Scripts\\activate (Windows)")


if __name__ == "__main__":
    main()
