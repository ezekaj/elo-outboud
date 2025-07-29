"""
Structured logging configuration for Elo Dental Clinic system
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
from config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging with PII masking"""
    
    @staticmethod
    def mask_pii(value: str, field_type: str) -> str:
        """Mask personally identifiable information"""
        if not value or not isinstance(value, str):
            return "***"
        
        if field_type == 'phone_number':
            # Mask phone number: show first 6 digits, mask rest, show last 2
            if len(value) > 8:
                return f"{value[:6]}***{value[-2:]}"
            return "***"
        elif field_type == 'patient_name':
            # Mask patient name: show first 2 characters only
            if len(value) > 2:
                return f"{value[:2]}***"
            return "***"
        elif field_type == 'email':
            # Mask email: show first 2 chars before @, keep domain
            if '@' in value:
                parts = value.split('@')
                if len(parts[0]) > 2:
                    return f"{parts[0][:2]}***@{parts[1]}"
            return "***"
        else:
            # Generic masking for other sensitive fields
            return f"{value[:2]}***" if len(value) > 2 else "***"
    
    def format(self, record):
        """Format log record as JSON with PII masking"""
        log_entry = {
            "timestamp": datetime.now(datetime.UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields with PII masking
        if hasattr(record, 'patient_name'):
            log_entry["patient_name"] = self.mask_pii(record.patient_name, 'patient_name')
        if hasattr(record, 'phone_number'):
            log_entry["phone_number"] = self.mask_pii(record.phone_number, 'phone_number')
        if hasattr(record, 'service_type'):
            log_entry["service_type"] = record.service_type  # Not PII
        if hasattr(record, 'appointment_id'):
            log_entry["appointment_id"] = record.appointment_id  # Not PII
        
        return json.dumps(log_entry)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_format: bool = False
) -> None:
    """Setup application logging"""
    
    # Use settings if not provided
    log_level = log_level or settings.logging.level
    log_file = log_file or settings.logging.file_path
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if json_format:
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(settings.logging.format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=settings.logging.max_file_size,
            backupCount=settings.logging.backup_count
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(settings.logging.format)
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Module-specific loggers
    loggers = {
        'elo_clinic': logging.getLogger('elo_clinic'),
        'elo_clinic.database': logging.getLogger('elo_clinic.database'),
        'elo_clinic.tools': logging.getLogger('elo_clinic.tools'),
        'elo_clinic.validators': logging.getLogger('elo_clinic.validators'),
        'elo_clinic.agent': logging.getLogger('elo_clinic.agent'),
    }
    
    for _, logger in loggers.items():
        logger.setLevel(getattr(logging, log_level.upper()))


class ContextLogger:
    """Logger with context for tracking operations"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
    
    def log_patient_operation(self, operation: str, patient_name: str, phone: str, **kwargs):
        """Log patient-related operations"""
        extra = {
            'patient_name': patient_name,
            'phone_number': phone,
            **kwargs
        }
        self.logger.info(f"{operation} for patient {patient_name}", extra=extra)
    
    def log_appointment_operation(self, operation: str, appointment_id: str, patient_name: str, **kwargs):
        """Log appointment-related operations"""
        extra = {
            'appointment_id': appointment_id,
            'patient_name': patient_name,
            **kwargs
        }
        self.logger.info(f"{operation} appointment {appointment_id}", extra=extra)
    
    def log_tool_execution(self, tool_name: str, parameters: dict, result: str):
        """Log tool execution"""
        self.logger.info(
            f"Tool {tool_name} executed",
            extra={
                'tool_name': tool_name,
                'parameters': str(parameters),
                'result_preview': result[:100] + "..." if len(result) > 100 else result
            }
        )
    
    def log_validation_error(self, field: str, value: str, error: str):
        """Log validation errors"""
        self.logger.warning(
            f"Validation failed for {field}",
            extra={
                'field': field,
                'value': value,
                'error': error
            }
        )
    
    def log_database_operation(self, operation: str, table: str, record_id: str = None):
        """Log database operations"""
        extra = {
            'operation': operation,
            'table': table
        }
        if record_id:
            extra['record_id'] = record_id
        self.logger.info(f"Database {operation} on {table}", extra=extra)


# Create context loggers
db_logger = ContextLogger('elo_clinic.database')
tool_logger = ContextLogger('elo_clinic.tools')
validator_logger = ContextLogger('elo_clinic.validators')
agent_logger = ContextLogger('elo_clinic.agent')


def get_logger(name: str) -> ContextLogger:
    """Get a context logger for a specific module"""
    return ContextLogger(name)


# Initialize logging on import
setup_logging()
