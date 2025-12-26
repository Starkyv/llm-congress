import { PropositionAgent } from "../PropositionAgent";
import { OppositionAgent } from "../OppositionAgent";
import { SpeechBubble } from "../SpeechBubble";
import { Agent } from "../../types/debate";
import styles from "./DebateArena.module.scss";

interface DebateArenaProps {
  propositionAgents: Agent[];
  oppositionAgent: Agent | null;
  currentSpeaker: string | null;
  currentSpeakerRole: "proposition" | "opposition" | null;
  streamingContent: string;
  activePropositionId: string | null;
}

export function DebateArena({
  propositionAgents,
  oppositionAgent,
  currentSpeaker,
  currentSpeakerRole,
  streamingContent,
  activePropositionId,
}: DebateArenaProps) {
  console.log("streamingContent in DebateArena", streamingContent);
  const arenaRadius = 280;
  const agentCount = propositionAgents.length;

  // Calculate angle offset to position active agent at the right side
  const getAngleOffset = () => {
    if (!activePropositionId) return 0;
    const activeIndex = propositionAgents.findIndex(
      (a) => a.id === activePropositionId
    );
    if (activeIndex === -1) return 0;
    // We want the active agent at approximately 90 degrees (right side)
    const baseAngle = (360 / agentCount) * activeIndex;
    return 90 - baseAngle;
  };

  const angleOffset = getAngleOffset();

  // Find the current speaker agent for the speech bubble
  const getCurrentSpeakerAgent = () => {
    if (!currentSpeaker) return null;
    if (currentSpeakerRole === "opposition") {
      return oppositionAgent;
    }
    return propositionAgents.find((a) => a.name === currentSpeaker);
  };

  const speakerAgent = getCurrentSpeakerAgent();

  // Get position for speech bubble based on speaker role
  const getSpeechBubblePosition = () => {
    if (currentSpeakerRole === "opposition") {
      return { top: "35%", left: "25%", position: "left" as const };
    }
    // Position proposition bubble on the right side
    return { top: "45%", right: "15%", position: "right" as const };
  };

  const bubblePosition = getSpeechBubblePosition();

  return (
    <div className={styles.arena}>
      {/* Main circular ring */}
      <div className={styles.ring}>
        <svg className={styles.ringSvg} viewBox="0 0 600 600">
          <circle
            cx="300"
            cy="300"
            r={arenaRadius}
            fill="none"
            stroke="rgba(255, 255, 255, 0.1)"
            strokeWidth="2"
            strokeDasharray="8 4"
          />
        </svg>
      </div>

      {/* Proposition agents around the circle */}
      <div className={styles.agentsContainer}>
        {propositionAgents.map((agent, index) => {
          const baseAngle = (360 / agentCount) * index;
          const angle = baseAngle + angleOffset;

          return (
            <PropositionAgent
              key={agent.id}
              id={agent.id}
              name={agent.name}
              icon={agent.icon}
              isActive={agent.id === activePropositionId}
              isSpeaking={
                agent.name === currentSpeaker &&
                currentSpeakerRole === "proposition"
              }
              voteStatus={agent.voteStatus}
              streamingContent={agent.streamingContent}
              angle={angle}
              radius={arenaRadius}
            />
          );
        })}
      </div>

      {/* Opposition agent in center */}
      {oppositionAgent && (
        <OppositionAgent
          name={oppositionAgent.name}
          icon={oppositionAgent.icon}
          isSpeaking={currentSpeakerRole === "opposition"}
        />
      )}

      {/* Opposition speech bubble (still using legacy streamingContent) */}
      {streamingContent &&
        speakerAgent &&
        currentSpeakerRole === "opposition" && (
          <div
            className={styles.speechBubbleContainer}
            style={{ top: bubblePosition.top, left: bubblePosition.left }}
          >
            <SpeechBubble
              content={streamingContent}
              agentName={speakerAgent.name}
              role="opposition"
              position="left"
              isStreaming={true}
            />
          </div>
        )}

      {/* Legend */}
      <div className={styles.legend}>
        <div className={styles.legendItem}>
          <div className={`${styles.legendIcon} ${styles.proposition}`} />
          <span>Proposition</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendIcon} ${styles.opposition}`} />
          <span>Opposition</span>
        </div>
      </div>
    </div>
  );
}
