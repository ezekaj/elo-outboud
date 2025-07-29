#!/usr/bin/env python3
"""
Enhanced setup script for Elo Dental Clinic system
"""
import os
import sys
import subprocess
import asyncio
from pathlib import Path
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedSetup:
    """Enhanced setup for Elo Dental Clinic system"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.venv_dir = self.base_dir / "venv"
        self.db_path = self.base_dir / "clinic.db"
        
    def check_python_version(self):
        """Check Python version compatibility"""
        if sys.version_info < (3, 8):
            logger.error("Python 3.8 or higher is required")
            sys.exit(1)
        logger.info(f"Python {sys.version} detected")
    
    def create_virtual_environment(self):
        """Create virtual environment"""
        if self.venv_dir.exists():
            logger.info("Virtual environment already exists")
            return
        
        logger.info("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)
        
    def install_dependencies(self):
        """Install required dependencies"""
        logger.info("Installing dependencies...")
        
        pip_path = self.venv_dir / ("Scripts" if os.name == 'nt' else "bin") / "pip"
        
        # Install enhanced requirements
        enhanced_requirements = [
            "aiosqlite>=0.19.0",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
            "structlog>=23.0.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "python-dotenv>=1.0.0",
            "livekit-agents>=1.1.4",
            "livekit-plugins-openai>=1.1.4",
            "livekit-plugins-noise-cancellation>=0.2.4",
            "langchain-community>=0.3.0",
            "duckduckgo-search>=8.0.0",
            "google-cloud-speech>=2.33.0",
            "google-cloud-texttospeech>=2.27.0",
            "google-genai>=1.23.0"
        ]
        
        subprocess.run([str(pip_path), "install"] + enhanced_requirements, check=True)
        logger.info("Dependencies installed successfully")
    
    def setup_environment_file(self):
        """Setup environment configuration"""
        env_example = self.base_dir / ".env.example"
        env_file = self.base_dir / ".env"
        
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            logger.info("Created .env file from .env.example")
        elif env_file.exists():
            logger.info(".env file already exists")
        else:
            logger.warning(".env.example not found, please create .env manually")
    
    def initialize_database(self):
        """Initialize database with schema"""
        if self.db_path.exists():
            logger.info("Database already exists")
            return
        
        logger.info("Initializing database...")
        
        # Import and initialize database
        sys.path.insert(0, str(self.base_dir))
        from database import db_manager
        
        async def init_db():
            await db_manager.init_db()
            logger.info("Database initialized successfully")
        
        asyncio.run(init_db())
    
    def run_tests(self):
        """Run comprehensive tests"""
        logger.info("Running tests...")
        
        pytest_path = self.venv_dir / ("Scripts" if os.name == 'nt' else "bin") / "pytest"
        
        try:
            result = subprocess.run([
                str(pytest_path), 
                "tests/", 
                "-v", 
                "--tb=short"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ All tests passed!")
            else:
                logger.warning("⚠️ Some tests failed:")
                logger.warning(result.stdout)
                logger.warning(result.stderr)
                
        except Exception as e:
            logger.error(f"Error running tests: {e}")
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            "logs",
            "backups",
            "exports"
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def setup_logging(self):
        """Setup initial logging configuration"""
        from logging_config import setup_logging
        setup_logging()
        logger.info("Logging configured")
    
    def display_next_steps(self):
        """Display next steps for user"""
        print("\n" + "="*60)
    print("🦷 Elo Dental Clinic - Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your actual credentials:")
    print("   - LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET")
    print("   - GOOGLE_API_KEY")
    print("\n2. Activate virtual environment:")
    if os.name == 'nt':
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("\n3. Run the agent:")
    print("   python agent.py dev")
    print("\n4. Run tests:")
    print("   pytest tests/ -v")
    print("\n5. Check logs:")
    print("   tail -f elo_clinic.log")
    print("\n📚 Documentation:")
    print("   - ARCHITECTURE.md: System architecture")
    print("   - development.md: Development guide")
    print("   - .env.example: Configuration reference")
    print("="*60)

    def run_setup(self):
        """Run complete setup process"""
        try:
            logger.info("Starting enhanced setup for Elo Dental Clinic...")
            
            self.check_python_version()
            self.create_virtual_environment()
            self.install_dependencies()
            self.setup_environment_file()
            self.create_directories()
            self.initialize_database()
            self.setup_logging()
            self.run_tests()
            self.display_next_steps()
            
            logger.info("✅ Enhanced setup completed successfully!")
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            sys.exit(1)


def main():
    """Main setup function"""
    setup = EnhancedSetup()
    setup.run_setup()


if __name__ == "__main__":
    main()
