import { useEffect } from "react";
import { PropositionAgent } from "../PropositionAgent";
import { OppositionAgent } from "../OppositionAgent";
import { useDebateStore } from "../../store/debateStore";
import styles from "./ArenaTable.module.scss";

interface ArenaTableProps {
  agents?: Array<{ 
    id: string; 
    name: string; 
    isActive?: boolean;
    voteStatus?: 'in' | 'out' | null;
  }>;
}

export function ArenaTable({ agents: propAgents }: ArenaTableProps) {
  const { agents, oppositionAgent, fetchAgents, isLoadingAgents, phase } =
    useDebateStore();

  useEffect(() => {
    // Fetch agents if not already loaded and no agents provided via props
    if (agents.length === 0 && !propAgents) {
      fetchAgents();
    }
  }, [agents.length, fetchAgents, propAgents]);

  // Use prop agents if provided, otherwise use store agents with streaming data
  const displayAgents =
    propAgents ||
    agents.map((agent) => ({
      id: agent.id,
      name: agent.name,
      icon: agent.icon,
      isActive: false,
      isSpeaking: agent.isSpeaking || false,
      streamingContent: agent.streamingContent || "",
      voteStatus: (agent as any).voteStatus || null,
      voteCast: (agent as any).voteCast || null,
    }));
  const circleRadius = 230; // Radius of the circle
  const agentSize = 30; // Size of each agent element (matches PropositionAgent circle size)
  const totalAgents = displayAgents.length;

  // Calculate position for each agent using the working logic
  const getAgentPosition = (index: number) => {
    const angle = (index * 2 * Math.PI) / totalAgents - Math.PI / 2; // Start from top
    const x = circleRadius * Math.cos(angle);
    const y = circleRadius * Math.sin(angle);
    return { x, y };
  };

  // Calculate angle in degrees for PropositionAgent component
  const getAngleInDegrees = (index: number) => {
    const angle = (index * 2 * Math.PI) / totalAgents - Math.PI / 2;
    return (angle * 180) / Math.PI + 90; // Convert to degrees and adjust
  };

  if (isLoadingAgents && displayAgents.length === 0) {
    return (
      <div className={styles.arenaTable}>
        <div className={styles.loading}>Loading agents...</div>
      </div>
    );
  }
  console.log("displayAgents", displayAgents);
  return (
    <div className={styles.arenaTable}>
      <div className={styles.outerCircle} />
      <div className={styles.innerCircle} />
      <div
        className={styles.agentsContainer}
        style={{
          width: circleRadius * 2 + agentSize,
          height: circleRadius * 2 + agentSize,
        }}
      >
        {displayAgents.map((agent, index) => {
          const { x, y } = getAgentPosition(index);
          const angleDegrees = getAngleInDegrees(index);
          return (
            <div
              key={agent.id}
              className={styles.agentWrapper}
              style={{
                position: "absolute",
                left: `calc(50% + ${x}px - ${agentSize / 2}px)`,
                top: `calc(50% + ${y}px - ${agentSize / 2}px)`,
              }}
            >
              <PropositionAgent
                id={agent.id}
                name={agent.name}
                icon={(agent as any).icon}
                isActive={agent.isActive || false}
                isSpeaking={(agent as any).isSpeaking || false}
                streamingContent={(agent as any).streamingContent || ""}
                voteStatus={(agent as any).voteStatus || null}
                voteCast={(agent as any).voteCast || null}
                phase={phase}
                angle={angleDegrees}
                radius={0}
              />
            </div>
          );
        })}
      </div>
      {oppositionAgent && (
        <div className={styles.oppositionContainer}>
          <OppositionAgent
            id={oppositionAgent.id}
            name={oppositionAgent.name}
            icon={oppositionAgent.icon}
            isSpeaking={oppositionAgent.isSpeaking || false}
            streamingContent={oppositionAgent.streamingContent || ""}
          />
        </div>
      )}
    </div>
  );
}
