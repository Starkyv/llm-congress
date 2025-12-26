import { useState, useEffect, useRef } from "react";
import { useDebateStore } from "../../store/debateStore";
import DebateIcon from "@/assets/icons/debate.svg?url";
import { ArenaTable } from "../../components/ArenaTable";
import { VotingResultModal } from "../../components/VotingResultModal";
import styles from "./Arena.module.scss";

function Arena() {
  const {
    topic,
    duration,
    isDebating,
    phase,
    startDebate,
    stopDebateStream,
    eventQueue,
    isPaused,
    skipCurrentEvent,
    togglePause,
    votingResultModal,
    closeVotingResultModal,
  } = useDebateStore();
  const [remainingSeconds, setRemainingSeconds] = useState(duration * 60);
  const hasStartedRef = useRef(false);

  // Start debate when component mounts (if topic is set)
  useEffect(() => {
    if (topic && !isDebating && !hasStartedRef.current) {
      hasStartedRef.current = true;
      startDebate();
    }

    // Cleanup: stop debate when leaving the page
    // return () => {
    //   if (isDebating) {
    //     stopDebateStream();
    //   }
    // };
  }, [topic, isDebating, startDebate, stopDebateStream]);

  useEffect(() => {
    if (remainingSeconds <= 0) return;

    const interval = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [remainingSeconds]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  return (
    <div className={styles.arena}>
      <div className={styles.header}>
        <div className={styles.topicSection}>
          <img src={DebateIcon} alt="Debate" className={styles.icon} />
          <span className={styles.topicText}>
            {topic || "The topic goes here"}
          </span>
          {isDebating && <span className={styles.liveIndicator}>LIVE</span>}
          {isDebating && (
            <span className={styles.phaseIndicator}>
              {phase === "debating" ? "DEBATING" : "VOTING"}
            </span>
          )}
        </div>
        <div className={styles.controlsSection}>
          {isDebating && eventQueue.length > 0 && (
            <div className={styles.queueInfo}>
              <span className={styles.queueCount}>
                {eventQueue.length} queued
              </span>
            </div>
          )}
          {/* {isDebating && (
            <div className={styles.controlButtons}>
              <button
                className={styles.controlButton}
                onClick={togglePause}
                title={isPaused ? "Resume" : "Pause"}
              >
                {isPaused ? "▶" : "⏸"}
              </button>
              <button
                className={styles.controlButton}
                onClick={skipCurrentMessage}
                disabled={messageQueue.length === 0}
                title="Skip to next message"
              >
                ⏭
              </button>
            </div>
          )} */}
          {/* <div className={styles.timerSection}>
            <span className={styles.timer}>{formatTime(remainingSeconds)}</span>
          </div> */}
        </div>
      </div>

      <div className={styles.middleSpace}>
        <ArenaTable />
      </div>
      <VotingResultModal
        agentName={votingResultModal.agentName}
        decision={votingResultModal.decision || "stay"}
        inVotes={votingResultModal.inVotes}
        outVotes={votingResultModal.outVotes}
        totalVotes={votingResultModal.totalVotes}
        isOpen={votingResultModal.isOpen}
        onClose={closeVotingResultModal}
        newAgentName={votingResultModal.newAgentName}
        reason={votingResultModal.reason}
      />
    </div>
  );
}

export default Arena;
