# LLM Congress Frontend

A React + TypeScript frontend for the LLM Congress multi-agent debate system, built with Vite.

## Features

- **Circular Debate Arena**: Visual representation of agents positioned around a circle
- **Real-time Streaming**: Live debate updates via Server-Sent Events (SSE)
- **Vote Visualization**: Color-coded voting states (green for "in", red for "out")
- **Speech Bubbles**: Streaming text display near speaking agents
- **Timer & Phases**: Track debate progress and current phase

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- pnpm (install with `npm install -g pnpm`)

### Installation

```bash
cd frontend
pnpm install
```

### Development

Start the development server:

```bash
pnpm dev
```

The app will be available at `http://localhost:3000`

Make sure the backend is running on `http://localhost:8000` for the API proxy to work.

### Build

Build for production:

```bash
pnpm build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── DebateArena/     # Main circular layout
│   │   ├── OppositionAgent/ # Green diamond (center)
│   │   ├── PropositionAgent/# Pink circles (perimeter)
│   │   ├── SpeechBubble/    # Streaming text display
│   │   ├── Timer/           # Progress and round info
│   │   └── TopicInput/      # Debate starter form
│   ├── services/            # API and streaming services
│   │   └── debateStream.ts  # SSE parser and API calls
│   ├── types/               # TypeScript definitions
│   │   └── debate.ts        # Debate state and event types
│   ├── App.tsx              # Main app with state management
│   └── main.tsx             # Entry point
├── index.html               # HTML template
├── vite.config.ts           # Vite configuration
└── package.json             # Dependencies
```

## Component Overview

### DebateArena
The main layout component that positions agents in a circle with the opposition in the center.

### PropositionAgent
Represents proposition agents as pink circles positioned around the arena perimeter. Shows:
- Active state (currently debating)
- Speaking indicator (sound wave animation)
- Vote status (green glow for "in", red for "out")

### OppositionAgent
The opposition agent displayed as a green diamond in the center.

### SpeechBubble
Displays streaming text from the current speaker with a typing indicator.

### TopicInput
Form to enter debate topic and duration, with start/stop controls.

### Timer
Shows elapsed time, remaining time, current phase, and round number.

## SSE Events Handled

| Event | Description |
|-------|-------------|
| `debate_started` | Debate begins, initializes state |
| `agent_message_chunk` | Streaming text chunk from agent |
| `agent_message_complete` | Agent finished speaking |
| `voting_initiated` | Voting round starts |
| `vote_cast` | Individual vote registered |
| `voting_complete` | All votes counted |
| `agent_switch` | Active proposition agent changes |
| `timer_update` | Time elapsed/remaining updates |
| `debate_complete` | Debate finished |

## API Proxy

The Vite dev server proxies `/api` requests to `http://localhost:8000` (the backend server).

## Styling

Each component has its own `*.module.scss` file for scoped styling. No inline styles or Tailwind - just clean SCSS modules.
