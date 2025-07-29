from datetime import datetime
from livekit.agents import function_tool, RunContext
from langchain_community.tools import DuckDuckGoSearchRun

from database import db_manager
from models import Appointment, FollowUp
from validators import (
    validate_name, validate_phone,
    validate_appointment_date, ValidationManager
)
from logging_config import tool_logger, validator_logger
from config import settings
from exceptions import (
    DatabaseError, ValidationError, ExternalServiceError,
    AppointmentError, PatientDataError, RateLimitError
)

# Database will be initialized when first used

async def ensure_db_initialized():
    """Ensure database is initialized"""
    if not db_manager._initialized:
        await db_manager.init_db()

# Core Tools for Dental Outbound Calls

@function_tool()
async def assess_client_needs(
    context: RunContext,
    client_interest: str,
    dental_concerns: str,
    time_availability: str) -> str:
    """
    Assess client needs and determine the best approach for the conversation.
    """
    try:
        # Log the assessment
        tool_logger.log_tool_execution(
            "assess_client_needs",
            {
                "client_interest": client_interest,
                "dental_concerns": dental_concerns,
                "time_availability": time_availability
            },
            "Assessment started"
        )
        
        # Enhanced assessment logic
        concerns_lower = dental_concerns.lower()
        interest_lower = client_interest.lower()
        time_lower = time_availability.lower()
        
        if any(word in concerns_lower for word in ["pain", "emergency", "urgent", "hurt"]):
            recommendation = "emergency consultation"
            urgency = "high"
        elif "interested" in interest_lower and "available" in time_lower:
            recommendation = "detailed consultation"
            urgency = "medium"
        elif "busy" in time_lower or "later" in time_lower:
            recommendation = "follow-up call"
            urgency = "low"
        else:
            recommendation = "general consultation"
            urgency = "medium"
        
        # Update analytics
        await db_manager._update_analytics(revenue=0.0)
        
        tool_logger.log_tool_execution(
            "assess_client_needs",
            {"urgency": urgency, "recommendation": recommendation},
            f"Assessment completed: {recommendation}"
        )
        
        return f"Based on your needs, I recommend a {recommendation}. This would be the best way to help you with your dental health goals. The urgency level is {urgency}."
        
    except DatabaseError as e:
        tool_logger.logger.error(f"Database error during client assessment: {e}", exc_info=True)
        return "I'm having trouble accessing our system right now. Let me help you with general information about our services."
    except ValidationError as e:
        tool_logger.logger.warning(f"Validation error in client assessment: {e}")
        return f"I need to clarify some information: {str(e)}"
    except Exception as e:
        tool_logger.logger.critical(f"Unexpected error in client assessment: {e}", exc_info=True)
        return "I apologize, but I'm experiencing technical difficulties. Please call our clinic directly for immediate assistance."

@function_tool()
async def schedule_follow_up(
    context: RunContext,
    client_name: str,
    phone_number: str,
    preferred_time: str) -> str:
    """
    Schedule a follow-up call or send reminders when the client is busy.
    """
    try:
        # Validate inputs
        name_validation = validate_name(client_name)
        phone_validation = validate_phone(phone_number)
        
        if not name_validation.is_valid:
            validator_logger.log_validation_error("client_name", client_name, name_validation.error)
            return f"I apologize, but {name_validation.error}"
        
        if not phone_validation.is_valid:
            validator_logger.log_validation_error("phone_number", phone_number, phone_validation.error)
            return f"I apologize, but {phone_validation.error}"
        
        # Create follow-up
        follow_up = FollowUp(
            patient_name=name_validation.value,
            phone_number=phone_validation.value,
            preferred_time=preferred_time,
            reason="Follow-up from initial call"
        )
        
        follow_up_id = await db_manager.add_follow_up(follow_up)
        
        tool_logger.log_patient_operation(
            "follow_up_scheduled",
            name_validation.value,
            phone_validation.value,
            follow_up_id=follow_up_id,
            preferred_time=preferred_time
        )
        
        return f"Perfect! I've scheduled a follow-up call for {preferred_time}. I'll call you back then to discuss your dental health needs. Thank you for your time!"
        
    except ValidationError as e:
        tool_logger.logger.warning(f"Validation error in follow-up scheduling: {e}")
        return f"I need to clarify some information: {str(e)}"
    except DatabaseError as e:
        tool_logger.logger.error(f"Database error during follow-up scheduling: {e}", exc_info=True)
        return "I'm having trouble with our scheduling system. I'll make sure to call you back at a better time."
    except Exception as e:
        tool_logger.logger.critical(f"Unexpected error scheduling follow-up: {e}", exc_info=True)
        return "I apologize for the technical difficulty. I'll make a note to have someone from our clinic call you back. Thank you for your patience!"

