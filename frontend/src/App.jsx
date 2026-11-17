
import { useEffect, useState } from "react";
import "./App.css";
import VoiceAssistant from "./VoiceAssistant";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [form, setForm] = useState({
    doctor_id: "",
    date: "",
    time: "",
    patient_name: "",
    phone_number: "",
  });

  const [submitting, setSubmitting] = useState(false);

  // Fetch doctors and appointments from backend
  const fetchData = async () => {
    setError("");

    try {
      const [doctorResponse, appointmentResponse] =
        await Promise.all([
          fetch(`${API_URL}/doctors`),
          fetch(`${API_URL}/appointments`),
        ]);

      if (!doctorResponse.ok || !appointmentResponse.ok) {
        throw new Error("Backend API request failed.");
      }

      const doctorData = await doctorResponse.json();
      const appointmentData = await appointmentResponse.json();

      if (!Array.isArray(doctorData) || !Array.isArray(appointmentData)) {
        throw new Error("Unexpected data received from backend.");
      }

      setDoctors(doctorData);
      setAppointments(appointmentData);

      console.log("Doctors received:", doctorData);
      console.log("Appointments received:", appointmentData);
    } catch (err) {
      console.error("Backend connection error:", err);
      setError(
        "Unable to connect to backend. Please check whether FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Handle form field changes
  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
      ...(name === "doctor_id" || name === "date" ? { time: "" } : {}),
    }));

    setMessage("");
  };

  // Get selected doctor's available slots
  const selectedDoctor = doctors.find(
    (doctor) => String(doctor.id) === form.doctor_id
  );

  const availableSlots = selectedDoctor?.slots || [];

  // Book appointment
  const handleBooking = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");

    if (!form.doctor_id || !form.date || !form.time) {
      setMessage("Please select a doctor, date and time.");
      return;
    }

    try {
      setSubmitting(true);

      const response = await fetch(`${API_URL}/appointments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          doctor_id: Number(form.doctor_id),
        }),
      });

      const result = await response.json();

      if (!response.ok || result.success === false) {
        throw new Error(result.message || "Appointment booking failed.");
      }

      setMessage(result.message || "Appointment booked successfully!");

      setForm({
        doctor_id: "",
        date: "",
        time: "",
        patient_name: "",
        phone_number: "",
      });

      await fetchData();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // Cancel appointment
  const handleCancellation = async (appointmentId) => {
    const phoneNumber = window.prompt(
      "Enter the phone number used for this appointment:"
    );

    if (!phoneNumber) return;

    const confirmed = window.confirm(
      "Are you sure you want to cancel this appointment?"
    );

    if (!confirmed) return;

    setMessage("");
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/appointments/${appointmentId}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            phone_number: phoneNumber,
          }),
        }
      );

      const result = await response.json();

      if (!response.ok || result.success === false) {
        throw new Error(result.message || "Cancellation failed.");
      }

      setMessage(result.message || "Appointment cancelled successfully!");

      await fetchData();
    } catch (err) {
      setMessage(err.message);
    }
  };

  const getDoctorName = (appointment) => {
    if (appointment.doctor_name) return appointment.doctor_name;

    const doctor = doctors.find(
      (item) => item.id === appointment.doctor_id
    );

    return doctor ? doctor.name : "Doctor";
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div>
            <h1>NexovAI</h1>
            <p>Doctor Appointment Assistant</p>
          </div>
        </div>
      </header>

      <main className="container">
        <section className="welcome">
          <p className="eyebrow">YOUR HEALTH, OUR PRIORITY</p>
          <h2>Welcome to NexovAI</h2>
          <p>
            Find doctors, check available slots and manage your
            appointments in one place.
          </p>
        </section>

        {error && <div className="alert error">{error}</div>}
        {message && <div className="alert success">{message}</div>}

        <section className="stats">
          <div className="stat-card">
            <span>Available Doctors</span>
            <h2>{loading ? "..." : doctors.length}</h2>
          </div>

          <div className="stat-card">
            <span>Total Appointments</span>
            <h2>{loading ? "..." : appointments.length}</h2>
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">OUR MEDICAL TEAM</p>
              <h2>Available Doctors</h2>
            </div>
          </div>

          {loading ? (
            <p className="info-text">Loading doctors...</p>
          ) : doctors.length === 0 ? (
            <p className="info-text">No doctors found.</p>
          ) : (
            <div className="doctor-grid">
              {doctors.map((doctor) => (
                <div className="doctor-card" key={doctor.id}>
                  <div className="doctor-icon">+</div>
                  <h3>{doctor.name}</h3>
                  <p className="speciality">{doctor.speciality}</p>

                  <h4>Available Slots</h4>

                  <div className="slots">
                    {doctor.slots?.length > 0 ? (
                      doctor.slots.map((slot) => (
                        <span key={slot}>{slot}</span>
                      ))
                    ) : (
                      <span>No slots available</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="section booking-section">
          <p className="eyebrow">BOOK A VISIT</p>
          <h2>Book an Appointment</h2>

          <form className="booking-form" onSubmit={handleBooking}>
            <div className="form-group">
              <label>Patient Name</label>
              <input
                type="text"
                name="patient_name"
                value={form.patient_name}
                onChange={handleChange}
                placeholder="Enter your full name"
                required
              />
            </div>

            <div className="form-group">
              <label>Phone Number</label>
              <input
                type="tel"
                name="phone_number"
                value={form.phone_number}
                onChange={handleChange}
                placeholder="Enter your phone number"
                pattern="[0-9]{10}"
                title="Enter a 10-digit phone number"
                required
              />
            </div>

            <div className="form-group">
              <label>Select Doctor</label>
              <select
                name="doctor_id"
                value={form.doctor_id}
                onChange={handleChange}
                required
              >
                <option value="">Choose a doctor</option>

                {doctors.map((doctor) => (
                  <option key={doctor.id} value={doctor.id}>
                    {doctor.name} - {doctor.speciality}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Appointment Date</label>
              <input
                type="date"
                name="date"
                value={form.date}
                onChange={handleChange}
                min={new Date().toISOString().split("T")[0]}
                required
              />
            </div>

            <div className="form-group full-width">
              <label>Select Time Slot</label>
              <select
                name="time"
                value={form.time}
                onChange={handleChange}
                disabled={!selectedDoctor}
                required
              >
                <option value="">Choose a time slot</option>

                {availableSlots.map((slot) => (
                  <option key={slot} value={slot}>
                    {slot}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="primary-button full-width"
              type="submit"
              disabled={submitting || loading}
            >
              {submitting ? "Booking..." : "Book Appointment"}
            </button>
          </form>
        </section>


        <VoiceAssistant />

        <section className="section">
          <p className="eyebrow">YOUR BOOKINGS</p>
          <h2>Appointments</h2>

          {loading ? (
            <p className="info-text">Loading appointments...</p>
          ) : appointments.length === 0 ? (
            <div className="empty-state">
              <h3>No appointments yet</h3>
              <p>Your booked appointments will appear here.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Phone</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>
                  {appointments.map((appointment) => (
                    <tr key={appointment.id}>
                      <td>{appointment.patient_name}</td>
                      <td>{getDoctorName(appointment)}</td>
                      <td>{appointment.date}</td>
                      <td>{appointment.time}</td>
                      <td>{appointment.phone_number}</td>
                      <td>
                        <button
                          className="cancel-button"
                          onClick={() =>
                            handleCancellation(appointment.id)
                          }
                        >
                          Cancel
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>NexovAI Doctor Assistant | Voice-based Appointment System</p>
      </footer>
    </div>
  );
}

export default App;
