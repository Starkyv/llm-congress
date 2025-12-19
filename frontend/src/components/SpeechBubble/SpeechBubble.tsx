import { Streamdown } from 'streamdown';
import styles from './SpeechBubble.module.scss';

interface SpeechBubbleProps {
  content: string;
  agentName: string;
  role: 'proposition' | 'opposition';
  position?: 'left' | 'right' | 'top' | 'bottom';
  isStreaming?: boolean;
}

export function SpeechBubble({
  content,
  agentName,
  role,
  position = 'right',
  isStreaming = false,
}: SpeechBubbleProps) {
  if (!content) return null;

  return (
    <div
      className={`${styles.bubble} ${styles[role]} ${styles[position]} ${
        isStreaming ? styles.streaming : ''
      }`}
    >
      <div className={styles.header}>
        <span className={styles.name}>{agentName}</span>
        {isStreaming && <span className={styles.indicator} />}
      </div>
      <div className={styles.content}>
        <Streamdown>{content}</Streamdown>
      </div>
    </div>
  );
}

