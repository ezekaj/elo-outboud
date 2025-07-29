#!/usr/bin/env python3
"""
LM Studio setup guide for Elo Dental Clinic
"""
import requests
import time
import os
from pathlib import Path


def check_lm_studio_running():
    """Check if LM Studio is running and accessible"""
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_loaded_models():
    """Get list of currently loaded models in LM Studio"""
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            return [model["id"] for model in models.get("data", [])]
        return []
    except requests.RequestException:
        return []


def test_lm_studio_chat():
    """Test LM Studio chat functionality"""
    try:
        payload = {
            "model": "local-model",
            "messages": [
                {"role": "system", "content": "You are Elo, a charming dental assistant."},
                {"role": "user", "content": "Hello, can you help me schedule an appointment?"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(
            "http://localhost:1234/v1/chat/completions",
            json=payload,
            headers={"Authorization": "Bearer lm-studio"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
        return None
    except requests.RequestException as e:
        return f"Error: {e}"


def main():
    print("LM Studio Setup for Elo Dental Clinic")
    print("=" * 50)
    
    # Check if LM Studio is running
    print("[1/4] Checking LM Studio connection...")
    if check_lm_studio_running():
        print("[+] LM Studio is running at http://localhost:1234")
    else:
        print("[-] LM Studio is not running")
        print("\n[!] To set up LM Studio:")
        print("1. Download LM Studio from: https://lmstudio.ai/")
        print("2. Install and launch LM Studio")
        print("3. In LM Studio:")
        print("   - Go to 'Discover' tab")
        print("   - Download a model (recommended: Llama 3.2 3B Instruct)")
        print("   - Go to 'Local Server' tab")
        print("   - Load your downloaded model")
        print("   - Click 'Start Server'")
        print("4. Make sure server is running on port 1234")
        print("5. Run this script again")
        return
    
    # Check loaded models
    print("\n[2/4] Checking loaded models...")
    models = get_loaded_models()
    if models:
        print(f"[+] Loaded models: {', '.join(models)}")
    else:
        print("[-] No models loaded")
        print("[!] Please load a model in LM Studio's 'Local Server' tab")
        return
    
    # Test chat functionality
    print("\n[3/4] Testing chat functionality...")
    test_result = test_lm_studio_chat()
    if test_result and not test_result.startswith("Error:"):
        print("[+] Chat test successful!")
        print(f"    Response: {test_result[:100]}...")
    else:
        print(f"[-] Chat test failed: {test_result}")
        return
    
    # Check environment configuration
    print("\n[4/4] Checking environment configuration...")
    env_path = Path(".env")
    if env_path.exists():
        env_content = env_path.read_text()
        if "LM_STUDIO_BASE_URL=http://localhost:1234/v1" in env_content:
            print("[+] LM Studio configuration found in .env")
        else:
            print("[-] LM Studio configuration missing in .env")
    else:
        print("[-] .env file not found")
    
    print("\n[+] LM Studio Setup Complete!")
    print("\n[!] Next steps:")
    print("1. Run your Elo agent: python agent.py console")
    print("2. Test voice mode: python agent.py dev")
    print("3. The agent will now use your local LM Studio model!")
    
    print("\n[!] Recommended Models for Dental Assistant:")
    print("- Llama 3.2 3B Instruct (fast, good for conversations)")
    print("- Phi-3 Medium (balanced performance)")
    print("- Mistral 7B Instruct (high quality responses)")
    
    print("\n[!] Your current configuration:")
    print(f"- LM Studio URL: http://localhost:1234/v1")
    print(f"- API Key: lm-studio")
    print(f"- Loaded models: {', '.join(models) if models else 'None'}")


if __name__ == "__main__":
    main()