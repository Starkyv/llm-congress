import { SpeechBubble } from '../SpeechBubble';
import styles from './PropositionAgent.module.scss';

interface PropositionAgentProps {
  id: string;
  name: string;
  isActive: boolean;
  isSpeaking: boolean;
  voteStatus?: 'in' | 'out' | null;
  streamingContent?: string;
  angle: number; // Position on the circle in degrees
  radius: number; // Distance from center
}

export function PropositionAgent({
  name,
  isActive,
  isSpeaking,
  voteStatus,
  streamingContent,
  angle,
  radius,
}: PropositionAgentProps) {
  console.log('streamingContent', streamingContent);
  // Convert angle to radians and calculate position
  const radian = (angle - 90) * (Math.PI / 180); // -90 to start from top
  const x = Math.cos(radian) * radius;
  const y = Math.sin(radian) * radius;

  const getStatusClass = () => {
    if (voteStatus === 'in') return styles.voteIn;
    if (voteStatus === 'out') return styles.voteOut;
    if (isActive) return styles.active;
    return '';
  };

  // Determine speech bubble position based on angle
  const getBubblePosition = (): 'left' | 'right' | 'top' | 'bottom' => {
    // Normalize angle to 0-360
    const normalizedAngle = ((angle % 360) + 360) % 360;
    
    // Right side (0-90 and 270-360)
    if (normalizedAngle <= 90 || normalizedAngle >= 270) {
      return 'right';
    }
    // Left side (90-270)
    if (normalizedAngle > 90 && normalizedAngle < 270) {
      return 'left';
    }
    return 'right';
  };

  const bubblePosition = getBubblePosition();

  return (
    <div
      className={`${styles.agent} ${getStatusClass()} ${
        isSpeaking ? styles.speaking : ''
      }`}
      style={{
        transform: `translate(${x}px, ${y}px)`,
      }}
    >
      <div className={styles.circle}>
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
      
      {/* Speech bubble with Streamdown */}
      {streamingContent && (
        <div className={styles.speechBubbleWrapper}>
          <SpeechBubble
            content={streamingContent}
            agentName={name}
            role="proposition"
            position={bubblePosition}
            isStreaming={true}
          />
        </div>
      )}
    </div>
  );
}



