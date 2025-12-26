import { useEffect } from "react";
import styles from "./VotingResultModal.module.scss";
import TickIcon from "../../assets/icons/tick.svg?url";
import CrossIcon from "../../assets/icons/vote-out.svg?url";

interface VotingResultModalProps {
  agentName: string;
  decision: "stay" | "switch";
  inVotes: number;
  outVotes: number;
  totalVotes: number;
  isOpen: boolean;
  onClose: () => void;
  // For agent_switch events
  newAgentName?: string;
  reason?: string;
}

export function VotingResultModal({
  agentName,
  decision,
  inVotes,
  outVotes,
  totalVotes,
  isOpen,
  onClose,
  newAgentName,
  reason,
}: VotingResultModalProps) {
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const stays = decision === "stay";
  const receivedVotes = stays ? inVotes : outVotes;
  const thresholdReached = receivedVotes > totalVotes / 2;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div
        className={`${styles.modal} ${
          stays ? styles.stayModal : styles.outModal
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.content}>
          <div
            className={`${styles.iconCircle} ${
              stays ? styles.stayIcon : styles.outIcon
            }`}
          >
            {stays ? (
              <img src={TickIcon} alt="Tick" className={styles.checkmark} />
            ) : (
              <img src={CrossIcon} alt="Cross" className={styles.cross} />
            )}
          </div>
          <div
            className={`${styles.heading} ${
              stays ? styles.stayHeading : styles.outHeading
            }`}
          >
            {newAgentName
              ? `${agentName} → ${newAgentName}`
              : `${agentName} ${stays ? "Continues" : "Voted Out"}`}
          </div>
          {reason && (
            <div className={styles.reason}>
              <div className={styles.reasonLabel}>Reason:</div>
              <div className={styles.reasonText}>{reason}</div>
            </div>
          )}
          <div className={styles.voteInfo}>
            <div className={styles.voteCount}>
              <span className={styles.voteText}>
                {agentName} received{" "}
                <span className={stays ? styles.stayNumber : styles.outNumber}>
                  {receivedVotes}
                </span>{" "}
                of{" "}
                <span className={stays ? styles.stayNumber : styles.outNumber}>
                  {totalVotes}
                </span>{" "}
                votes
              </span>
            </div>
            <div className={styles.threshold}>
              {thresholdReached
                ? "Majority threshold reached"
                : "Majority threshold not reached"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
