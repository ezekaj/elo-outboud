"""
Data models for Elo Dental Clinic system
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class AppointmentStatus(Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class FollowUpStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Patient:
    """Patient information"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    phone_number: str = ""
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Appointment:
    """Appointment details"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    patient_name: str = ""
    phone_number: str = ""
    service_type: str = ""
    scheduled_date: datetime = field(default_factory=datetime.now)
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    revenue: float = 0.0
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class FollowUp:
    """Follow-up call information"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_name: str = ""
    phone_number: str = ""
    preferred_time: str = ""
    reason: str = ""
    status: FollowUpStatus = FollowUpStatus.PENDING
    scheduled_by: str = "Elo"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class CallAnalytics:
    """Analytics for outbound calls"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    total_calls: int = 0
    appointments_booked: int = 0
    revenue_generated: float = 0.0
    conversion_rate: float = 0.0
    date: datetime = field(default_factory=datetime.now)


@dataclass
class ClinicInfo:
    """Clinic information"""
    name: str = "Romi Dental Clinic"
    location: str = "Albania"
    services: List[str] = field(default_factory=lambda: [
        "Regular check-ups and cleanings",
        "Cosmetic dentistry and whitening",
        "Emergency dental care",
        "Children's dentistry",
        "Dental implants and prosthetics"
    ])
    payment_methods: List[str] = field(default_factory=lambda: [
        "Cash (Euro)",
        "Credit Cards",
        "Debit Cards",
        "Bank Transfers"
    ])
    working_hours: dict = field(default_factory=lambda: {
        "monday": "9 AM - 6 PM",
        "tuesday": "9 AM - 6 PM",
        "wednesday": "9 AM - 6 PM",
        "thursday": "9 AM - 6 PM",
        "friday": "9 AM - 6 PM",
        "saturday": "9 AM - 2 PM",
        "sunday": "Closed"
    })
