import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDebateStore } from "../../store/debateStore";
import styles from "./Home.module.scss";
import DebateIcon from "@/assets/icons/debate.svg?url";

function Home() {
  const navigate = useNavigate();
  const { topic, duration, setTopic, setDuration } = useDebateStore();
  const [localTopic, setLocalTopic] = useState(topic);
  const [localDuration, setLocalDuration] = useState(duration.toString());

  const handleStartDebate = () => {
    if (localTopic.trim()) {
      setTopic(localTopic.trim());
      setDuration(parseInt(localDuration, 10) || 3);
      navigate("/arena");
    }
  };

  const handleDurationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value === "" || (!isNaN(Number(value)) && Number(value) > 0)) {
      setLocalDuration(value);
    }
  };

  return (
    <div className={styles.home}>
      <div className={styles.header}>
        <div className={styles.icon}>
          <img src={DebateIcon} alt="Debate Icon" />
        </div>
        <h1 className={styles.title}>Debate Arena</h1>
        {/* <p className={styles.subtitle}>Any subtext goes here</p> */}
      </div>

      <div className={styles.card}>
        <div className={styles.inputGroup}>
          <label className={styles.label}>DEBATE TOPIC</label>
          <input
            type="text"
            className={styles.input}
            placeholder="Enter the topic to debate about"
            value={localTopic}
            onChange={(e) => setLocalTopic(e.target.value)}
          />
        </div>

        <div className={styles.inputGroup}>
          <label className={styles.label}>DURATION (MINUTES)</label>
          <input
            type="number"
            className={styles.input}
            value={localDuration}
            onChange={handleDurationChange}
            min="1"
          />
        </div>

        <button
          className={styles.button}
          onClick={handleStartDebate}
          disabled={!localTopic.trim()}
        >
          Start Debate
        </button>
      </div>
    </div>
  );
}

export default Home;