@function_tool()
async def schedule_appointment(
    context: RunContext,
    patient_name: str,
    preferred_date: str,
    service_type: str,
    phone_number: str) -> str:
    """
    Schedule a dental appointment for a patient. Use this when the patient agrees to book an appointment.
    """
    try:
        # Ensure database is initialized
        await ensure_db_initialized()

        # Validate all inputs
        validations = ValidationManager.validate_appointment_data(
            patient_name, phone_number, service_type, preferred_date
        )
        
        # Check for validation errors
        errors = []
        for field, result in validations.items():
            if not result.is_valid:
                validator_logger.log_validation_error(field, str(locals().get(field, "")), result.error)
                errors.append(f"{field}: {result.error}")
        
        if errors:
            return f"I apologize, but I need to correct the following: {', '.join(errors)}"
        
        # Create appointment
        appointment = Appointment(
            patient_name=validations["patient_name"].value,
            phone_number=validations["phone_number"].value,
            service_type=validations["service_type"].value,
            scheduled_date=datetime.fromisoformat(validations["appointment_date"].value),
            revenue=settings.clinic.consultation_fee
        )
        
        appointment_id = await db_manager.add_appointment(appointment)
        
        tool_logger.log_patient_operation(
            "appointment_scheduled",
            validations["patient_name"].value,
            validations["phone_number"].value,
            appointment_id=appointment_id,
            service_type=validations["service_type"].value,
            scheduled_date=validations["appointment_date"].value
        )
        
        return f"Excellent! I've scheduled your {validations['service_type'].value} appointment for {preferred_date}. You'll receive a confirmation shortly. All payments are made at our clinic in Euro for your security. Thank you for choosing Romi Dental!"
        
    except Exception as e:
        tool_logger.logger.error(f"Error scheduling appointment: {e}", exc_info=True)
        return "I apologize, but I'm having trouble scheduling your appointment right now. Please call our clinic directly."

@function_tool()
async def get_clinic_info(context: RunContext) -> str:
    """
    Get information about Romi Dental Clinic including services and contact details.
    """
    try:
        clinic_info = f"""{settings.clinic.name} offers comprehensive dental services with experienced professionals. I'm Elo, your AI assistant.

Our services include:
{chr(10).join(f"• {service}" for service in settings.clinic.services)}

Hours: 
{chr(10).join(f"• {day.title()}: {hours}" for day, hours in settings.clinic.working_hours.items())}

Payment methods:
{chr(10).join(f"• {method}" for method in settings.clinic.payment_methods)}

Special offers available for new patients!"""
        
        tool_logger.log_tool_execution("get_clinic_info", {}, "Clinic info retrieved")
        return clinic_info
        
    except Exception as e:
        tool_logger.logger.error(f"Error getting clinic info: {e}", exc_info=True)
        return "I apologize, but I'm having trouble retrieving clinic information right now."

