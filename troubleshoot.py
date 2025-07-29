#!/usr/bin/env python3
"""
Elo Voice Assistant - Troubleshooting Script
Automatically diagnoses common issues and provides solutions.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_status(check, status, message=""):
    """Print status with colored output"""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {check}: {message}")
    return status

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Python Version Check")
    version = sys.version_info
    compatible = version.major == 3 and version.minor >= 8
    
    print_status(
        "Python Version", 
        compatible,
        f"Python {version.major}.{version.minor}.{version.micro} {'(Compatible)' if compatible else '(Requires 3.8+)'}"
    )
    
    if not compatible:
        print("❗ Please upgrade to Python 3.8 or higher")
    
    return compatible

def check_virtual_environment():
    """Check if virtual environment is active"""
    print_header("Virtual Environment Check")
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    print_status("Virtual Environment", in_venv, "Active" if in_venv else "Not active")
    
    if not in_venv:
        print("❗ Activate virtual environment:")
        print("   Windows: .\\elvi_env\\Scripts\\activate")
        print("   macOS/Linux: source elvi_env/bin/activate")
    
    return in_venv

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Dependencies Check")
    
    required_packages = [
        'livekit-agents',
        'livekit-plugins-google',
        'livekit-plugins-noise-cancellation',
        'duckduckgo-search',
        'langchain-community',
        'requests',
        'python-dotenv'
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_status(f"Package: {package}", True, "Installed")
        except ImportError:
            print_status(f"Package: {package}", False, "Missing")
            all_installed = False
    
    if not all_installed:
        print("❗ Install missing packages:")
        print("   pip install -r requirements.txt")
    
    return all_installed

def check_environment_file():
    """Check if .env file exists and has required variables"""
    print_header("Environment Configuration Check")
    
    env_file = Path('.env')
    if not env_file.exists():
        print_status(".env file", False, "File not found")
        print("❗ Create .env file with required variables")
        return False
    
    print_status(".env file", True, "Found")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = [
        'LIVEKIT_URL',
        'LIVEKIT_API_KEY', 
        'LIVEKIT_API_SECRET',
        'GOOGLE_API_KEY'
    ]
    
    all_vars_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        has_value = value and value.strip() and not value.startswith('your_')
        print_status(f"Variable: {var}", has_value, "Set" if has_value else "Missing or placeholder")
        if not has_value:
            all_vars_present = False
    
    return all_vars_present

def check_livekit_connection():
    """Test LiveKit server connectivity"""
    print_header("LiveKit Connection Check")
    
    livekit_url = os.getenv('LIVEKIT_URL')
    if not livekit_url:
        print_status("LiveKit URL", False, "Not configured")
        return False
    
    # Convert WebSocket URL to HTTP for testing
    http_url = livekit_url.replace('wss://', 'https://').replace('ws://', 'http://')
    
    try:
        response = requests.get(f"{http_url}/", timeout=10)
        connected = response.status_code in [200, 404]  # 404 is normal for root path
        print_status("LiveKit Server", connected, f"Reachable ({response.status_code})")
        return connected
    except requests.exceptions.RequestException as e:
        print_status("LiveKit Server", False, f"Connection failed: {str(e)}")
        return False

def check_google_api():
    """Test Google API connectivity"""
    print_header("Google API Check")

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print_status("Google API Key", False, "Not configured")
        return False

    if api_key.startswith('your_') or len(api_key) < 30:
        print_status("Google API Key", False, "Placeholder value detected")
        return False

    print_status("Google API Key", True, f"Configured (length: {len(api_key)})")

    # Test basic connectivity to Google services
    try:
        response = requests.get("https://www.googleapis.com/", timeout=5)
        connected = response.status_code in [200, 404]
        print_status("Google Services", connected, "Reachable" if connected else "Unreachable")
        return True  # Return True if key is configured, even if we can't test the specific API
    except requests.exceptions.RequestException as e:
        print_status("Google Services", False, f"Connection failed: {str(e)}")
        return False

def check_file_structure():
    """Check if all required files are present"""
    print_header("File Structure Check")
    
    required_files = [
        'agent.py',
        'prompts.py', 
        'tools.py',
        'requirements.txt',
        '.env'
    ]
    
    all_files_present = True
    
    for file in required_files:
        exists = Path(file).exists()
        print_status(f"File: {file}", exists, "Found" if exists else "Missing")
        if not exists:
            all_files_present = False
    
    return all_files_present

def run_basic_import_test():
    """Test basic imports to catch syntax errors"""
    print_header("Import Test")
    
    modules_to_test = [
        ('prompts', 'prompts.py'),
        ('tools', 'tools.py'),
        ('agent', 'agent.py')
    ]
    
    all_imports_ok = True
    
    for module_name, file_name in modules_to_test:
        try:
            __import__(module_name)
            print_status(f"Import: {file_name}", True, "OK")
        except Exception as e:
            print_status(f"Import: {file_name}", False, f"Error: {str(e)}")
            all_imports_ok = False
    
    return all_imports_ok

def provide_solutions():
    """Provide common solutions for issues"""
    print_header("Common Solutions")
    
    print("🔧 Quick Fixes:")
    print("   1. Restart agent: Ctrl+C then 'python agent.py dev'")
    print("   2. Clear cache: Delete __pycache__ folders")
    print("   3. Reinstall dependencies: pip install -r requirements.txt --force-reinstall")
    print("   4. Check credentials: Verify all API keys in .env file")
    
    print("\n🌐 Network Issues:")
    print("   1. Check internet connection")
    print("   2. Verify firewall settings")
    print("   3. Try different network (mobile hotspot)")
    
    print("\n🔑 API Issues:")
    print("   1. Regenerate API keys")
    print("   2. Check API quotas and billing")
    print("   3. Verify API permissions")
    
    print("\n📚 Resources:")
    print("   - LiveKit Docs: https://docs.livekit.io/")
    print("   - Google AI Docs: https://ai.google.dev/")
    print("   - Development Guide: See development.md")

def main():
    """Run all diagnostic checks"""
    print("🔍 Elo Voice Assistant - Diagnostic Tool")
    print("This script will check for common issues and provide solutions.")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Environment Config", check_environment_file),
        ("Import Test", run_basic_import_test),
        ("LiveKit Connection", check_livekit_connection),
        ("Google API", check_google_api),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_status(check_name, False, f"Check failed: {str(e)}")
            results.append((check_name, False))
    
    # Summary
    print_header("Diagnostic Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} checks")
    
    if passed == total:
        print("🎉 All checks passed! Your Elo agent should work correctly.")
        print("   Run: python agent.py dev")
    else:
        print("❌ Some issues found. See solutions below.")
        provide_solutions()

if __name__ == "__main__":
    main()
