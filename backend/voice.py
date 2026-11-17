
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.transports.base_transport import TransportParams

from pipecat.services.elevenlabs.stt import ElevenLabsRealtimeSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.llm import GoogleLLMService

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair
)

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams

from backend.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID
)

from backend.assistant import SYSTEM_INSTRUCTION, DOCTOR_ASSISTANT_TOOLS


def create_voice_pipeline(webrtc_connection):

    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is missing")

    if not ELEVENLABS_API_KEY:
        raise ValueError("ElevenLabs API key is missing")

    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True
        )
    )

    # Speech to Text
    stt = ElevenLabsRealtimeSTTService(
        api_key=ELEVENLABS_API_KEY
    )

    # Gemini LLM
    llm = GoogleLLMService(
        api_key=GEMINI_API_KEY,
        settings=GoogleLLMService.Settings(
            model=GEMINI_MODEL,
            system_instruction=SYSTEM_INSTRUCTION
        )
    )

    # Text to Speech
    tts = ElevenLabsTTSService(
        api_key=ELEVENLABS_API_KEY,
        voice_id=ELEVENLABS_VOICE_ID
    )

    context = LLMContext(
        tools=DOCTOR_ASSISTANT_TOOLS
    )

    user_aggregator, assistant_aggregator = (
        LLMContextAggregatorPair(context)
    )

    pipeline = Pipeline([
        transport.input(),
        stt,
        user_aggregator,
        llm,
        tts,
        transport.output(),
        assistant_aggregator
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000
        )
    )

    return transport, task, context
