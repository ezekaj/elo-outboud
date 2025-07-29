#!/usr/bin/env python3
"""
Elo Voice Assistant - Setup Script
Automates the initial setup process for the voice assistant.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step_num, total_steps, description):
    """Print current step"""
    print(f"\n[{step_num}/{total_steps}] {description}")

def run_command(command, description="", check=True):
    """Run a shell command with error handling"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        print("Please upgrade Python and try again.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected (Compatible)")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("elvi_env")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("Creating virtual environment...")
        venv.create("elvi_env", with_pip=True)
        print("✅ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = "elvi_env\\Scripts\\pip.exe"
    else:  # macOS/Linux
        pip_path = "elvi_env/bin/pip"
    
    print("Installing dependencies...")
    success = run_command(f"{pip_path} install -r requirements.txt")
    
    if success:
        print("✅ Dependencies installed successfully")
    else:
        print("❌ Failed to install dependencies")
    
    return success

def create_env_template():
    """Create .env template file"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    env_template = """# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here

# Google Configuration  
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Email functionality (if implementing)
# GMAIL_APP_PASSWORD=your_app_password
# GMAIL_USER=your_email@gmail.com
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_template)
        print("✅ .env template created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_gitignore():
    """Create .gitignore file to protect sensitive data"""
    gitignore_file = Path(".gitignore")
    
    gitignore_content = """# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
elvi_env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
"""
    
    if gitignore_file.exists():
        print("✅ .gitignore already exists")
        return True
    
    try:
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        print("✅ .gitignore created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .gitignore: {e}")
        return False

def verify_setup():
    """Verify the setup is working"""
    print("Verifying setup...")
    
    # Check if we can import the main modules
    if os.name == 'nt':  # Windows
        python_path = "elvi_env\\Scripts\\python.exe"
    else:  # macOS/Linux
        python_path = "elvi_env/bin/python"
    
    test_commands = [
        f"{python_path} -c \"import livekit; print('✅ LiveKit imported successfully')\"",
        f"{python_path} -c \"import google.genai; print('✅ Google GenAI imported successfully')\"",
        f"{python_path} -c \"import prompts; print('✅ Prompts module imported successfully')\"",
        f"{python_path} -c \"import tools; print('✅ Tools module imported successfully')\""
    ]
    
    all_passed = True
    for cmd in test_commands:
        if not run_command(cmd, check=False):
            all_passed = False
    
    return all_passed

def print_next_steps():
    """Print instructions for next steps"""
    print_header("Setup Complete! Next Steps")
    
    print("🎯 Configuration Required:")
    print("   1. Get LiveKit credentials:")
    print("      - Go to https://cloud.livekit.io/")
    print("      - Create a project")
    print("      - Copy URL, API Key, and API Secret")
    print()
    print("   2. Get Google API key:")
    print("      - Go to https://console.cloud.google.com/")
    print("      - Enable Generative AI API")
    print("      - Create an API key")
    print()
    print("   3. Update .env file with your credentials")
    print()
    print("🚀 Running the Agent:")
    print("   1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("      .\\elvi_env\\Scripts\\activate")
    else:  # macOS/Linux
        print("      source elvi_env/bin/activate")
    print()
    print("   2. Run the agent:")
    print("      python agent.py dev")
    print()
    print("🔧 Troubleshooting:")
    print("   - Run diagnostic: python troubleshoot.py")
    print("   - Check development.md for detailed guide")
    print("   - Debug interface: http://localhost:PORT/debug")

def main():
    """Main setup function"""
    print("🎙️ Elo Voice Assistant - Setup Script")
    print("This script will set up your development environment.")
    
    total_steps = 6
    current_step = 0
    
    # Step 1: Check Python version
    current_step += 1
    print_step(current_step, total_steps, "Checking Python version")
    if not check_python_version():
        return False
    
    # Step 2: Create virtual environment
    current_step += 1
    print_step(current_step, total_steps, "Creating virtual environment")
    if not create_virtual_environment():
        return False
    
    # Step 3: Install dependencies
    current_step += 1
    print_step(current_step, total_steps, "Installing dependencies")
    if not install_dependencies():
        return False
    
    # Step 4: Create .env template
    current_step += 1
    print_step(current_step, total_steps, "Creating configuration files")
    if not create_env_template():
        return False
    
    # Step 5: Create .gitignore
    current_step += 1
    print_step(current_step, total_steps, "Creating .gitignore")
    create_gitignore()  # Non-critical
    
    # Step 6: Verify setup
    current_step += 1
    print_step(current_step, total_steps, "Verifying setup")
    if not verify_setup():
        print("⚠️ Setup completed with some issues. Run troubleshoot.py for diagnosis.")
    else:
        print("✅ Setup completed successfully!")
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
