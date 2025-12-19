import styles from './OppositionAgent.module.scss';

interface OppositionAgentProps {
  name: string;
  isSpeaking: boolean;
}

export function OppositionAgent({ name, isSpeaking }: OppositionAgentProps) {
  return (
    <div className={`${styles.agent} ${isSpeaking ? styles.speaking : ''}`}>
      <div className={styles.diamond}>
        <span className={styles.initial}>{name.charAt(0)}</span>
      </div>
      <div className={styles.nameTag}>{name}</div>
      {isSpeaking && (
        <div className={styles.speakingIndicator}>
          <span />
          <span />
          <span />
        </div>
      )}
    </div>
  );
}

