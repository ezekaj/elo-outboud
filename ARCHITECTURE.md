# Elo Dental Clinic System - Architecture Documentation

## 🏗️ System Overview

The Elo Dental Clinic system is a production-ready AI-powered voice assistant designed specifically for dental clinic outbound calling campaigns. The system has been enhanced with enterprise-grade features including persistent storage, comprehensive validation, structured logging, and monitoring capabilities.

## 📊 Architecture Components

### 1. **Core Architecture**
- **Framework**: LiveKit-based real-time voice communication
- **AI Engine**: Google Realtime API with GPT-4 integration
- **Database**: SQLite with async support via aiosqlite
- **Configuration**: Pydantic-based hierarchical configuration
- **Logging**: Structured logging with JSON formatting and rotation

### 2. **Data Layer**
```
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Patients   │  │ Appointments │  │   Follow-ups     │  │
│  │   Table     │  │    Table     │  │     Table        │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Analytics Table                        │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3. **Service Layer**
```
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐                │
│  │   Validation    │  │   Database       │                │
│  │   Service       │  │   Service        │                │
│  └─────────────────┘  └──────────────────┘                │
│  ┌─────────────────┐  ┌──────────────────┐                │
│  │   Logging       │  │   Configuration  │                │
│  │   Service       │  │   Service        │                │
│  └─────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 4. **Tool Layer**
```
┌─────────────────────────────────────────────────────────────┐
│                    Tool Layer                               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐                │
│  │ assess_client_  │  │ schedule_        │                │
│  │ needs           │  │ appointment      │                │
│  └─────────────────┘  └──────────────────┘                │
│  ┌─────────────────┐  ┌──────────────────┐                │
│  │ schedule_       │  │ get_clinic_      │                │
│  │ follow_up       │  │ info             │                │
│  └─────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ Database Schema

### Patients Table
```sql
CREATE TABLE patients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Appointments Table
```sql
CREATE TABLE appointments (
    id TEXT PRIMARY KEY,
    patient_id TEXT,
    patient_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    service_type TEXT NOT NULL,
    scheduled_date TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'scheduled',
    revenue REAL DEFAULT 0.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
);
```

### Follow-ups Table
```sql
CREATE TABLE follow_ups (
    id TEXT PRIMARY KEY,
    patient_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    preferred_time TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    scheduled_by TEXT DEFAULT 'Elo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

### Analytics Table
```sql
CREATE TABLE call_analytics (
    id TEXT PRIMARY KEY,
    total_calls INTEGER DEFAULT 0,
    appointments_booked INTEGER DEFAULT 0,
    revenue_generated REAL DEFAULT 0.0,
    conversion_rate REAL DEFAULT 0.0,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration System

### Environment-based Configuration
The system uses Pydantic for type-safe configuration:

```python
# Configuration hierarchy
AppSettings
├── DatabaseSettings
├── SecuritySettings
├── ClinicSettings
├── LiveKitSettings
├── GoogleSettings
└── LoggingSettings
```

### Configuration Validation
- Type checking with Pydantic
- Environment variable validation
- Range validation for numeric values
- Format validation for URLs and keys

## 🛡️ Validation System

### Input Validation
- **Phone Numbers**: Albanian format validation (+355 prefix)
- **Names**: XSS prevention and sanitization
- **Emails**: RFC-compliant email validation
- **Dates**: Past/future date validation
- **Service Types**: Whitelist-based validation

### Security Features
- SQL injection prevention via parameterized queries
- XSS prevention via input sanitization
- Rate limiting (configurable per hour)
- Input length restrictions

## 📊 Logging & Monitoring

### Structured Logging
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "elo_clinic.tools",
  "message": "Appointment scheduled",
  "patient_name": "John Doe",
  "phone_number": "+355671234567",
  "appointment_id": "uuid-here"
}
```

### Log Rotation
- Automatic log rotation at 10MB
- 5 backup files retained
- JSON format for easy parsing
- Contextual information included

## 🧪 Testing Strategy

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end workflow testing
3. **Database Tests**: CRUD operation testing
4. **Validation Tests**: Input validation testing
5. **Concurrent Tests**: Multi-threading testing

### Test Coverage
- ✅ All tools and functions
- ✅ Database operations
- ✅ Input validation
- ✅ Error handling
- ✅ Concurrent operations

## 🚀 Deployment Architecture

### Development Environment
```bash
# Quick start
cp .env.example .env
# Edit .env with your values
python agent.py dev
```

### Production Environment
```bash
# Production deployment
export ENVIRONMENT=production
export LOG_LEVEL=WARNING
python agent.py start
```

### Docker Support (Future)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "agent.py", "start"]
```

## 📈 Performance Considerations

### Database Optimization
- Indexed columns for fast lookups
- Connection pooling for concurrent access
- Async operations for non-blocking I/O
- Optimized queries with EXPLAIN analysis

### Memory Management
- Lazy loading of database connections
- Efficient data models with dataclasses
- Garbage collection optimization
- Resource cleanup on shutdown

### Scalability Features
- Stateless design for horizontal scaling
- Database sharding support (future)
- Caching layer support (future)
- Load balancing ready

## 🔍 Monitoring & Observability

### Health Checks
- Database connectivity check
- API endpoint availability
- Memory usage monitoring
- Error rate tracking

### Metrics Collection
- Appointment booking rate
- Conversion rate tracking
- Response time monitoring
- Patient satisfaction metrics

## 🔄 Migration Strategy

### From In-Memory to Database
1. **Phase 1**: Deploy new system alongside old
2. **Phase 2**: Migrate existing data (if any)
3. **Phase 3**: Switch traffic to new system
4. **Phase 4**: Decommission old system

### Data Migration Script
```python
# Example migration script
async def migrate_data():
    # Migrate from old clinic_data structure
    old_data = {...}  # Load old data
    for appointment in old_data["appointments"]:
        await db_manager.add_appointment(Appointment(...))
```

## 🛠️ Development Workflow

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run with development config
python agent.py dev
```

### Code Quality
- Type hints throughout codebase
- Comprehensive docstrings
- PEP 8 compliant formatting
- Automated testing on CI/CD

## 📋 Future Enhancements

### Phase 2 Features
- [ ] Email notifications
- [ ] SMS reminders
- [ ] Calendar integration
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

### Phase 3 Features
- [ ] Machine learning for appointment optimization
- [ ] Voice sentiment analysis
- [ ] Predictive scheduling
- [ ] Integration with practice management systems
- [ ] Mobile app for patients

## 🔗 API Reference

### Tool Functions
- `assess_client_needs(client_interest, dental_concerns, time_availability)`
- `schedule_appointment(patient_name, preferred_date, service_type, phone_number)`
- `schedule_follow_up(client_name, phone_number, preferred_time)`
- `get_clinic_info()`
- `check_available_slots(preferred_date)`
- `get_payment_info()`
- `search_web(query)`
- `get_clinic_stats()`

### Configuration Reference
See `.env.example` for all available configuration options.

## 📞 Support & Troubleshooting

### Common Issues
1. **Database locked**: Ensure proper async handling
2. **Validation errors**: Check input format requirements
3. **Connection issues**: Verify LiveKit credentials
4. **Performance issues**: Check database indexes

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python agent.py dev
```

### Health Check Endpoint
```python
# Built into the system
stats = await get_clinic_stats()
```

---

**Last Updated**: 2025-07-16  
**Version**: 2.0.0 - Enhanced Production System
