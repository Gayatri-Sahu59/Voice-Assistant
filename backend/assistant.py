
from datetime import date

from pipecat.adapters.llm.schemas.function_schema import FunctionSchema
from pipecat.services.llm_service import FunctionCallParams

from backend.appointments import (
    check_doctor_availability as check_availability,
    book_appointment as save_appointment,
    cancel_appointment as remove_appointment
)


TODAY = date.today().isoformat()


SYSTEM_INSTRUCTION = f"""
You are NexovAI Doctor Assistant, a friendly voice-based
doctor appointment booking assistant.

Today's date is {TODAY}.

YOUR RESPONSIBILITIES:
1. Help patients find doctors by speciality.
2. Check available appointment dates and time slots.
3. Book appointments.
4. Cancel appointments.

GENERAL RULES:
- Speak politely using simple English.
- Ask for missing information before taking action.
- Never invent doctors, dates or available time slots.
- Always use the availability tool before booking.
- Never accept a past appointment date.
- If the patient gives a past date, politely ask for a future date.
- Never change AM to PM or PM to AM.
- If the requested time is unclear, ask the patient to clarify.
- Clearly communicate booking and cancellation results.
- Never claim an action succeeded unless its tool confirms it.

BOOKING RULES:
1. Collect the patient's full name.
2. Collect the complete phone number.
3. Read the entire phone number back digit by digit.
4. Ask: "Is this phone number correct?"
5. Wait for the patient's explicit YES.
6. If the patient says NO, ask for the correct number
   and repeat the confirmation process.
7. Do not call book_appointment before explicit confirmation.
8. Before booking, confirm the doctor, date and time.
9. Call the booking tool only after all required details
   have been collected and confirmed.
10. Tell the patient the actual result returned by the tool.

CANCELLATION RULES:
1. Collect the patient's phone number.
2. Collect the appointment ID.
3. Read the complete phone number back digit by digit.
4. Ask for explicit YES confirmation.
5. If the patient says NO, do not cancel.
6. Do not call cancel_appointment before confirmation.
7. Tell the patient the actual result returned by the tool.

IMPORTANT:
Never assume that silence means confirmation.
Never treat a question or uncertain response as YES.
"""


def validate_appointment_date(date_string):
    try:
        appointment_date = date.fromisoformat(date_string)
    except (ValueError, TypeError):
        return False, "Invalid date. Please provide a date in YYYY-MM-DD format."

    if appointment_date < date.today():
        return False, "This date is in the past. Please choose a future date."

    return True, "Valid date."


# Tool 1: Check doctor availability
async def check_doctor_availability(params: FunctionCallParams):

    arguments = params.arguments

    is_valid, message = validate_appointment_date(
        arguments["date"]
    )

    if not is_valid:
        await params.result_callback({
            "success": False,
            "message": message
        })
        return

    result = check_availability(
        arguments["speciality"],
        arguments["date"]
    )

    await params.result_callback(result)


# Tool 2: Book appointment
async def book_appointment(params: FunctionCallParams):

    arguments = params.arguments

    is_valid, message = validate_appointment_date(
        arguments["date"]
    )

    if not is_valid:
        await params.result_callback({
            "success": False,
            "message": message
        })
        return

    result = save_appointment(
        doctor_id=arguments["doctor_id"],
        date=arguments["date"],
        time=arguments["time"],
        patient_name=arguments["patient_name"],
        phone_number=arguments["phone_number"]
    )

    await params.result_callback(result)


# Tool 3: Cancel appointment
async def cancel_appointment(params: FunctionCallParams):

    arguments = params.arguments

    result = remove_appointment(
        phone_number=arguments["phone_number"],
        appointment_id=arguments["appointment_id"]
    )

    await params.result_callback(result)


# Register appointment tools
DOCTOR_ASSISTANT_TOOLS = [

    FunctionSchema(
        name="check_doctor_availability",
        description=(
            "Check available doctors and appointment slots "
            "for a speciality and a date that is today or in the future."
        ),
        properties={
            "speciality": {
                "type": "string",
                "description": "Doctor speciality."
            },
            "date": {
                "type": "string",
                "description": "Date in YYYY-MM-DD format. Must not be in the past."
            }
        },
        required=["speciality", "date"],
        handler=check_doctor_availability
    ),

    FunctionSchema(
        name="book_appointment",
        description=(
            "Book an appointment only after collecting the patient's "
            "full name and phone number, reading the complete phone "
            "number digit by digit, receiving an explicit YES, and "
            "confirming the doctor, date and time."
        ),
        properties={
            "doctor_id": {
                "type": "integer",
                "description": "Selected doctor ID."
            },
            "date": {
                "type": "string",
                "description": "Appointment date in YYYY-MM-DD format."
            },
            "time": {
                "type": "string",
                "description": "Exact selected appointment time, including AM or PM."
            },
            "patient_name": {
                "type": "string",
                "description": "Patient's full name."
            },
            "phone_number": {
                "type": "string",
                "description": "Patient's confirmed complete phone number."
            }
        },
        required=[
            "doctor_id",
            "date",
            "time",
            "patient_name",
            "phone_number"
        ],
        handler=book_appointment
    ),

    FunctionSchema(
        name="cancel_appointment",
        description=(
            "Cancel an appointment only after collecting the phone "
            "number and appointment ID, reading the phone number "
            "digit by digit, and receiving explicit YES confirmation."
        ),
        properties={
            "phone_number": {
                "type": "string",
                "description": "Patient's confirmed phone number."
            },
            "appointment_id": {
                "type": "integer",
                "description": "Appointment ID to cancel."
            }
        },
        required=["phone_number", "appointment_id"],
        handler=cancel_appointment
    )

]
