// Debate Types

export interface Agent {
  id: string;
  name: string;
  role: 'proposition' | 'opposition';
  isActive: boolean;
  isSpeaking: boolean;
  icon?: string;
  voteStatus?: 'in' | 'out' | null;
  streamingContent?: string; // Current streaming text for this agent
}

export interface Message {
  agentId: string;
  agentName: string;
  role: 'proposition' | 'opposition';
  content: string;
  timestamp: string;
}

export interface Vote {
  voterId: string;
  voterName: string;
  vote: 'in' | 'out';
  reasoning?: string;
}

export interface DebateState {
  isRunning: boolean;
  topic: string;
  phase: 'idle' | 'debating' | 'voting' | 'switching' | 'complete';
  currentSpeaker: string | null;
  currentSpeakerRole: 'proposition' | 'opposition' | null;
  streamingContent: string; // Legacy - kept for opposition agent
  propositionAgents: Agent[];
  oppositionAgent: Agent | null;
  activePropositionId: string | null;
  messages: Message[];
  votes: Vote[];
  roundNumber: number;
  elapsedSeconds: number;
  remainingSeconds: number;
}

// SSE Event Types
export interface SSEEvent {
  event: string;
  data: any;
}

export interface DebateStartedData {
  topic: string;
  duration: number;
  exchanges_per_round: number;
  first_debater_id: string;
  first_debater_name: string;
  opposition_name: string;
  observer_names: string[];
  total_agents: number;
  timestamp: string;
}

export interface AgentMessageChunkData {
  agent_id: string;
  agent_name: string;
  role: 'proposition' | 'opposition';
  chunk: string;
  timestamp: string;
}

export interface AgentMessageCompleteData {
  agent_id: string;
  agent_name: string;
  role: 'proposition' | 'opposition';
  content: string;
  word_count: number;
  round_number: number;
  timestamp: string;
}

export interface VotingInitiatedData {
  evaluating_agent_id: string;
  evaluating_agent_name: string;
  round_number: number;
  observer_count: number;
  timestamp: string;
}

export interface VoteCastData {
  voter_id: string;
  voter_name: string;
  vote: 'in' | 'out';
  reasoning: string;
  timestamp: string;
}

export interface VotingCompleteData {
  evaluating_agent_id: string;
  evaluating_agent_name: string;
  in_votes: number;
  out_votes: number;
  decision: 'switch' | 'stay';
  votes: Vote[];
  timestamp: string;
}

export interface AgentSwitchData {
  old_agent_id: string;
  old_agent_name: string;
  new_agent_id: string;
  new_agent_name: string;
  reason: string;
  in_votes: number;
  out_votes: number;
  round_number: number;
  timestamp: string;
}

export interface TimerUpdateData {
  elapsed_seconds: number;
  remaining_seconds: number;
  elapsed_formatted: string;
  remaining_formatted: string;
  is_paused: boolean;
  timestamp: string;
}

export interface PhaseChangeData {
  old_phase: string;
  new_phase: string;
  message: string;
  timestamp: string;
}

export interface DebateCompleteData {
  topic: string;
  duration_seconds: number;
  total_messages: number;
  total_rounds: number;
  total_switches: number;
  final_proposition_agent: string;
  summary_preview: string;
  statistics: Record<string, any>;
  timestamp: string;
}

