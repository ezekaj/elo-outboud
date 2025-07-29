# Simple Configuration for Romi Dental Clinic

class SimpleConfig:
    """Basic configuration for dental outbound calls"""

    # Clinic Information
    CLINIC_NAME = "Romi Dental Clinic"
    CLINIC_LOCATION = "Albania"

    # Call Settings
    MAX_CALLS_PER_HOUR = 30
    CALL_DURATION_LIMIT = 300  # 5 minutes

    # Services Offered
    SERVICES = [
        "Regular check-ups and cleanings",
        "Cosmetic dentistry and whitening",
        "Emergency dental care",
        "Children's dentistry",
        "Dental implants and prosthetics"
    ]

    # Call Hours (24-hour format)
    CALL_HOURS = {
        "monday": [9, 10, 11, 14, 15, 16, 17],
        "tuesday": [9, 10, 11, 14, 15, 16, 17],
        "wednesday": [9, 10, 11, 14, 15, 16, 17],
        "thursday": [9, 10, 11, 14, 15, 16, 17],
        "friday": [9, 10, 11, 14, 15, 16, 17],
        "saturday": [9, 10, 11, 12, 13],
        "sunday": []
    }

    # Payment Information
    PAYMENT_METHODS = ["Cash (Euro)", "Credit Cards", "Debit Cards", "Bank Transfers"]
    PAYMENT_POLICY = "All payments made at clinic for security"

# Simple data storage for the clinic
clinic_stats = {
    "total_calls": 0,
    "appointments_booked": 0,
    "revenue_generated": 0.0
}

def log_call_outcome(outcome: str, revenue: float = 0.0):
    """Simple function to track call outcomes"""
    clinic_stats["total_calls"] += 1
    if outcome == "appointment_booked":
        clinic_stats["appointments_booked"] += 1
        clinic_stats["revenue_generated"] += revenue

def get_clinic_stats():
    """Get simple clinic statistics"""
    total_calls = clinic_stats["total_calls"]
    conversion_rate = (clinic_stats["appointments_booked"] / total_calls * 100) if total_calls > 0 else 0

    return {
        "total_calls": total_calls,
        "appointments_booked": clinic_stats["appointments_booked"],
        "conversion_rate": f"{conversion_rate:.1f}%",
        "revenue_generated": f"€{clinic_stats['revenue_generated']:.2f}"
    }