import { useState, useCallback, useRef } from "react";
import { streamDebate, stopDebate } from "./services/debateStream";
import { SSEEvent } from "./types/debate";
import "./App.scss";

interface EventLog {
  id: number;
  timestamp: Date;
  event: string;
  data: any;
}

function App() {
  const [events, setEvents] = useState<EventLog[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [topic, setTopic] = useState("");
  const [duration, setDuration] = useState(300);
  const cancelStreamRef = useRef<(() => void) | null>(null);
  const eventIdRef = useRef(0);

  const handleEvent = useCallback((event: SSEEvent) => {
    const newEvent: EventLog = {
      id: eventIdRef.current++,
      timestamp: new Date(),
      event: event.event,
      data: event.data,
    };
    setEvents((prev) => [...prev, newEvent]);
  }, []);

  const handleStart = useCallback(async () => {
    if (!topic.trim()) return;

    setEvents([]);
    eventIdRef.current = 0;
    setIsRunning(true);

    const cancel = await streamDebate(
      topic,
      duration,
      handleEvent,
      () => {
        setIsRunning(false);
      },
      (error) => {
        console.error("Stream error:", error);
        setIsRunning(false);
      }
    );

    cancelStreamRef.current = cancel;
  }, [topic, duration, handleEvent]);

  const handleStop = useCallback(async () => {
    if (cancelStreamRef.current) {
      cancelStreamRef.current();
      cancelStreamRef.current = null;
    }

    try {
      await stopDebate();
    } catch (error) {
      console.error("Failed to stop debate:", error);
    }

    setIsRunning(false);
  }, []);

  return (
    <div className="app">
      <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
        <h1>Event Stream</h1>
        
        <div style={{ marginBottom: "20px", display: "flex", gap: "10px", alignItems: "center" }}>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter debate topic"
            disabled={isRunning}
            style={{ flex: 1, padding: "8px", fontSize: "14px" }}
          />
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            placeholder="Duration (seconds)"
            disabled={isRunning}
            style={{ width: "150px", padding: "8px", fontSize: "14px" }}
          />
          {!isRunning ? (
            <button onClick={handleStart} style={{ padding: "8px 16px", fontSize: "14px" }}>
              Start
            </button>
          ) : (
            <button onClick={handleStop} style={{ padding: "8px 16px", fontSize: "14px" }}>
              Stop
            </button>
          )}
        </div>

        <div style={{ border: "1px solid #ccc", borderRadius: "4px", padding: "10px", maxHeight: "70vh", overflowY: "auto" }}>
          {events.length === 0 ? (
            <p style={{ color: "#666", textAlign: "center", padding: "20px" }}>
              No events yet. Start a debate to see events stream in.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {events.map((event) => (
                <div
                  key={event.id}
                  style={{
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                    padding: "10px",
                    backgroundColor: "#f9f9f9",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "5px" }}>
                    <strong style={{ color: "#333" }}>{event.event}</strong>
                    <span style={{ color: "#666", fontSize: "12px" }}>
                      {event.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <pre
                    style={{
                      margin: 0,
                      fontSize: "12px",
                      color: "#555",
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                    }}
                  >
                    {JSON.stringify(event.data, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
