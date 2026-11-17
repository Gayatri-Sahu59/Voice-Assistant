
import { useRef, useState } from "react";
import { PipecatClient } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";
import "./VoiceAssistant.css";

const API_URL = "http://127.0.0.1:8000";

function VoiceAssistant() {
  const clientRef = useRef(null);
  const audioRef = useRef(null);

  const [status, setStatus] = useState("Disconnected");
  const [transcripts, setTranscripts] = useState([]);
  const [error, setError] = useState("");

  const addTranscript = (speaker, text) => {
    if (!text) return;

    setTranscripts((previous) => [
      ...previous,
      { speaker, text }
    ]);
  };

  const startCall = async () => {
    try {
      setError("");
      setStatus("Connecting...");

      const client = new PipecatClient({
        transport: new SmallWebRTCTransport(),
        enableMic: true,
        enableCam: false,

        callbacks: {
          onConnected: () => {
            setStatus("Connected");
          },

          onDisconnected: () => {
            setStatus("Disconnected");

            if (audioRef.current) {
              audioRef.current.pause();
              audioRef.current.srcObject = null;
            }
          },

          onTransportStateChanged: (state) => {
            setStatus(String(state));
          },

          // Receive and play assistant audio
          onTrackStarted: (track, participant) => {
            if (track.kind !== "audio" || participant?.local) {
              return;
            }

            console.log("Assistant audio track received");

            if (audioRef.current) {
              audioRef.current.srcObject =
                new MediaStream([track]);

              audioRef.current.play().catch((err) => {
                console.error("Audio playback failed:", err);
                setError("Browser could not play assistant audio.");
              });
            }
          },

          onUserTranscript: (data) => {
  console.log("User transcript received:", data);

  if (data.final && data.text) {
    addTranscript("You", data.text);
  }
},

          onBotOutput: (data) => {
            if (
              data.will_be_spoken &&
              data.spoken_status === "completed"
            ) {
              addTranscript("Assistant", data.text);
            }
          },

          onError: (message) => {
            console.error("Pipecat error:", message);

            setError(
              message?.data?.error ||
              message?.message ||
              "Voice connection error"
            );
          }
        }
      });

      clientRef.current = client;

      await client.connect({
        webrtcRequestParams: {
          endpoint: `${API_URL}/api/offer`
        }
      });

    } catch (err) {
      console.error("Voice connection failed:", err);

      setError(err.message || "Unable to connect");
      setStatus("Disconnected");
      clientRef.current = null;
    }
  };

  const endCall = async () => {
    try {
      if (clientRef.current) {
        await clientRef.current.disconnect();
        clientRef.current = null;
      }

      setStatus("Disconnected");

    } catch (err) {
      console.error("Error ending call:", err);
      setError("Unable to end the call properly.");
    }
  };

  return (
    <section className="voice-section">
      <h2>Voice Doctor Assistant</h2>

      <p>
        Status: <strong>{status}</strong>
      </p>

      <div className="voice-buttons">
        <button
          onClick={startCall}
          disabled={status !== "Disconnected"}
        >
          Start Call
        </button>

        <button
          onClick={endCall}
          disabled={!clientRef.current}
        >
          End Call
        </button>
      </div>

      {error && <p className="voice-error">{error}</p>}

      {/* Assistant audio player */}
      <audio ref={audioRef} autoPlay />

      <div className="transcript-box">
        <h3>Live Conversation</h3>

        {transcripts.length === 0 ? (
          <p>Your conversation will appear here.</p>
        ) : (
          transcripts.map((item, index) => (
            <p key={index}>
              <strong>{item.speaker}:</strong> {item.text}
            </p>
          ))
        )}
      </div>
    </section>
  );
}

export default VoiceAssistant;
