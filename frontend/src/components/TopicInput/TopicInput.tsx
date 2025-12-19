import { useState } from "react";
import styles from "./TopicInput.module.scss";

interface TopicInputProps {
  onStart: (topic: string, duration: number) => void;
  isRunning: boolean;
  onStop?: () => void;
}

export function TopicInput({ onStart, isRunning, onStop }: TopicInputProps) {
  const [topic, setTopic] = useState("");
  const [duration, setDuration] = useState(300);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (topic.trim() && !isRunning) {
      onStart(topic.trim(), duration);
    }
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.inputGroup}>
          <label htmlFor="topic" className={styles.label}>
            Debate Topic
          </label>
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a topic to debate..."
            className={styles.input}
            disabled={isRunning}
          />
        </div>

        <div className={styles.controls}>
          <div className={styles.durationGroup}>
            <label htmlFor="duration" className={styles.label}>
              Duration
            </label>
            <select
              id="duration"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className={styles.select}
              disabled={isRunning}
            >
              <option value={30}>30 seconds</option>
              <option value={60}>1 minute</option>
              <option value={120}>2 minutes</option>
              <option value={300}>5 minutes</option>
              <option value={600}>10 minutes</option>
              <option value={900}>15 minutes</option>
            </select>
          </div>

          {isRunning ? (
            <button
              type="button"
              onClick={onStop}
              className={`${styles.button} ${styles.stopButton}`}
            >
              Stop Debate
            </button>
          ) : (
            <button
              type="submit"
              disabled={!topic.trim()}
              className={styles.button}
            >
              Start Debate
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
