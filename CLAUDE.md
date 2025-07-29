# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Elo - Romi Dental Clinic MCOP (Multi-Channel Outbound Platform) System, an AI-powered voice assistant for dental clinic outbound calling campaigns with emotional intelligence and comprehensive analytics capabilities.

## Common Development Commands

### Setup and Installation
```bash
# Create and activate virtual environment (Windows)
python -m venv elvi_env
.\elvi_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with LiveKit credentials and API keys
```

### Running the Application
```bash
# Development mode with auto-reload
python agent.py dev

# Production mode
python agent.py start

# Console mode for text-based testing
python agent.py console

# Connect to specific room
python agent.py connect --room-name "room-name"
```

### Testing and Diagnostics
```bash
# Run test suite
pytest tests/ -v

# Run specific test file
pytest tests/test_database.py -v

# Troubleshooting diagnostics
python troubleshoot.py

# Quick functionality check
python quick_check.py

# Test simplified model
python test_simplified_model.py
```

### Build and Quality Commands
```bash
# No specific lint/typecheck commands configured
# Consider implementing:
# - ruff for Python linting
# - mypy for type checking
# - black for code formatting
```

## High-Level Architecture

### Core Components
1. **EloDentalAgent** (`agent.py`): Main AI assistant with charming personality and emotional intelligence
2. **Database Layer** (`database.py`): SQLite with async support, following repository pattern
3. **Service Layer** (`services/`): Validation, logging, and configuration services
4. **Tool Suite** (`tools.py`): 16+ specialized dental clinic functions
5. **LiveKit Integration**: Real-time voice communication infrastructure

### Key Design Patterns
- **Repository Pattern**: All database operations isolated in `database.py`
- **Service Pattern**: Business logic separated into service modules
- **Tool/Plugin Pattern**: Extensible tool system for AI capabilities
- **Configuration Pattern**: Pydantic-based hierarchical configuration in `config.py`

### Database Schema
- **patients**: Client information and contact details
- **appointments**: Scheduled appointments with revenue tracking
- **follow_ups**: Follow-up scheduling and tracking
- **analytics**: Campaign performance and metrics

### Tool Categories
1. **Client Intelligence Tools**:
   - `assess_client_needs`: AI-powered service recommendations
   - `schedule_follow_up`: Intelligent follow-up scheduling
   
2. **Core Dental Tools**:
   - `schedule_appointment`: Real-time appointment booking
   - `get_clinic_info`: Clinic information retrieval
   - `payment_info`: Euro-based payment processing

3. **Analytics Tools**:
   - Campaign performance tracking
   - ROI calculation
   - Client segmentation

## Development Considerations

### Environment Configuration
The system uses a hierarchical configuration approach:
1. `.env` file for sensitive credentials
2. `config.py` for Pydantic-based configuration validation
3. Environment-specific settings (dev/staging/production)

### Error Handling
- Comprehensive validation using Pydantic models
- Structured logging with JSON formatting
- Graceful error recovery in voice interactions

### Security Considerations
- No phone payments (clinic-only transactions)
- Secure credential management via environment variables
- Data protection for client information

### Performance Optimization
- Async database operations with aiosqlite
- Connection pooling for database efficiency
- Structured logging with rotation to prevent disk space issues

## Testing Strategy

### Test Structure
```
tests/
├── test_database.py      # CRUD operations and data integrity
├── test_integration.py   # End-to-end workflow testing
└── test_validators.py    # Input validation and sanitization
```

### Running Tests
- Use `pytest` with `-v` flag for verbose output
- Tests use `pytest-asyncio` for async operation testing
- Mock LiveKit connections for isolated testing

## Key Files to Understand

1. **`agent.py`**: Main entry point and agent implementation
2. **`database.py`**: All database operations and schema
3. **`config.py`**: Configuration management
4. **`tools.py`**: AI tool implementations
5. **`services/validators.py`**: Input validation logic

## Deployment Notes

- Supports dev/staging/production environments
- Uses LiveKit Cloud for voice infrastructure
- Requires Google Cloud credentials for AI processing
- Euro-based payment system (clinic-only)