import styles from './Timer.module.scss';

interface TimerProps {
  elapsedSeconds: number;
  remainingSeconds: number;
  roundNumber: number;
  phase: string;
}

export function Timer({
  elapsedSeconds,
  remainingSeconds,
  roundNumber,
  phase,
}: TimerProps) {
  // Ensure values are numbers and handle NaN/undefined
  const safeElapsed = Number(elapsedSeconds) || 0;
  const safeRemaining = Number(remainingSeconds) || 0;
  const safeRound = Number(roundNumber) || 1;

  const formatTime = (seconds: number): string => {
    const safeSeconds = Number(seconds) || 0;
    const mins = Math.floor(safeSeconds / 60);
    const secs = safeSeconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getPhaseLabel = (phase: string): string => {
    switch (phase) {
      case 'debating':
        return 'Debating';
      case 'voting':
        return 'Voting';
      case 'switching':
        return 'Switching';
      case 'complete':
        return 'Complete';
      default:
        return 'Ready';
    }
  };

  const totalDuration = safeElapsed + safeRemaining;
  const progress = totalDuration > 0 ? (safeElapsed / totalDuration) * 100 : 0;

  return (
    <div className={styles.timer}>
      <div className={styles.progressBar}>
        <div
          className={styles.progressFill}
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className={styles.info}>
        <div className={styles.time}>
          <span className={styles.elapsed}>{formatTime(safeElapsed)}</span>
          <span className={styles.separator}>/</span>
          <span className={styles.total}>{formatTime(totalDuration)}</span>
        </div>
        <div className={styles.meta}>
          <span className={`${styles.phase} ${styles[phase]}`}>
            {getPhaseLabel(phase)}
          </span>
          <span className={styles.round}>Round {safeRound}</span>
        </div>
      </div>
    </div>
  );
}

