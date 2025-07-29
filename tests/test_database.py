"""
Tests for database operations
"""
import pytest
import pytest_asyncio
import asyncio
import tempfile
import os
from datetime import datetime, timedelta
from database import DatabaseManager
from models import Patient, Appointment, FollowUp, FollowUpStatus


@pytest_asyncio.fixture
async def test_db():
    """Create a test database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    db = DatabaseManager(db_path)
    await db.init_db()
    
    yield db
    
    # Cleanup
    await asyncio.sleep(0.1)  # Allow async operations to complete
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.mark.asyncio
async def test_database_initialization(test_db):
    """Test database initialization"""
    assert test_db._initialized is True


@pytest.mark.asyncio
async def test_add_and_get_patient(test_db):
    """Test adding and retrieving patients"""
    patient = Patient(
        name="John Doe",
        phone_number="+355671234567",
        email="john@example.com"
    )
    
    patient_id = await test_db.add_patient(patient)
    assert patient_id is not None
    
    retrieved_patient = await test_db.get_patient_by_phone("+355671234567")
    assert retrieved_patient is not None
    assert retrieved_patient.name == "John Doe"
    assert retrieved_patient.email == "john@example.com"


@pytest.mark.asyncio
async def test_add_appointment(test_db):
    """Test adding appointments"""
    # First add a patient
    patient = Patient(
        name="Jane Smith",
        phone_number="+355681234567",
        email="jane@example.com"
    )
    patient_id = await test_db.add_patient(patient)
    
    # Add appointment
    appointment = Appointment(
        patient_id=patient_id,
        patient_name="Jane Smith",
        phone_number="+355681234567",
        service_type="Regular Check-up",
        scheduled_date=datetime.now() + timedelta(days=7),
        revenue=50.0
    )
    
    appointment_id = await test_db.add_appointment(appointment)
    assert appointment_id is not None
    
    # Check analytics were updated
    stats = await test_db.get_clinic_stats()
    assert stats["total_appointments"] >= 1
    assert stats["total_revenue"] >= 50.0


@pytest.mark.asyncio
async def test_get_appointments_by_date(test_db):
    """Test retrieving appointments by date"""
    # Add test appointments
    target_date = datetime.now() + timedelta(days=3)
    
    appointment1 = Appointment(
        patient_name="Alice Brown",
        phone_number="+355691234567",
        service_type="Teeth Cleaning",
        scheduled_date=target_date.replace(hour=9, minute=0),
        revenue=75.0
    )
    
    appointment2 = Appointment(
        patient_name="Bob Wilson",
        phone_number="+355701234567",
        service_type="Consultation",
        scheduled_date=target_date.replace(hour=14, minute=0),
        revenue=50.0
    )
    
    await test_db.add_appointment(appointment1)
    await test_db.add_appointment(appointment2)
    
    # Retrieve appointments for the date
    appointments = await test_db.get_appointments_by_date(target_date)
    assert len(appointments) >= 2
    
    # Check appointment details
    services = [apt.service_type for apt in appointments]
    assert "Teeth Cleaning" in services
    assert "Consultation" in services


@pytest.mark.asyncio
async def test_follow_up_operations(test_db):
    """Test follow-up operations"""
    # Add follow-up
    follow_up = FollowUp(
        patient_name="Charlie Davis",
        phone_number="+355711234567",
        preferred_time="Next Tuesday at 2 PM",
        reason="Patient requested callback"
    )
    
    follow_up_id = await test_db.add_follow_up(follow_up)
    assert follow_up_id is not None
    
    # Get pending follow-ups
    pending_follow_ups = await test_db.get_pending_follow_ups()
    assert len(pending_follow_ups) >= 1
    
    found = any(fu.patient_name == "Charlie Davis" for fu in pending_follow_ups)
    assert found
    
    # Update follow-up status
    await test_db.update_follow_up_status(follow_up_id, FollowUpStatus.COMPLETED)
    
    # Check it's no longer pending
    pending_follow_ups = await test_db.get_pending_follow_ups()
    found = any(fu.patient_name == "Charlie Davis" for fu in pending_follow_ups)
    assert not found


@pytest.mark.asyncio
async def test_clinic_statistics(test_db):
    """Test clinic statistics"""
    # Add multiple appointments
    appointments = [
        Appointment(
            patient_name=f"Patient {i}",
            phone_number=f"+355{67 + i}1234567",
            service_type="Check-up",
            scheduled_date=datetime.now() + timedelta(days=i),
            revenue=50.0
        )
        for i in range(5)
    ]
    
    for appointment in appointments:
        await test_db.add_appointment(appointment)
    
    # Get statistics
    stats = await test_db.get_clinic_stats()
    
    assert stats["total_appointments"] >= 5
    assert stats["total_revenue"] >= 250.0
    assert stats["unique_patients"] >= 5
    assert stats["today_appointments"] >= 0
    assert stats["today_revenue"] >= 0.0


@pytest.mark.asyncio
async def test_patient_uniqueness(test_db):
    """Test patient uniqueness by phone number"""
    # Add first patient
    patient1 = Patient(
        name="Original Name",
        phone_number="+355991234567",
        email="original@example.com"
    )
    await test_db.add_patient(patient1)
    
    # Try to get patient by phone
    retrieved = await test_db.get_patient_by_phone("+355991234567")
    assert retrieved is not None
    assert retrieved.name == "Original Name"
    
    # Test non-existent patient
    non_existent = await test_db.get_patient_by_phone("+355000000000")
    assert non_existent is None


@pytest.mark.asyncio
async def test_analytics_update(test_db):
    """Test analytics update functionality"""
    initial_stats = await test_db.get_clinic_stats()
    initial_total = initial_stats["total_appointments"]
    
    # Add appointment
    appointment = Appointment(
        patient_name="Analytics Test",
        phone_number="+355881234567",
        service_type="Test Service",
        scheduled_date=datetime.now() + timedelta(days=1),
        revenue=100.0
    )
    
    await test_db.add_appointment(appointment)
    
    # Check analytics updated
    updated_stats = await test_db.get_clinic_stats()
    assert updated_stats["total_appointments"] == initial_total + 1
    assert updated_stats["total_revenue"] >= initial_stats["total_revenue"] + 100.0


@pytest.mark.asyncio
async def test_error_handling(test_db):
    """Test error handling in database operations"""
    # Test with invalid data (should not crash)
    try:
        # This should handle gracefully
        await test_db.get_appointments_by_date("invalid-date")
        assert False, "Should have raised an exception"
    except Exception as e:
        # Should handle the error gracefully
        assert "invalid" in str(e).lower() or "format" in str(e).lower()


@pytest.mark.asyncio
async def test_concurrent_operations(test_db):
    """Test concurrent database operations"""
    async def add_patient_task(i):
        patient = Patient(
            name=f"Concurrent User {i}",
            phone_number=f"+355{80 + i}1234567",
            email=f"user{i}@example.com"
        )
        return await test_db.add_patient(patient)
    
    # Run concurrent operations
    tasks = [add_patient_task(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 10
    assert all(result is not None for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
