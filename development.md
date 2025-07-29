# Elo Voice Assistant - Development Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Configuration](#configuration)
5. [Running the Agent](#running-the-agent)
6. [Common Issues & Troubleshooting](#common-issues--troubleshooting)
7. [Development Workflow](#development-workflow)
8. [Testing & Debugging](#testing--debugging)
9. [API Reference](#api-reference)

## 🎯 Project Overview

Elo is a sophisticated voice assistant built with LiveKit and Google's Realtime API. It features:
- **Personality**: Classy, sarcastic butler (inspired by Iron Man's AI)
- **Capabilities**: Weather lookup, web search, natural conversation
- **Technology**: LiveKit for real-time communication, Google Gemini for AI processing

## 🔧 Prerequisites

### Required Accounts & API Keys
1. **LiveKit Cloud Account**: [https://cloud.livekit.io/](https://cloud.livekit.io/)
2. **Google Cloud Account**: [https://console.cloud.google.com/](https://console.cloud.google.com/)

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for API calls
- **Microphone**: For voice input testing

## 🚀 Initial Setup

### 1. Clone/Download Project
```bash
# If using git
git clone <repository-url>
cd elo_base

# Or download and extract the project files
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv elvi_env
.\elvi_env\Scripts\activate

# macOS/Linux
python3 -m venv elvi_env
source elvi_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import livekit; print('LiveKit installed successfully')"
python -c "import google.genai; print('Google GenAI installed successfully')"
```

## ⚙️ Configuration

### 1. LiveKit Setup

#### Create LiveKit Project
1. Go to [LiveKit Cloud](https://cloud.livekit.io/)
2. Sign up/Login
3. Create a new project
4. Note down:
   - **Project URL** (e.g., `wss://your-project.livekit.cloud`)
   - **API Key** (starts with `API`)
   - **API Secret** (long string)

### 2. Google Cloud Setup

#### Enable Required APIs
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - **Generative AI API**
   - **Speech-to-Text API** (if needed)
   - **Text-to-Speech API** (if needed)

#### Create API Key
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. Copy the generated key

### 3. Environment Configuration

Create/update `.env` file:
```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here

# Google Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Email functionality (if implementing)
# GMAIL_APP_PASSWORD=your_app_password
# GMAIL_USER=your_email@gmail.com
```

**⚠️ Security Note**: Never commit the `.env` file to version control!

## 🏃‍♂️ Running the Agent

### Development Mode
```bash
python agent.py dev
```

### Production Mode
```bash
python agent.py start
```

### Connect to Specific Room
```bash
python agent.py connect --room-name "your-room-name"
```

### Console Mode (Text-based testing)
```bash
python agent.py console
```

## 🔍 Common Issues & Troubleshooting

### Issue 1: Connection Errors
**Symptoms**: `InvalidUrlClientError`, connection timeouts
**Causes**: 
- Incorrect LiveKit URL format
- Invalid API credentials
- Network/firewall issues

**Solutions**:
```bash
# Check URL format (must start with wss://)
# Verify credentials in LiveKit dashboard
# Test network connectivity
curl -I https://cloud.livekit.io
```

### Issue 2: Google API Errors
**Symptoms**: `403 Forbidden`, `API key invalid`
**Causes**:
- API key not enabled for required services
- Billing not set up
- API quotas exceeded

**Solutions**:
1. Enable Generative AI API in Google Cloud Console
2. Set up billing account
3. Check API quotas and usage

### Issue 3: Import Errors
**Symptoms**: `ModuleNotFoundError`
**Causes**:
- Virtual environment not activated
- Dependencies not installed
- Python version incompatibility

**Solutions**:
```bash
# Activate virtual environment
.\elvi_env\Scripts\activate  # Windows
source elvi_env/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue 4: Audio/Voice Issues
**Symptoms**: No audio input/output, voice not recognized
**Causes**:
- Microphone permissions
- Audio device configuration
- Browser compatibility

**Solutions**:
1. Check microphone permissions
2. Test with different browsers
3. Verify audio device settings

## 🔄 Development Workflow

### 1. Making Changes
The agent runs in development mode with auto-reload:
- Edit `prompts.py` for personality changes
- Edit `tools.py` for new functionality
- Edit `agent.py` for core configuration

### 2. Testing Changes
```bash
# Agent automatically reloads in dev mode
# Monitor logs for errors
# Test via debug interface: http://localhost:PORT/debug
```

### 3. Adding New Tools
```python
# In tools.py
@function_tool()
async def new_tool(context: RunContext, parameter: str) -> str:
    """Tool description for the AI"""
    # Implementation
    return result

# In agent.py, add to tools list
tools=[
    get_weather,
    search_web,
    new_tool  # Add here
]
```

## 🧪 Testing & Debugging

### Debug Interface
Access real-time debugging at: `http://localhost:PORT/debug`
- View active connections
- Monitor tool executions
- Check error logs

### Manual Testing
1. **Weather Tool**: "What's the weather in London?"
2. **Search Tool**: "Search for Python tutorials"
3. **Conversation**: "Hello Elo, how are you?"

### Log Analysis
```bash
# Check for common error patterns
grep -i "error" logs/agent.log
grep -i "failed" logs/agent.log
grep -i "timeout" logs/agent.log
```

### Performance Monitoring
- Monitor response times in debug interface
- Check memory usage: `ps aux | grep python`
- Monitor network usage during calls

## 📚 API Reference

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `LIVEKIT_URL` | Yes | WebSocket URL for LiveKit server |
| `LIVEKIT_API_KEY` | Yes | API key from LiveKit dashboard |
| `LIVEKIT_API_SECRET` | Yes | API secret from LiveKit dashboard |
| `GOOGLE_API_KEY` | Yes | Google Cloud API key |

### Agent Commands
| Command | Description |
|---------|-------------|
| `dev` | Development mode with auto-reload |
| `start` | Production mode |
| `connect` | Connect to specific room |
| `console` | Text-based testing mode |

### Tool Functions
- `get_weather(city: str)`: Get weather for specified city
- `search_web(query: str)`: Search web using DuckDuckGo

## 🚨 Emergency Troubleshooting

### Quick Fixes
1. **Restart agent**: `Ctrl+C` then `python agent.py dev`
2. **Clear cache**: Delete `__pycache__` folders
3. **Reinstall deps**: `pip install -r requirements.txt --force-reinstall`
4. **Check credentials**: Verify all API keys in `.env`

### Normal Development Mode Behaviors
- **Auto-restart**: Agent restarts when files change (normal)
- **DuplexClosed errors**: Part of restart process (can be ignored)
- **Multiple worker IDs**: Each restart creates new worker (normal)

### Automated Tools
- **Setup**: `python setup.py` - Initial project setup
- **Diagnostics**: `python troubleshoot.py` - Check for issues
- **Development**: `python agent.py dev` - Run in development mode

### Getting Help
1. Check LiveKit documentation: [https://docs.livekit.io/](https://docs.livekit.io/)
2. Google AI documentation: [https://ai.google.dev/](https://ai.google.dev/)
3. Review agent logs in debug interface
4. Test individual components separately

---

**Last Updated**: 2025-06-28
**Version**: 1.0.0
