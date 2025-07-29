#!/usr/bin/env python3
"""
Quick diagnostic check for Elo Voice Assistant
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check environment configuration"""
    print("🔍 Environment Check")
    print("-" * 40)
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file found")
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'LIVEKIT_URL': 'LiveKit URL',
        'LIVEKIT_API_KEY': 'LiveKit API Key', 
        'LIVEKIT_API_SECRET': 'LiveKit API Secret',
        'GOOGLE_API_KEY': 'Google API Key'
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"❌ {description}: Not configured")
            all_good = False
        else:
            print(f"✅ {description}: Configured")
    
    return all_good

def check_imports():
    """Check if all required modules can be imported"""
    print("\n🔍 Import Check")
    print("-" * 40)
    
    modules = [
        ('livekit', 'LiveKit'),
        ('livekit.agents', 'LiveKit Agents'),
        ('livekit.plugins.google', 'Google Plugin'),
        ('google.genai', 'Google GenAI'),
        ('requests', 'Requests'),
        ('duckduckgo_search', 'DuckDuckGo Search'),
        ('prompts', 'Prompts Module'),
        ('tools', 'Tools Module')
    ]
    
    all_good = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except ImportError as e:
            print(f"❌ {name}: Failed - {e}")
            all_good = False
    
    return all_good

def check_files():
    """Check if all required files exist"""
    print("\n🔍 File Check")
    print("-" * 40)
    
    required_files = [
        'agent.py',
        'prompts.py',
        'tools.py',
        'requirements.txt',
        '.env'
    ]
    
    all_good = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}: Found")
        else:
            print(f"❌ {file}: Missing")
            all_good = False
    
    return all_good

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🔍 Functionality Check")
    print("-" * 40)
    
    try:
        # Test prompts
        import prompts
        if hasattr(prompts, 'AGENT_INSTRUCTION') and hasattr(prompts, 'SESSION_INSTRUCTION'):
            print("✅ Prompts: Configuration loaded")
        else:
            print("❌ Prompts: Missing required variables")
            return False
        
        # Test tools
        import tools
        if hasattr(tools, 'get_weather') and hasattr(tools, 'search_web'):
            print("✅ Tools: Functions available")
        else:
            print("❌ Tools: Missing required functions")
            return False
        
        print("✅ Basic functionality: OK")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def analyze_agent_status():
    """Analyze current agent status"""
    print("\n🔍 Agent Status Analysis")
    print("-" * 40)
    
    # Check if agent process might be running
    try:
        import psutil
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('agent.py' in arg for arg in cmdline):
                        python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if python_processes:
            print(f"✅ Found {len(python_processes)} agent process(es) running")
            for proc in python_processes:
                print(f"   PID: {proc['pid']}")
        else:
            print("ℹ️  No agent processes detected")
            
    except ImportError:
        print("ℹ️  psutil not available - cannot check running processes")
    
    # Check for common port usage
    try:
        import socket
        ports_to_check = [53859, 53905, 53927, 54155]  # Common debug ports
        active_ports = []
        
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                active_ports.append(port)
            sock.close()
        
        if active_ports:
            print(f"✅ Active debug ports: {active_ports}")
            print(f"   Debug interface likely at: http://localhost:{active_ports[0]}/debug")
        else:
            print("ℹ️  No active debug ports detected")
            
    except Exception as e:
        print(f"ℹ️  Port check failed: {e}")

def provide_recommendations():
    """Provide recommendations based on findings"""
    print("\n💡 Recommendations")
    print("-" * 40)
    
    print("🚀 To start the agent:")
    print("   python agent.py dev")
    print()
    print("🔧 If you see errors:")
    print("   1. Check that all environment variables are set in .env")
    print("   2. Ensure virtual environment is activated")
    print("   3. Verify internet connectivity")
    print("   4. Check API credentials are valid")
    print()
    print("📊 To monitor the agent:")
    print("   - Watch console output for connection status")
    print("   - Access debug interface at http://localhost:PORT/debug")
    print("   - Look for 'registered worker' message for successful startup")
    print()
    print("⚠️  Normal development mode behaviors (not errors):")
    print("   - DuplexClosed errors during file reloads")
    print("   - Multiple worker IDs on restarts")
    print("   - Auto-restart messages when files change")

def main():
    """Run comprehensive check"""
    print("🎙️ Elo Voice Assistant - Quick Diagnostic Check")
    print("=" * 60)
    
    checks = [
        ("Files", check_files),
        ("Environment", check_environment),
        ("Imports", check_imports),
        ("Functionality", test_basic_functionality)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results.append((name, False))
    
    # Analyze agent status
    analyze_agent_status()
    
    # Summary
    print("\n📋 Summary")
    print("-" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All checks passed ({passed}/{total})!")
        print("Your Elo agent should work correctly.")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("Some issues may need attention.")
    
    provide_recommendations()

if __name__ == "__main__":
    main()
