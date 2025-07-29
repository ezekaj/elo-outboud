"""
Tests for input validation and sanitization
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from validators import (
    PhoneNumberValidator,
    NameValidator,
    EmailValidator,
    DateValidator,
    ServiceTypeValidator,
    ValidationManager,
    validate_phone,
    validate_name,
    validate_email,
    validate_service,
    validate_appointment_date
)


class TestPhoneNumberValidator:
    """Test phone number validation"""
    
    def test_valid_albanian_mobile(self):
        """Test valid Albanian mobile numbers"""
        test_cases = [
            "+355671234567",
            "355671234567",
            "+355 67 123 4567",
            "0671234567",
            "671234567"
        ]
        
        for phone in test_cases:
            result = PhoneNumberValidator.validate(phone)
            assert result.is_valid, f"Failed for {phone}: {result.error}"
            assert result.value.startswith("+355")
    
    def test_valid_albanian_landline(self):
        """Test valid Albanian landline numbers"""
        test_cases = [
            "+35521234567",
            "35521234567",
            "021234567"
        ]
        
        for phone in test_cases:
            result = PhoneNumberValidator.validate(phone)
            assert result.is_valid, f"Failed for {phone}: {result.error}"
            assert result.value.startswith("+355")
    
    def test_invalid_phone_numbers(self):
        """Test invalid phone numbers"""
        test_cases = [
            ("", "Phone number is required"),
            ("123", "Invalid phone number length"),
            ("+123456789012", "Only Albanian phone numbers are supported"),
            ("3551234567", "Invalid phone number length"),
            ("invalid", "Invalid Albanian phone number format")
        ]
        
        for phone, expected_error in test_cases:
            result = PhoneNumberValidator.validate(phone)
            assert not result.is_valid
            assert expected_error in result.error


class TestNameValidator:
    """Test name validation"""
    
    def test_valid_names(self):
        """Test valid names"""
        test_cases = [
            "John Doe",
            "Maria Smith",
            "Jean-Pierre Dubois",
            "O'Connor",
            "Dr. Smith",
            "Anna-Maria"
        ]
        
        for name in test_cases:
            result = NameValidator.validate(name)
            assert result.is_valid, f"Failed for {name}: {result.error}"
    
    def test_invalid_names(self):
        """Test invalid names"""
        test_cases = [
            ("", "Name is required"),
            ("A", "Name must be at least 2 characters"),
            ("a" * 101, "Name must be less than 100 characters"),
            ("<script>alert('xss')</script>", "Invalid characters in name"),
            ("javascript:alert(1)", "Invalid characters in name"),
            ("123Invalid", "Name contains invalid characters")
        ]
        
        for name, expected_error in test_cases:
            result = NameValidator.validate(name)
            assert not result.is_valid
            assert expected_error in result.error
    
    def test_name_sanitization(self):
        """Test name sanitization"""
        test_cases = [
            ("  john   doe  ", "John Doe"),
            ("JOHN DOE", "John Doe"),
            ("john-doe", "John-Doe"),
            ("o'connor", "O'Connor")
        ]
        
        for input_name, expected in test_cases:
            result = NameValidator.validate(input_name)
            assert result.is_valid
            assert result.value == expected


class TestEmailValidator:
    """Test email validation"""
    
    def test_valid_emails(self):
        """Test valid email addresses"""
        test_cases = [
            "test@example.com",
            "user.name@domain.co.uk",
            "firstname.lastname@company.org",
            "user+tag@example.com"
        ]
        
        for email in test_cases:
            result = EmailValidator.validate(email)
            assert result.is_valid
            assert result.value == email.lower()
    
    def test_invalid_emails(self):
        """Test invalid email addresses"""
        test_cases = [
            ("invalid", "Invalid email format"),
            ("@example.com", "Invalid email format"),
            ("user@", "Invalid email format"),
            ("user@example", "Invalid email format"),
            ("a" * 250 + "@example.com", "Email address too long")
        ]
        
        for email, expected_error in test_cases:
            result = EmailValidator.validate(email)
            assert not result.is_valid
            assert expected_error in result.error
    
    def test_empty_email(self):
        """Test empty email (should be valid as optional)"""
        result = EmailValidator.validate("")
        assert result.is_valid
        assert result.value is None


class TestDateValidator:
    """Test date validation"""
    
    def test_valid_dates(self):
        """Test valid appointment dates"""
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        result = DateValidator.validate_appointment_date(future_date)
        assert result.is_valid
    
    def test_past_dates(self):
        """Test past dates"""
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        result = DateValidator.validate_appointment_date(past_date)
        assert not result.is_valid
        assert "past" in result.error
    
    def test_far_future_dates(self):
        """Test dates too far in future"""
        far_future = (datetime.now() + timedelta(days=400)).isoformat()
        result = DateValidator.validate_appointment_date(far_future)
        assert not result.is_valid
        assert "too far" in result.error
    
    def test_invalid_date_format(self):
        """Test invalid date formats"""
        test_cases = [
            "invalid-date",
            "2023-13-45",
            "not-a-date"
        ]
        
        for date_str in test_cases:
            result = DateValidator.validate_appointment_date(date_str)
            assert not result.is_valid
            assert "Invalid date format" in result.error


class TestServiceTypeValidator:
    """Test service type validation"""
    
    def test_valid_services(self):
        """Test valid service types"""
        test_cases = [
            "regular check-ups",
            "cosmetic dentistry",
            "emergency care",
            "children's dentistry",
            "dental implants"
        ]
        
        for service in test_cases:
            result = ServiceTypeValidator.validate(service)
            assert result.is_valid
    
    def test_custom_services(self):
        """Test custom service types"""
        result = ServiceTypeValidator.validate("custom dental service")
        assert result.is_valid
        assert result.value == "Custom Dental Service"
    
    def test_invalid_services(self):
        """Test invalid service types"""
        test_cases = [
            ("", "Service type is required"),
            ("a", "Service description must be 3-100 characters"),
            ("a" * 101, "Service description must be 3-100 characters")
        ]
        
        for service, expected_error in test_cases:
            result = ServiceTypeValidator.validate(service)
            assert not result.is_valid
            assert expected_error in result.error


class TestValidationManager:
    """Test validation manager"""
    
    def test_validate_patient_data(self):
        """Test patient data validation"""
        result = ValidationManager.validate_patient_data(
            "John Doe",
            "+355671234567",
            "john@example.com"
        )
        
        assert all(r.is_valid for r in result.values())
        assert result["name"].value == "John Doe"
        assert result["phone"].value == "+355671234567"
        assert result["email"].value == "john@example.com"
    
    def test_validate_appointment_data(self):
        """Test appointment data validation"""
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        result = ValidationManager.validate_appointment_data(
            "John Doe",
            "+355671234567",
            "regular check-up",
            future_date,
            "Patient has sensitive teeth"
        )
        
        assert all(r.is_valid for r in result.values())
        assert result["patient_name"].value == "John Doe"
        assert result["phone"].value == "+355671234567"
        assert result["service"].value == "Regular check-ups and cleanings"
    
    def test_validate_follow_up_data(self):
        """Test follow-up data validation"""
        result = ValidationManager.validate_follow_up_data(
            "John Doe",
            "+355671234567",
            "Next week",
            "Patient requested callback"
        )
        
        assert all(r.is_valid for r in result.values())
        assert result["patient_name"].value == "John Doe"
        assert result["phone"].value == "+355671234567"


@pytest.mark.asyncio
async def test_integration_validators():
    """Test integration of validators"""
    # Test complete patient registration flow
    patient_data = {
        "name": "Maria Garcia",
        "phone": "+355681234567",
        "email": "maria@example.com"
    }
    
    result = ValidationManager.validate_patient_data(**patient_data)
    assert all(r.is_valid for r in result.values())
    
    # Test complete appointment booking flow
    future_date = (datetime.now() + timedelta(days=3)).isoformat()
    appointment_data = {
        "patient_name": "Maria Garcia",
        "phone": "+355681234567",
        "service": "cosmetic dentistry",
        "appointment_date": future_date,
        "notes": "Interested in teeth whitening"
    }
    
    result = ValidationManager.validate_appointment_data(**appointment_data)
    assert all(r.is_valid for r in result.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
