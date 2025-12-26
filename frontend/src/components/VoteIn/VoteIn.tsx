import styles from "./VoteIn.module.scss";

interface VoteInProps {
  visible?: boolean;
  reasoning?: string;
}

export function VoteIn({ visible = false, reasoning }: VoteInProps) {
  if (!visible) return null;

  return (
    <div className={styles.voteIn}>
      <div className={styles.marker}>
        <div className={styles.square}>
          <span className={styles.tick}>✓</span>
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