@function_tool()
async def check_available_slots(context: RunContext, preferred_date: str) -> str:
    """
    Check available appointment slots for a specific date.
    """
    try:
        # Validate date
        date_validation = validate_appointment_date(preferred_date)
        if not date_validation.is_valid:
            return f"I apologize, but {date_validation.error}"
        
        # Get appointments for the date
        appointment_date = datetime.fromisoformat(date_validation.value)
        appointments = await db_manager.get_appointments_by_date(appointment_date)
        
        # Generate available slots based on working hours
        weekday = appointment_date.strftime('%A').lower()
        if weekday not in settings.clinic.working_hours:
            return "Sorry, that date is not available for appointments."
        
        # Sample available slots (in real implementation, this would check against booked appointments)
        all_slots = ["9:00 AM", "10:30 AM", "12:00 PM", "2:00 PM", "3:30 PM", "4:30 PM"]
        
        # Filter out booked slots
        booked_times = [apt.scheduled_date.strftime("%I:%M %p") for apt in appointments]
        available_slots = [slot for slot in all_slots if slot not in booked_times]
        
        if not available_slots:
            return f"Sorry, all slots are booked for {preferred_date}. Would you like to check another date?"
        
        tool_logger.log_tool_execution(
            "check_available_slots",
            {"preferred_date": preferred_date},
            f"Found {len(available_slots)} available slots"
        )
        
        return f"For {preferred_date}, we have slots available at: {', '.join(available_slots)}. These are filling up quickly! Would you like me to book one of these times? We have special offers for new patients."
        
    except Exception as e:
        tool_logger.logger.error(f"Error checking available slots: {e}", exc_info=True)
        return "I apologize, but I'm having trouble checking available slots right now."

@function_tool()
async def get_payment_info(context: RunContext) -> str:
    """
    Provide payment information and policies.
    """
    try:
        payment_info = f"""At {settings.clinic.name}, all payments are processed at our clinic for your security and convenience.

We accept:
{chr(10).join(f"• {method}" for method in settings.clinic.payment_methods)}

Consultation fees vary by service and are payable when you visit. We work with most dental insurance providers and offer payment plans for major procedures. Plus, we have special offers for new patients!"""
        
        tool_logger.log_tool_execution("get_payment_info", {}, "Payment info retrieved")
        return payment_info
        
    except Exception as e:
        tool_logger.logger.error(f"Error getting payment info: {e}", exc_info=True)
        return "I apologize, but I'm having trouble retrieving payment information right now."

@function_tool()
async def search_web(context: RunContext, query: str) -> str:
    """
    Search for dental health information when needed.
    """
    try:
        # Sanitize query
        from validators import InputSanitizer
        safe_query = InputSanitizer.sanitize_text(query, max_length=200)
        
        search = DuckDuckGoSearchRun()
        results = search.run(safe_query)
        
        tool_logger.log_tool_execution(
            "search_web",
            {"query": safe_query},
            f"Search completed for: {safe_query[:50]}..."
        )
        
        return results
        
    except Exception as e:
        tool_logger.logger.error(f"Search error: {e}", exc_info=True)
        return "I apologize, but I'm having trouble finding that information right now. Please consult with our dental professionals for specific medical advice."

@function_tool()
async def get_clinic_stats(context: RunContext) -> str:
    """
    Get comprehensive clinic statistics and analytics.
    """
    try:
        stats = await db_manager.get_clinic_stats()
        
        stats_text = f"""📊 {settings.clinic.name} Statistics:

📈 Total Appointments: {stats['total_appointments']}
✅ Completed Appointments: {stats['completed_appointments']}
💰 Total Revenue: €{stats['total_revenue']:.2f}
👥 Unique Patients: {stats['unique_patients']}

📅 Today's Appointments: {stats['today_appointments']}
💸 Today's Revenue: €{stats['today_revenue']:.2f}

📞 Pending Follow-ups: {stats['pending_follow_ups']}

These statistics help us improve our service and patient care."""
        
        tool_logger.log_tool_execution("get_clinic_stats", {}, "Stats retrieved")
        return stats_text
        
    except Exception as e:
        tool_logger.logger.error(f"Error getting clinic stats: {e}", exc_info=True)
        return "I apologize, but I'm having trouble retrieving statistics right now."
