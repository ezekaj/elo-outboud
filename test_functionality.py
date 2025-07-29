#!/usr/bin/env python3
"""
Test core functionality of Elo Voice Assistant
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_weather_tool():
    """Test the weather tool functionality"""
    print("🌤️  Testing Weather Tool...")
    
    try:
        from tools import get_weather
        from livekit.agents import RunContext
        
        # Create a mock context
        class MockContext:
            pass
        
        context = MockContext()
        
        # Test weather for a known city
        result = await get_weather(context, "London")
        
        if result and "London" in result:
            print(f"✅ Weather tool working: {result}")
            return True
        else:
            print(f"⚠️  Weather tool returned: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Weather tool failed: {e}")
        return False

async def test_search_tool():
    """Test the web search tool functionality"""
    print("🔍 Testing Web Search Tool...")
    
    try:
        from tools import search_web
        from livekit.agents import RunContext
        
        # Create a mock context
        class MockContext:
            pass
        
        context = MockContext()
        
        # Test search with a simple query
        result = await search_web(context, "Python programming")
        
        if result and len(result) > 50:  # Should return substantial content
            print(f"✅ Search tool working: {result[:100]}...")
            return True
        else:
            print(f"⚠️  Search tool returned: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Search tool failed: {e}")
        return False

def test_prompts():
    """Test prompts configuration"""
    print("💬 Testing Prompts Configuration...")
    
    try:
        import prompts
        
        # Check if required prompts exist
        if hasattr(prompts, 'AGENT_INSTRUCTION') and hasattr(prompts, 'SESSION_INSTRUCTION'):
            agent_instruction = prompts.AGENT_INSTRUCTION
            session_instruction = prompts.SESSION_INSTRUCTION
            
            # Check if prompts contain expected content
            if "butler" in agent_instruction.lower() and "conversational" in agent_instruction.lower():
                print("✅ Agent instruction properly configured")
            else:
                print("⚠️  Agent instruction may need review")
            
            if "assistant" in session_instruction.lower():
                print("✅ Session instruction properly configured")
            else:
                print("⚠️  Session instruction may need review")
            
            return True
        else:
            print("❌ Required prompt variables not found")
            return False
            
    except Exception as e:
        print(f"❌ Prompts test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("🔧 Testing Environment Configuration...")
    
    load_dotenv()
    
    required_vars = [
        'LIVEKIT_URL',
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET',
        'GOOGLE_API_KEY'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value and not value.startswith('your_'):
            print(f"✅ {var}: Configured")
        else:
            print(f"❌ {var}: Not configured or placeholder")
            all_good = False
    
    return all_good

def test_imports():
    """Test critical imports"""
    print("📦 Testing Critical Imports...")
    
    imports_to_test = [
        ('livekit.agents', 'LiveKit Agents'),
        ('livekit.plugins.google', 'Google Plugin'),
        ('google.genai', 'Google GenAI'),
        ('requests', 'Requests'),
        ('duckduckgo_search', 'DuckDuckGo Search')
    ]
    
    all_good = True
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {name}: Import successful")
        except ImportError as e:
            print(f"❌ {name}: Import failed - {e}")
            all_good = False
    
    return all_good

async def main():
    """Run all functionality tests"""
    print("🎙️ Elo Voice Assistant - Functionality Test")
    print("=" * 50)
    
    # Run synchronous tests first
    sync_tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Prompts", test_prompts)
    ]
    
    sync_results = []
    for name, test_func in sync_tests:
        print(f"\n[TEST] {name}")
        print("-" * 30)
        try:
            result = test_func()
            sync_results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            sync_results.append((name, False))
    
    # Run async tests
    async_tests = [
        ("Weather Tool", test_weather_tool),
        ("Search Tool", test_search_tool)
    ]
    
    async_results = []
    for name, test_func in async_tests:
        print(f"\n[TEST] {name}")
        print("-" * 30)
        try:
            result = await test_func()
            async_results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            async_results.append((name, False))
    
    # Summary
    all_results = sync_results + async_results
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    
    print(f"\n📊 Test Summary")
    print("=" * 50)
    
    for name, result in all_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All functionality tests passed!")
        print("Your Elo agent is ready for voice interactions.")
    elif passed >= total * 0.8:  # 80% pass rate
        print("✅ Most tests passed - agent should work correctly.")
        print("Minor issues detected but core functionality is working.")
    else:
        print("⚠️  Several issues detected - may need attention.")
    
    print(f"\n🚀 Next Steps:")
    print("1. Start agent: python agent.py dev")
    print("2. Check debug interface: http://localhost:PORT/debug")
    print("3. Test voice interactions via LiveKit client")

if __name__ == "__main__":
    asyncio.run(main())
