
from backend.appointments import (
    check_doctor_availability,
    book_appointment,
    cancel_appointment
)

# 1. Check available doctors
print("AVAILABLE DOCTORS:")
print(check_doctor_availability("Cardiologist", "2026-11-17"))

# 2. Book an appointment
print("\nBOOKING APPOINTMENT:")
result = book_appointment(
    1,
    "2026-11-17",
    "10:00 AM",
    "Rahul",
    "9876543210"
)
print(result)

# 3. Cancel the appointment
print("\nCANCELLING APPOINTMENT:")
cancel_result = cancel_appointment("9876543210", 1)
print(cancel_result)

# 4. Check availability again
print("\nAVAILABILITY AFTER CANCELLATION:")
print(check_doctor_availability("Cardiologist", "2026-11-17"))
