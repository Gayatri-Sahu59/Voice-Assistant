
from datetime import date as current_date
import re

from backend.data import doctors, appointments


# Validate appointment date
def validate_date(date_string):

    try:
        appointment_date = current_date.fromisoformat(date_string)
    except (ValueError, TypeError):
        return False

    return appointment_date >= current_date.today()


# Validate Indian mobile number (10 digits)
def validate_phone_number(phone_number):

    if not isinstance(phone_number, str):
        return False

    return bool(re.fullmatch(r"[6-9]\d{9}", phone_number.strip()))


# Check available doctors and their slots
def check_doctor_availability(speciality, date):

    if not validate_date(date):
        return {
            "success": False,
            "message": "Invalid or past date. Please choose today or a future date."
        }

    available_doctors = []

    for doctor in doctors:

        if doctor["speciality"].lower() == speciality.strip().lower():

            booked_slots = [
                appointment["time"]
                for appointment in appointments
                if appointment["doctor_id"] == doctor["id"]
                and appointment["date"] == date
            ]

            available_slots = [
                slot for slot in doctor["slots"]
                if slot not in booked_slots
            ]

            available_doctors.append({
                "doctor_id": doctor["id"],
                "doctor_name": doctor["name"],
                "speciality": doctor["speciality"],
                "available_slots": available_slots
            })

    if not available_doctors:
        return {
            "success": False,
            "message": "No doctors found for this speciality."
        }

    return {
        "success": True,
        "doctors": available_doctors
    }


# Book an appointment
def book_appointment(doctor_id, date, time, patient_name, phone_number):

    # Validate required details
    if not isinstance(patient_name, str) or not patient_name.strip():
        return {
            "success": False,
            "message": "Please provide the patient's full name."
        }

    if not validate_phone_number(phone_number):
        return {
            "success": False,
            "message": "Please provide a valid 10-digit Indian mobile number."
        }

    if not validate_date(date):
        return {
            "success": False,
            "message": "Invalid or past date. Please choose today or a future date."
        }

    # Find doctor
    doctor = next(
        (d for d in doctors if d["id"] == doctor_id),
        None
    )

    if doctor is None:
        return {
            "success": False,
            "message": "Doctor not found."
        }

    # Validate selected slot
    if time not in doctor["slots"]:
        return {
            "success": False,
            "message": "Invalid time slot."
        }

    # Check whether slot is already booked
    for appointment in appointments:

        if (
            appointment["doctor_id"] == doctor_id
            and appointment["date"] == date
            and appointment["time"] == time
        ):
            return {
                "success": False,
                "message": "This slot is already booked. Please select another slot."
            }

    # Generate a unique appointment ID
    new_id = max(
        (appointment["id"] for appointment in appointments),
        default=0
    ) + 1

    # Create appointment
    new_appointment = {
        "id": new_id,
        "doctor_id": doctor_id,
        "doctor_name": doctor["name"],
        "date": date,
        "time": time,
        "patient_name": patient_name.strip(),
        "phone_number": phone_number.strip()
    }

    appointments.append(new_appointment)

    return {
        "success": True,
        "message": "Appointment booked successfully.",
        "appointment": new_appointment
    }


# Cancel an appointment
def cancel_appointment(phone_number, appointment_id):

    if not validate_phone_number(phone_number):
        return {
            "success": False,
            "message": "Please provide a valid 10-digit Indian mobile number."
        }

    for appointment in appointments:

        if (
            appointment["phone_number"] == phone_number.strip()
            and appointment["id"] == appointment_id
        ):

            appointments.remove(appointment)

            return {
                "success": True,
                "message": "Appointment cancelled successfully.",
                "appointment_id": appointment_id
            }

    return {
        "success": False,
        "message": "No appointment found with this phone number and appointment ID."
    }
