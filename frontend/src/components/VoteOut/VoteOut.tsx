import styles from "./VoteOut.module.scss";

interface VoteOutProps {
  visible?: boolean;
  reasoning?: string;
}

export function VoteOut({ visible = false, reasoning }: VoteOutProps) {
  if (!visible) return null;

  return (
    <div className={styles.voteOut}>
      <div className={styles.marker}>
        <div className={styles.square}>
          <span className={styles.x}>✕</span>
        </div>
        <div className={styles.pin} />
      </div>
      {reasoning && (
        <div className={styles.reasoning}>
          <div className={styles.reasoningContent}>{reasoning}</div>
        </div>
      )}
    </div>
  );
}

