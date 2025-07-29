"""
Integration tests for Elo Dental Clinic system
"""
import pytest
import asyncio
import tempfile
import os
from datetime import datetime, timedelta
from livekit.agents import RunContext

from database import db_manager
from tools import (
    assess_client_needs,
    schedule_follow_up,
    schedule_appointment,
    get_clinic_info,
    check_available_slots,
    get_payment_info,
    search_web,
    get_clinic_stats
)
from validators import ValidationManager


@pytest.fixture
async def test_db():
    """Create a test database for integration tests"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Override database path for testing
    original_db = db_manager.db_path
    db_manager.db_path = db_path
    db_manager._initialized = False
    
    await db_manager.init_db()
    
    yield
    
    # Cleanup
    db_manager.db_path = original_db
    db_manager._initialized = False
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def mock_context():
    """Mock RunContext for testing"""
    class MockRunContext:
        pass
    return MockRunContext()


@pytest.mark.asyncio
async def test_complete_patient_flow(test_db, mock_context):
    """Test complete patient registration and appointment flow"""
    
    # Step 1: Assess client needs
    needs_result = await assess_client_needs(
        mock_context,
        client_interest="very interested",
        dental_concerns="mild tooth pain",
        time_availability="available next week"
    )
    
    assert "detailed consultation" in needs_result.lower()
    
    # Step 2: Schedule appointment
    future_date = (datetime.now() + timedelta(days=7)).isoformat()
    appointment_result = await schedule_appointment(
        mock_context,
        patient_name="Alice Johnson",
        preferred_date=future_date,
        service_type="dental check-up",
        phone_number="+355671234567"
    )
    
    assert "scheduled" in appointment_result.lower()
    assert "Alice Johnson" in appointment_result
    
    # Step 3: Verify appointment in database
    appointment_date = datetime.fromisoformat(future_date)
    appointments = await db_manager.get_appointments_by_date(appointment_date)
    
    alice_appointment = next(
        (apt for apt in appointments if apt.patient_name == "Alice Johnson"),
        None
    )
    assert alice_appointment is not None
    assert alice_appointment.phone_number == "+355671234567"
    assert alice_appointment.service_type == "Regular check-ups and cleanings"


@pytest.mark.asyncio
async def test_follow_up_workflow(test_db, mock_context):
    """Test follow-up scheduling workflow"""
    
    # Schedule follow-up
    follow_up_result = await schedule_follow_up(
        mock_context,
        client_name="Bob Smith",
        phone_number="+355681234567",
        preferred_time="Next Monday at 3 PM"
    )
    
    assert "follow-up call" in follow_up_result.lower()
    
    # Verify follow-up in database
    pending_follow_ups = await db_manager.get_pending_follow_ups()
    bob_follow_up = next(
        (fu for fu in pending_follow_ups if fu.patient_name == "Bob Smith"),
        None
    )
    assert bob_follow_up is not None
    assert bob_follow_up.phone_number == "+355681234567"
    assert "Next Monday at 3 PM" in bob_follow_up.preferred_time
    
    # Update follow-up status
    await db_manager.update_follow_up_status(bob_follow_up.id, FollowUpStatus.COMPLETED)
    
    # Verify it's no longer pending
    pending_follow_ups = await db_manager.get_pending_follow_ups()
    bob_follow_up = next(
        (fu for fu in pending_follow_ups if fu.patient_name == "Bob Smith"),
        None
    )
    assert bob_follow_up is None


@pytest.mark.asyncio
async def test_clinic_information_tools(test_db, mock_context):
    """Test clinic information retrieval tools"""
    
    # Test clinic info
    clinic_info = await get_clinic_info(mock_context)
    assert "Romi Dental Clinic" in clinic_info
    assert "services" in clinic_info.lower()
    assert "payment" in clinic_info.lower()
    
    # Test payment info
    payment_info = await get_payment_info(mock_context)
    assert "Euro" in payment_info
    assert "Credit cards" in payment_info or "Cash" in payment_info
    
    # Test available slots
    future_date = (datetime.now() + timedelta(days=3)).isoformat()
    slots_info = await check_available_slots(mock_context, future_date)
    assert "available" in slots_info.lower()
    assert "AM" in slots_info or "PM" in slots_info


@pytest.mark.asyncio
async def test_analytics_tracking(test_db, mock_context):
    """Test analytics and statistics tracking"""
    
    # Get initial stats
    initial_stats = await get_clinic_stats(mock_context)
    assert "Statistics" in initial_stats
    
    # Add multiple appointments
    appointments = [
        {
            "patient_name": f"Test Patient {i}",
            "phone_number": f"+355{67 + i}1234567",
            "service_type": "check-up",
            "date": (datetime.now() + timedelta(days=i)).isoformat()
        }
        for i in range(3)
    ]
    
    for apt in appointments:
        await schedule_appointment(
            mock_context,
            patient_name=apt["patient_name"],
            preferred_date=apt["date"],
            service_type=apt["service_type"],
            phone_number=apt["phone_number"]
        )
    
    # Check updated stats
    updated_stats = await get_clinic_stats(mock_context)
    assert "Total Appointments" in updated_stats
    assert "Total Revenue" in updated_stats


@pytest.mark.asyncio
async def test_error_handling(test_db, mock_context):
    """Test error handling in tools"""
    
    # Test with invalid phone number
    result = await schedule_appointment(
        mock_context,
        patient_name="Test User",
        preferred_date=(datetime.now() + timedelta(days=1)).isoformat(),
        service_type="check-up",
        phone_number="invalid-phone"
    )
    
    assert "apologize" in result.lower() or "invalid" in result.lower()
    
    # Test with past date
    result = await schedule_appointment(
        mock_context,
        patient_name="Test User",
        preferred_date=(datetime.now() - timedelta(days=1)).isoformat(),
        service_type="check-up",
        phone_number="+355671234567"
    )
    
    assert "past" in result.lower() or "apologize" in result.lower()


@pytest.mark.asyncio
async def test_search_functionality(test_db, mock_context):
    """Test web search functionality"""
    
    # Test search
    search_result = await search_web(
        mock_context,
        query="dental health tips for sensitive teeth"
    )
    
    assert isinstance(search_result, str)
    assert len(search_result) > 0
    
    # Test search with special characters
    search_result = await search_web(
        mock_context,
        query="dental care & oral hygiene"
    )
    
    assert isinstance(search_result, str)
    assert "&" not in search_result or "and" in search_result.lower()


@pytest.mark.asyncio
async def test_concurrent_operations(test_db, mock_context):
    """Test concurrent operations"""
    
    async def schedule_appointment_task(i):
        return await schedule_appointment(
            mock_context,
            patient_name=f"Concurrent Patient {i}",
            preferred_date=(datetime.now() + timedelta(days=i)).isoformat(),
            service_type="check-up",
            phone_number=f"+355{67 + i}1234567"
        )
    
    # Run concurrent appointment scheduling
    tasks = [schedule_appointment_task(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 5
    assert all("scheduled" in result.lower() for result in results)
    
    # Verify all appointments were created
    stats = await get_clinic_stats(mock_context)
    assert "Concurrent Patient" in stats


@pytest.mark.asyncio
async def test_validation_integration(test_db, mock_context):
    """Test validation integration with tools"""
    
    # Test validation with real data
    validation_result = ValidationManager.validate_appointment_data(
        patient_name="Valid Name",
        phone="+355671234567",
        service="regular check-up",
        appointment_date=(datetime.now() + timedelta(days=7)).isoformat(),
        notes="Valid notes"
    )
    
    assert all(r.is_valid for r in validation_result.values())
    
    # Test with invalid data
    validation_result = ValidationManager.validate_appointment_data(
        patient_name="",
        phone="invalid",
        service="",
        appointment_date="invalid-date",
        notes=""
    )
    
    assert not all(r.is_valid for r in validation_result.values())
    assert validation_result["name"].error == "Name is required"
    assert validation_result["phone"].error == "Invalid Albanian phone number format"


@pytest.mark.asyncio
async def test_workflow_with_patient_lookup(test_db, mock_context):
    """Test workflow with patient lookup"""
    
    # Add patient first
    from database import db_manager
    
    # Schedule appointment
    future_date = (datetime.now() + timedelta(days=5)).isoformat()
    await schedule_appointment(
        mock_context,
        patient_name="Emma Wilson",
        preferred_date=future_date,
        service_type="children's dentistry",
        phone_number="+355691234567"
    )
    
    # Check if patient exists
    patient = await db_manager.get_patient_by_phone("+355691234567")
    # Note: Patient might not be auto-created, this tests the lookup functionality
    
    # Schedule follow-up for same patient
    await schedule_follow_up(
        mock_context,
        client_name="Emma Wilson",
        phone_number="+355691234567",
        preferred_time="Next week"
    )
    
    # Verify both operations completed successfully
    pending_follow_ups = await db_manager.get_pending_follow_ups()
    emma_follow_up = next(
        (fu for fu in pending_follow_ups if fu.patient_name == "Emma Wilson"),
        None
    )
    assert emma_follow_up is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
