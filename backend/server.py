
import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.runner import PipelineRunner

from pipecat.transports.smallwebrtc.request_handler import (
    SmallWebRTCRequest,
    SmallWebRTCPatchRequest,
    SmallWebRTCRequestHandler,
    IceCandidate,
)

from backend.data import doctors, appointments
from backend.appointments import book_appointment, cancel_appointment
from backend.voice import create_voice_pipeline


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(title="NexovAI Doctor Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# WebRTC session management
# --------------------------------------------------

webrtc_handler = SmallWebRTCRequestHandler()
active_sessions = {}


# --------------------------------------------------
# Request models
# --------------------------------------------------

class AppointmentRequest(BaseModel):
    doctor_id: int
    date: str
    time: str
    patient_name: str
    phone_number: str


class CancellationRequest(BaseModel):
    phone_number: str


# --------------------------------------------------
# Basic API routes
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "NexovAI Doctor Assistant API is running"
    }


@app.get("/doctors")
def get_doctors():
    return doctors


@app.get("/appointments")
def get_appointments():
    return appointments


# --------------------------------------------------
# Appointment booking
# --------------------------------------------------

@app.post("/appointments")
def create_appointment(request: AppointmentRequest):

    result = book_appointment(
        doctor_id=request.doctor_id,
        date=request.date,
        time=request.time,
        patient_name=request.patient_name,
        phone_number=request.phone_number,
    )

    return result


# --------------------------------------------------
# Appointment cancellation
# --------------------------------------------------

@app.delete("/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    request: CancellationRequest
):

    result = cancel_appointment(
        phone_number=request.phone_number,
        appointment_id=appointment_id,
    )

    return result


# --------------------------------------------------
# WebRTC voice connection
# --------------------------------------------------

@app.post("/api/offer")
async def handle_offer(request: Request):

    body = await request.json()

    webrtc_request = SmallWebRTCRequest(**body)

    async def connection_callback(connection):

        transport, task, context = create_voice_pipeline(connection)

        runner = PipelineRunner()

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):

            print("Voice client connected")

            context.add_message({
                "role": "developer",
                "content": (
                    "Introduce yourself briefly as NexovAI Doctor Assistant. "
                    "Ask the patient how you can help."
                ),
            })

            await task.queue_frames([LLMRunFrame()])

        active_sessions[connection.pc_id] = task

        asyncio.create_task(runner.run(task))

    answer = await webrtc_handler.handle_web_request(
        webrtc_request,
        connection_callback,
    )

    return answer


# --------------------------------------------------
# WebRTC ICE candidate handling
# --------------------------------------------------

@app.patch("/api/offer")
async def handle_offer_patch(request: Request):

    body = await request.json()

    candidates = []

    for item in body.get("candidates", []):

        candidates.append(
            IceCandidate(
                candidate=item.get("candidate", ""),
                sdp_mid=item.get(
                    "sdp_mid",
                    item.get("sdpMid", "")
                ),
                sdp_mline_index=item.get(
                    "sdp_mline_index",
                    item.get("sdpMLineIndex", 0)
                ),
            )
        )

    patch_request = SmallWebRTCPatchRequest(
        pc_id=body["pc_id"],
        candidates=candidates,
    )

    await webrtc_handler.handle_patch_request(patch_request)

    return {
        "status": "ok"
    }
