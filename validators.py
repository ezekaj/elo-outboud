"""
Input validation and sanitization for Elo Dental Clinic system
"""
import re
from datetime import datetime, date
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
import unicodedata
from config import settings


@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    value: Optional[str] = None
    error: Optional[str] = None


class PhoneNumberValidator:
    """Albanian phone number validation"""
    
    ALBANIAN_PREFIXES = ["355", "+355"]
    MOBILE_PREFIXES = ["67", "68", "69"]
    LANDLINE_PREFIXES = ["2", "3", "4"]
    
    @classmethod
    def validate(cls, phone: str) -> ValidationResult:
        """Validate Albanian phone number"""
        if not phone or not isinstance(phone, str):
            return ValidationResult(False, error="Phone number is required")
        
        # Remove all non-digits except +
        cleaned = re.sub(r'[^\d+]', '', phone.strip())
        
        # Check if it starts with country code
        if cleaned.startswith('+'):
            if not cleaned.startswith('+355'):
                return ValidationResult(False, error="Only Albanian phone numbers are supported")
            cleaned = cleaned[1:]  # Remove +
        
        # Remove country code if present
        if cleaned.startswith('355'):
            cleaned = cleaned[3:]
        
        # Validate length and prefix
        if len(cleaned) < 8 or len(cleaned) > 9:
            return ValidationResult(False, error="Invalid phone number length")
        
        # Check mobile prefixes
        if len(cleaned) == 9 and cleaned[:2] in cls.MOBILE_PREFIXES:
            formatted = f"+355{cleaned}"
            return ValidationResult(True, value=formatted)
        
        # Check landline prefixes
        if len(cleaned) == 8 and cleaned[0] in cls.LANDLINE_PREFIXES:
            formatted = f"+355{cleaned}"
            return ValidationResult(True, value=formatted)
        
        return ValidationResult(False, error="Invalid Albanian phone number format")


class DateValidator:
    """Date and time validation for appointments"""
    
    @classmethod
    def validate_appointment_date(cls, date_str: str) -> ValidationResult:
        """Validate appointment date"""
        if not date_str:
            return ValidationResult(False, error="Date is required")
        
        try:
            # Try parsing ISO format
            appointment_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Check if date is in the past
            if appointment_date.date() < date.today():
                return ValidationResult(False, error="Appointment date cannot be in the past")
            
            # Check if date is too far in future (max 1 year)
            if appointment_date.date() > date.today().replace(year=date.today().year + 1):
                return ValidationResult(False, error="Appointment date too far in future")
            
            # Check working hours
            weekday = appointment_date.strftime('%A').lower()
            if weekday not in settings.clinic.working_hours:
                return ValidationResult(False, error="Invalid weekday")
            
            # Check if it's a working day
            if weekday == 'sunday':
                return ValidationResult(False, error="Clinic is closed on Sundays")
            
            return ValidationResult(True, value=appointment_date.isoformat())
            
        except ValueError as e:
            return ValidationResult(False, error=f"Invalid date format: {str(e)}")
    
    @classmethod
    def validate_time_slot(cls, time_str: str) -> ValidationResult:
        """Validate appointment time slot"""
        if not time_str:
            return ValidationResult(False, error="Time slot is required")
        
        # Common time formats
        time_patterns = [
            r'^(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?$',
            r'^(\d{1,2})\s*(AM|PM|am|pm)$',
            r'^(\d{1,2}):(\d{2})$'
        ]
        
        for pattern in time_patterns:
            match = re.match(pattern, time_str.strip())
            if match:
                return ValidationResult(True, value=time_str.strip().upper())
        
        return ValidationResult(False, error="Invalid time format")


