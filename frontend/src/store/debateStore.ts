import { create } from "zustand";
import { streamDebate, stopDebate } from "../services/debateStream";
import { SSEEvent } from "../types/debate";

interface Agent {
  id: string;
  name: string;
  personality?: string;
  icon?: string;
  streamingContent?: string;
  isSpeaking?: boolean;
  voteStatus?: 'in' | 'out' | null; // Whether this agent was voted in/out
  voteCast?: { vote: 'in' | 'out'; reasoning: string } | null; // Vote cast BY this agent
}

interface AgentsResponse {
  total_agents: number;
  proposition_count: number;
  proposition_agents: Agent[];
  opposition: Record<string, any>;
  moderator: Record<string, any>;
}

interface OppositionAgent {
  id: string;
  name: string;
  personality?: string;
  icon?: string;
  streamingContent?: string;
  isSpeaking?: boolean;
}

type QueuedEventType = 
  | "agent_message_complete"
  | "voting_initiated"
  | "vote_cast"
  | "voting_complete"
  | "agent_switch";

interface QueuedEvent {
  type: QueuedEventType;
  timestamp: number;
  // For agent_message_complete
  agent_id?: string;
  agent_name?: string;
  role?: "proposition" | "opposition";
  content?: string;
  // For voting_initiated
  evaluating_agent_id?: string;
  evaluating_agent_name?: string;
  round_number?: number;
  observer_count?: number;
  // For vote_cast
  voter_id?: string;
  voter_name?: string;
  vote?: "in" | "out";
  reasoning?: string;
  // For voting_complete
  decision?: "stay" | "switch";
  in_votes?: number;
  out_votes?: number;
  vote_tally?: { in: number; out: number };
  // For agent_switch
  old_agent_id?: string;
  old_agent_name?: string;
  new_agent_id?: string;
  new_agent_name?: string;
  reason?: string;
}

interface VoteCast {
  voter_id: string;
  voter_name: string;
  vote: "in" | "out";
  reasoning: string;
  timestamp: string;
}

interface VotingResultModal {
  isOpen: boolean;
  agentName: string;
  decision: "stay" | "switch" | null;
  inVotes: number;
  outVotes: number;
  totalVotes: number;
  newAgentName?: string;
  reason?: string;
}


interface DebateState {
  topic: string;
  duration: number;
  agents: Agent[];
  oppositionAgent: OppositionAgent | null;
  isLoadingAgents: boolean;
  isDebating: boolean;
  phase: "debating" | "voting";
  currentSpeakerId: string | null;
  currentSpeakerRole: "proposition" | "opposition" | null;
  currentEvaluatingAgentId: string | null;
  cancelDebate: (() => void) | null;
  eventQueue: QueuedEvent[];
  isProcessingQueue: boolean;
  isPaused: boolean;
  queueProcessorTimeout: NodeJS.Timeout | null;
  voteCasts: VoteCast[];
  votingResultModal: VotingResultModal;
  setTopic: (topic: string) => void;
  setDuration: (duration: number) => void;
  setAgents: (agents: Agent[]) => void;
  setOppositionAgent: (agent: OppositionAgent | null) => void;
  fetchAgents: () => Promise<void>;
  startDebate: () => Promise<void>;
  stopDebateStream: () => void;
  handleSSEEvent: (event: SSEEvent) => void;
  processEventQueue: () => void;
  skipCurrentEvent: () => void;
  togglePause: () => void;
  closeVotingResultModal: () => void;
  reset: () => void;
}

// Calculate reading time based on message length
// Average reading speed: ~200 words per minute = ~3.3 words per second
// Add minimum time to ensure readability
const calculateReadingTime = (content: string): number => {
  const wordCount = content
    .split(/\s+/)
    .filter((word) => word.length > 0).length;
  // 3.3 words per second = ~300ms per word, minimum 3 seconds, maximum 15 seconds
  const readingTime = Math.max(wordCount * 300, 3000);
  return Math.min(readingTime, 15000);
};

