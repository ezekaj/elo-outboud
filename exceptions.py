"""
Custom exception classes for Elo Dental Clinic system
"""


class EloBaseException(Exception):
    """Base exception class for all Elo application errors"""
    pass


class DatabaseError(EloBaseException):
    """Database-related errors"""
    pass


class ValidationError(EloBaseException):
    """Input validation errors"""
    pass


class ConfigurationError(EloBaseException):
    """Configuration-related errors"""
    pass


class AuthenticationError(EloBaseException):
    """Authentication and authorization errors"""
    pass


class ExternalServiceError(EloBaseException):
    """Errors from external services (LiveKit, OpenAI, etc.)"""
    pass


class RateLimitError(EloBaseException):
    """Rate limiting errors"""
    pass


class AppointmentError(EloBaseException):
    """Appointment scheduling and management errors"""
    pass


class PatientDataError(EloBaseException):
    """Patient data related errors"""
    pass