class NameValidator:
    """Name validation and sanitization"""
    
    DISALLOWED_PATTERNS = [
        r'<[^>]+>',  # HTML tags
        r'javascript:',  # JavaScript injection
        r'vbscript:',  # VBScript injection
        r'on\w+=',  # Event handlers
        r'data:',  # Data URLs
    ]
    
    @classmethod
    def validate(cls, name: str) -> ValidationResult:
        """Validate and sanitize name"""
        if not name or not isinstance(name, str):
            return ValidationResult(False, error="Name is required")
        
        # Strip and normalize
        name = name.strip()
        if len(name) < 2:
            return ValidationResult(False, error="Name must be at least 2 characters")
        
        if len(name) > 100:
            return ValidationResult(False, error="Name must be less than 100 characters")
        
        # Check for disallowed patterns
        for pattern in cls.DISALLOWED_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                return ValidationResult(False, error="Invalid characters in name")
        
        # Normalize unicode
        name = unicodedata.normalize('NFKC', name)
        
        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name)
        
        # Validate characters (allow letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name):
            return ValidationResult(False, error="Name contains invalid characters")
        
        # Capitalize properly
        name = ' '.join(word.capitalize() for word in name.split())
        
        return ValidationResult(True, value=name)


class ServiceTypeValidator:
    """Service type validation"""
    
    VALID_SERVICES = [
        "regular check-ups and cleanings",
        "cosmetic dentistry and whitening",
        "emergency dental care",
        "children's dentistry",
        "dental implants and prosthetics",
        "root canal treatment",
        "dental crowns",
        "teeth whitening",
        "dental fillings",
        "orthodontics"
    ]
    
    @classmethod
    def validate(cls, service: str) -> ValidationResult:
        """Validate service type"""
        if not service:
            return ValidationResult(False, error="Service type is required")
        
        service = service.strip().lower()
        
        # Check against valid services
        for valid_service in cls.VALID_SERVICES:
            if service in valid_service.lower() or valid_service.lower() in service:
                return ValidationResult(True, value=valid_service)
        
        # Allow custom services with validation
        if len(service) < 3 or len(service) > 100:
            return ValidationResult(False, error="Service description must be 3-100 characters")
        
        return ValidationResult(True, value=service.title())


class EmailValidator:
    """Email validation"""
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @classmethod
    def validate(cls, email: str) -> ValidationResult:
        """Validate email address"""
        if not email:
            return ValidationResult(True, value=None)  # Email is optional
        
        email = email.strip().lower()
        
        if len(email) > 254:  # RFC 5321 limit
            return ValidationResult(False, error="Email address too long")
        
        if not cls.EMAIL_PATTERN.match(email):
            return ValidationResult(False, error="Invalid email format")
        
        return ValidationResult(True, value=email)


class InputSanitizer:
    """General input sanitization"""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 500) -> str:
        """Sanitize general text input"""
        if not text:
            return ""
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text
    
    @staticmethod
    def sanitize_phone_notes(notes: str) -> str:
        """Sanitize phone call notes"""
        return InputSanitizer.sanitize_text(notes, max_length=1000)


class ValidationManager:
    """Central validation manager"""
    
    @staticmethod
    def validate_patient_data(name: str, phone: str, email: Optional[str] = None) -> Dict[str, ValidationResult]:
        """Validate patient registration data"""
        return {
            "name": NameValidator.validate(name),
            "phone": PhoneNumberValidator.validate(phone),
            "email": EmailValidator.validate(email or "")
        }
    
    @staticmethod
    def validate_appointment_data(
        patient_name: str,
        phone: str,
        service: str,
        appointment_date: str,
        notes: Optional[str] = None
    ) -> Dict[str, ValidationResult]:
        """Validate appointment booking data"""
        return {
            "patient_name": NameValidator.validate(patient_name),
            "phone": PhoneNumberValidator.validate(phone),
            "service": ServiceTypeValidator.validate(service),
            "appointment_date": DateValidator.validate_appointment_date(appointment_date),
            "notes": ValidationResult(True, value=InputSanitizer.sanitize_phone_notes(notes or ""))
        }
    
    @staticmethod
    def validate_follow_up_data(
        patient_name: str,
        phone: str,
        preferred_time: str,
        reason: str
    ) -> Dict[str, ValidationResult]:
        """Validate follow-up scheduling data"""
        return {
            "patient_name": NameValidator.validate(patient_name),
            "phone": PhoneNumberValidator.validate(phone),
            "preferred_time": DateValidator.validate_time_slot(preferred_time),
            "reason": ValidationResult(True, value=InputSanitizer.sanitize_text(reason, max_length=200))
        }


# Export commonly used validators
validate_phone = PhoneNumberValidator.validate
validate_name = NameValidator.validate
validate_email = EmailValidator.validate
validate_service = ServiceTypeValidator.validate
validate_appointment_date = DateValidator.validate_appointment_date