export const useDebateStore = create<DebateState>((set, get) => ({
  topic: "",
  duration: 3,
  agents: [],
  oppositionAgent: null,
  isLoadingAgents: false,
  isDebating: false,
  phase: "debating",
  currentSpeakerId: null,
  currentSpeakerRole: null,
  currentEvaluatingAgentId: null,
  cancelDebate: null,
  eventQueue: [],
  isProcessingQueue: false,
  isPaused: false,
  queueProcessorTimeout: null,
  voteCasts: [],
  votingResultModal: {
    isOpen: false,
    agentName: "",
    decision: null,
    inVotes: 0,
    outVotes: 0,
    totalVotes: 0,
    newAgentName: undefined,
    reason: undefined,
  },
  setTopic: (topic) => set({ topic }),
  setDuration: (duration) => set({ duration }),
  setAgents: (agents) => set({ agents }),
  setOppositionAgent: (agent) => set({ oppositionAgent: agent }),
  fetchAgents: async () => {
    set({ isLoadingAgents: true });
    try {
      const response = await fetch("/api/agents");
      if (!response.ok) {
        throw new Error("Failed to fetch agents");
      }
      const data: AgentsResponse = await response.json();
      set({
        agents: data.proposition_agents || [],
        oppositionAgent: data.opposition
          ? {
              id: data.opposition.id || "",
              name: data.opposition.name || "Opposition",
              personality: data.opposition.personality,
              icon: data.opposition.icon,
            }
          : null,
        isLoadingAgents: false,
      });
    } catch (error) {
      console.error("Error fetching agents:", error);
      set({ isLoadingAgents: false });
    }
  },
  startDebate: async () => {
    const { topic, duration, handleSSEEvent } = get();
    if (!topic) return;

    set({ isDebating: true });

    const cancel = await streamDebate(
      topic,
      duration * 60, // Convert minutes to seconds
      (event) => handleSSEEvent(event),
      () => {
        set({ isDebating: false, cancelDebate: null });
      },
      (error) => {
        console.error("Debate stream error:", error);
        set({ isDebating: false, cancelDebate: null });
      }
    );

    set({ cancelDebate: cancel });
  },
  stopDebateStream: () => {
    const { cancelDebate, queueProcessorTimeout } = get();
    if (cancelDebate) {
      cancelDebate();
    }
    if (queueProcessorTimeout) {
      clearTimeout(queueProcessorTimeout);
    }
    stopDebate().catch(console.error);
    set({
      isDebating: false,
      cancelDebate: null,
      eventQueue: [],
      isProcessingQueue: false,
      isPaused: false,
      queueProcessorTimeout: null,
    });
  },
  handleSSEEvent: (event: SSEEvent) => {
    console.log("event", event);
    
    // Queue all events that need to be displayed in order
    const queueableEvents: QueuedEventType[] = [
      "agent_message_complete",
      "voting_initiated",
      "vote_cast",
      "voting_complete",
      "agent_switch",
    ];

    if (queueableEvents.includes(event.event as QueuedEventType)) {
      // Add event to queue
      const queuedEvent: QueuedEvent = {
        type: event.event as QueuedEventType,
        timestamp: Date.now(),
        ...event.data,
      };

      const { eventQueue } = get();
      const updatedQueue = [...eventQueue, queuedEvent];
      set({ eventQueue: updatedQueue });

      // Start processing if not already processing
      if (!get().isProcessingQueue) {
        get().processEventQueue();
      }
    } else if (event.event === "debate_complete") {
      // Don't queue debate_complete, but ensure queue continues processing
      // The queue will finish processing all remaining items
      set({
        isDebating: false,
        currentSpeakerId: null,
        currentSpeakerRole: null,
      });
    }
  },
  processEventQueue: () => {
    const { eventQueue, isPaused } = get();

    // Stop if paused
    if (isPaused) {
      set({ isProcessingQueue: false });
      return;
    }

    // If no events left, stop processing
    if (eventQueue.length === 0) {
      set({ isProcessingQueue: false });
      return;
    }

    // Mark as processing
    set({ isProcessingQueue: true });

    // Get first event from queue
    const [currentEvent, ...remainingQueue] = eventQueue;

    // Remove event from queue immediately
    set({ eventQueue: remainingQueue });

    // Handle different event types
    switch (currentEvent.type) {
      case "agent_message_complete": {
        const { agent_id, agent_name, role, content } = currentEvent;
        if (!content) break;

        // Calculate reading time for this message
        const readingTime = calculateReadingTime(content);

        // Display the message immediately
        const { agents, oppositionAgent } = get();

        if (role === "opposition" && oppositionAgent) {
          // Clear all proposition agents and show opposition
          const clearedAgents = agents.map((agent) => ({
            ...agent,
            streamingContent: "",
            isSpeaking: false,
          }));
          set({
            agents: clearedAgents,
            oppositionAgent: {
              ...oppositionAgent,
              streamingContent: content,
              isSpeaking: true,
            },
            currentSpeakerId: agent_id,
            currentSpeakerRole: "opposition",
          });
        } else {
          // Clear opposition and show proposition agent
          const updatedAgents = agents.map((agent) =>
            agent.id === agent_id || agent.name === agent_name
              ? {
                  ...agent,
                  streamingContent: content,
                  isSpeaking: true,
                }
              : { ...agent, streamingContent: "", isSpeaking: false }
          );
          set({
            agents: updatedAgents,
            oppositionAgent: oppositionAgent
              ? {
                  ...oppositionAgent,
                  streamingContent: "",
                  isSpeaking: false,
                }
              : null,
            currentSpeakerId: agent_id,
            currentSpeakerRole: "proposition",
          });
        }

        // After reading time, clear message and process next
        const timeout = setTimeout(() => {
          // Clear current message
          const { agents: currentAgents, oppositionAgent: currentOpp } = get();

          if (role === "opposition" && currentOpp) {
            set({
              oppositionAgent: {
                ...currentOpp,
                streamingContent: "",
                isSpeaking: false,
              },
            });
          } else {
            const clearedAgents = currentAgents.map((agent) => ({
              ...agent,
              streamingContent: "",
              isSpeaking: false,
            }));
            set({ agents: clearedAgents });
          }

          // Process next event
          get().processEventQueue();
        }, readingTime);

        set({ queueProcessorTimeout: timeout });
        break;
      }

      case "voting_initiated": {
        const { evaluating_agent_id } = currentEvent;
        
        console.log("Voting initiated, switching to voting phase");

        // Switch to voting phase
        const { agents } = get();
        const clearedAgents = agents.map((agent) => ({
          ...agent,
          voteStatus: null,
          voteCast: null,
          streamingContent: "",
          isSpeaking: false,
        }));

        set({
          phase: "voting",
          currentEvaluatingAgentId: evaluating_agent_id,
          agents: clearedAgents,
          oppositionAgent: (() => {
            const opp = get().oppositionAgent;
            return opp
              ? {
                  id: opp.id,
                  name: opp.name,
                  personality: opp.personality,
                  icon: opp.icon,
                  streamingContent: "",
                  isSpeaking: false,
                }
              : null;
          })(),
          voteCasts: [],
          currentSpeakerId: null,
          currentSpeakerRole: null,
        });

        // Process next event immediately
        get().processEventQueue();
        break;
      }

      case "vote_cast": {
        const { voter_id, voter_name, vote, reasoning } = currentEvent;
        const { agents, voteCasts } = get();

        // Add vote cast to the list
        const newVoteCast: VoteCast = {
          voter_id: voter_id || "",
          voter_name: voter_name || "",
          vote: vote || "out",
          reasoning: reasoning || "",
          timestamp: new Date().toISOString(),
        };

        const updatedVoteCasts = [...voteCasts, newVoteCast];
        set({ voteCasts: updatedVoteCasts });

        // Update the VOTER agent with their vote cast (keep previous votes visible)
        const updatedAgents = agents.map((agent) =>
          agent.id === voter_id
            ? { ...agent, voteCast: { vote: vote || "out", reasoning: reasoning || "" } }
            : agent
        );
        set({ agents: updatedAgents });

        // Show vote cast for 1 second, then process next event (don't clear the vote)
        const timeout = setTimeout(() => {
          // Process next event (keep all votes visible)
          get().processEventQueue();
        }, 1000); // 1 second delay to show the vote animation

        set({ queueProcessorTimeout: timeout });
        break;
      }

      case "voting_complete": {
        const {
          evaluating_agent_id,
          evaluating_agent_name,
          decision,
          in_votes,
          out_votes,
          vote_tally,
        } = currentEvent;
        const { agents } = get();

        // Extract vote counts (support both formats)
        const inVotes = in_votes ?? vote_tally?.in ?? 0;
        const outVotes = out_votes ?? vote_tally?.out ?? 0;
        const totalVotes = inVotes + outVotes;

        // Show voting result modal
        set({
          votingResultModal: {
            isOpen: true,
            agentName: evaluating_agent_name || "Agent",
            decision: decision as "stay" | "switch",
            inVotes,
            outVotes,
            totalVotes,
          },
        });

        // Clear all vote casts and update voteStatus based on decision
        const updatedAgents = agents.map((agent) =>
          agent.id === evaluating_agent_id
            ? {
                ...agent,
                voteCast: null, // Clear vote cast
                voteStatus: (decision === "switch" ? "out" : "in") as "in" | "out",
              }
            : {
                ...agent,
                voteCast: null, // Clear all vote casts
              }
        );

        // Switch back to debating phase but keep paused until modal closes
        set({
          phase: "debating",
          currentEvaluatingAgentId: null,
          agents: updatedAgents,
          isPaused: true, // Keep paused while modal is shown
          isProcessingQueue: false,
        });

        // Don't process next event until modal closes
        break;
      }

      case "agent_switch": {
        const {
          old_agent_name,
          new_agent_name,
          reason,
          vote_tally,
        } = currentEvent;

        // Extract vote counts
        const inVotes = vote_tally?.in ?? 0;
        const outVotes = vote_tally?.out ?? 0;
        const totalVotes = inVotes + outVotes;
        const decision = outVotes > inVotes ? "switch" : "stay";

        const { agents } = get();

        // Clear all vote casts
        const updatedAgents = agents.map((agent) => ({
          ...agent,
          voteCast: null,
        }));

        // Show voting result modal with agent switch info
        set({
          votingResultModal: {
            isOpen: true,
            agentName: old_agent_name || "Agent",
            decision: decision as "stay" | "switch",
            inVotes,
            outVotes,
            totalVotes,
            newAgentName: new_agent_name,
            reason: reason || "",
          },
          agents: updatedAgents,
          isPaused: true, // Keep paused while modal is shown
          isProcessingQueue: false,
        });

        // Don't process next event until modal closes
        break;
      }

      default:
        // Unknown event type, process next immediately
        get().processEventQueue();
        break;
    }
  },
  skipCurrentEvent: () => {
    const { queueProcessorTimeout } = get();

    // Clear current timeout
    if (queueProcessorTimeout) {
      clearTimeout(queueProcessorTimeout);
      set({ queueProcessorTimeout: null });
    }

    // Clear current displayed message
    const { agents, oppositionAgent } = get();
    const clearedAgents = agents.map((agent) => ({
      ...agent,
      streamingContent: "",
      isSpeaking: false,
    }));
    set({
      agents: clearedAgents,
      oppositionAgent: oppositionAgent
        ? {
            ...oppositionAgent,
            streamingContent: "",
            isSpeaking: false,
          }
        : null,
    });

    // Process next event immediately
    get().processEventQueue();
  },
  togglePause: () => {
    const { isPaused, queueProcessorTimeout } = get();

    if (isPaused) {
      // Resume: start processing queue
      set({ isPaused: false });
      get().processEventQueue();
    } else {
      // Pause: stop processing
      if (queueProcessorTimeout) {
        clearTimeout(queueProcessorTimeout);
        set({ queueProcessorTimeout: null });
      }
      set({ isPaused: true, isProcessingQueue: false });
    }
  },
  closeVotingResultModal: () => {
    const currentState = get();
    
    set({
      votingResultModal: {
        isOpen: false,
        agentName: "",
        decision: null,
        inVotes: 0,
        outVotes: 0,
        totalVotes: 0,
        newAgentName: undefined,
        reason: undefined,
      },
      isPaused: false,
    });

    // Always resume processing event queue after modal closes
    // Check if we should resume based on current state
    if (
      currentState.phase === "debating" &&
      currentState.eventQueue.length > 0 &&
      !currentState.isProcessingQueue
    ) {
      // Use setTimeout to ensure state update (isPaused: false) is applied
      setTimeout(() => {
        const updatedState = get();
        if (!updatedState.isPaused && !updatedState.isProcessingQueue) {
          console.log("Resuming event queue after modal close", {
            queueLength: updatedState.eventQueue.length,
            phase: updatedState.phase,
          });
          updatedState.processEventQueue();
        }
      }, 50);
    }
  },
  reset: () => {
    const { queueProcessorTimeout } = get();
    if (queueProcessorTimeout) {
      clearTimeout(queueProcessorTimeout);
    }
    set({
      topic: "",
      duration: 3,
      isDebating: false,
      phase: "debating",
      currentSpeakerId: null,
      currentSpeakerRole: null,
      currentEvaluatingAgentId: null,
      eventQueue: [],
      isProcessingQueue: false,
      isPaused: false,
      queueProcessorTimeout: null,
      voteCasts: [],
    });
  },
}));
