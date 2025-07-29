#!/usr/bin/env python3
"""
Quick setup script for Elo Dental Clinic MCOP System
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[*] {description}...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=True, 
                                  capture_output=True, text=True)
        print(f"[+] {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] {description} failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[-] Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"[+] Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def create_env_file():
    """Create .env file from example if it doesn't exist"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists() and env_example_path.exists():
        print("[*] Creating .env file from template...")
        env_path.write_text(env_example_path.read_text())
        print("[+] .env file created")
        print("[!] IMPORTANT: Please edit .env file with your actual API keys!")
        return True
    elif env_path.exists():
        print("[+] .env file already exists")
        return True
    else:
        print("[-] No .env.example found to create .env file")
        return False


def setup_virtual_environment():
    """Set up Python virtual environment"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("[+] Virtual environment already exists")
    
    # Activate and install dependencies
    if platform.system() == "Windows":
        pip_cmd = r"venv\Scripts\pip.exe"
        python_cmd = r"venv\Scripts\python.exe"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True


def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "LIVEKIT_URL", 
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "GOOGLE_API_KEY"
    ]
    
    missing_vars = []
    
    # Load .env file manually
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                if key.strip() in required_vars and value.strip() and not value.strip().startswith("your-"):
                    os.environ[key.strip()] = value.strip()
    
    for var in required_vars:
        value = os.environ.get(var, "")
        if not value or value.startswith("your-") or value.startswith("sk-your-"):
            missing_vars.append(var)
    
    if missing_vars:
        print("[!] Missing or placeholder environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n[!] Please update your .env file with actual values")
        return False
    else:
        print("[+] All required environment variables are set")
        return True


def main():
    """Main setup function"""
    print("Elo Dental Clinic MCOP System - Quick Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    print("\n[+] Setup Summary:")
    print("[+] Python version compatible")
    print("[+] Virtual environment ready")
    print("[+] Dependencies installed")
    print("[+] Configuration files created")
    
    if env_ok:
        print("[+] Environment variables configured")
        print("\n[+] Ready to run! Use:")
        if platform.system() == "Windows":
            print("   venv\\Scripts\\python.exe agent.py dev")
        else:
            print("   venv/bin/python agent.py dev")
    else:
        print("[!] Environment variables need configuration")
        print("\n[!] Next steps:")
        print("1. Edit .env file with your actual API keys")
        print("2. Run the application with:")
        if platform.system() == "Windows":
            print("   venv\\Scripts\\python.exe agent.py dev")
        else:
            print("   venv/bin/python agent.py dev")


if __name__ == "__main__":
    main()