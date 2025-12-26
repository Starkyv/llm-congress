# LLM Congress - Multi-Agent Debate Platform

A real-time debate simulation platform where different LLM models or AI personalities debate with each other in a structured format. Watch as AI agents with distinct personalities engage in dynamic debates, vote on each other's performance, and switch roles based on peer evaluation.

## Overview

LLM Congress simulates a congressional-style debate where:
- **One Opposition Agent** defends a position
- **N Proposition Agents** challenge the opposition
- Agents take turns debating, with the other proposition agents voting on whether the current debater should continue or be replaced
- Debates run for a specified duration with real-time streaming updates

## How It Works

1. **Topic Selection**: A debate topic is provided
2. **Random Selection**: One proposition agent is randomly chosen to debate the opposition
3. **Debate Exchanges**: The selected proposition and opposition engage in multiple exchanges
4. **Peer Voting**: After each round, the other (N-1) proposition agents vote:
   - **Vote In**: The current debater continues
   - **Vote Out**: The current debater is replaced
5. **Replacement Rule**: If more than 50% vote out, a new proposition agent takes over
6. **Continuation**: If 50% or less vote out, the current debater continues
7. **Timer**: The process repeats until the timer expires

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- pnpm (or npm/yarn)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd llm-congress
   ```

2. **Set up Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Frontend**
   ```bash
   cd frontend
   pnpm install
   ```

4. **Configure Environment**
   
   Create a `.env` file in the `backend` directory with your API keys:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

### Running the Application

1. **Start the Backend**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Frontend** (in a new terminal)
   ```bash
   cd frontend
   pnpm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Configuration

### Agent Configuration

Edit `backend/config/agent_config.json` to configure agents, their personalities, models, and behavior.

**Configuration Structure:**
- `debate_config`: Default settings for debates (model, temperature, streaming, max_tokens)
- `proposition_agents`: Array of proposition agents with:
  - `id`: Unique identifier
  - `name`: Display name
  - `personality_type`: Personality category
  - `behavior`: Detailed personality description/prompt
  - `temperature`: Model temperature (0.0-1.0)
  - `model`: LLM model identifier
- `opposition_agent`: Single opposition agent configuration
- `moderator_agent`: Moderator agent for summaries

**Example Agent:**
```json
{
  "id": "agent_bruce_wayne",
  "name": "Bruce Wayne",
  "personality_type": "brooding_strategic_billionaire",
  "behavior": "You are Bruce Wayne from Batman. Speak in a serious, calculated, and intense tone...",
  "temperature": 0.6,
  "model": "x-ai/grok-4.1-fast"
}
```

## API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /agents` - Get all available agents
- `GET /health` - Health check

### Debate Endpoints

- `POST /debate/start` - Start a debate (non-streaming)
- `GET /debate/stream` - Start a debate with Server-Sent Events streaming
  - Query params: `topic`, `duration` (default: 300s), `exchanges_per_round` (default: 3), `first_agent_id` (optional)
- `GET /debate/status` - Get current debate status
- `GET /debate/state` - Get full debate state
- `POST /debate/stop` - Stop current debate
- `GET /debate/events` - Get buffered events (for late-joining clients)

### Event Types

The streaming endpoint emits the following event types:
- `debate_started` - Debate initialization
- `agent_message_chunk` - Streaming message chunk
- `agent_message_complete` - Complete agent message
- `voting_initiated` - Voting round started
- `vote_cast` - Individual vote recorded
- `voting_complete` - Voting round finished
- `agent_switch` - Agent replacement occurred
- `timer_update` - Time remaining update
- `debate_complete` - Debate finished

## Project Structure

```
llm-congress/
├── backend/
│   ├── agents/          # Agent factory and management
│   ├── config/          # Configuration files (agent_config.json)
│   ├── state/           # Debate state models and operations
│   ├── streaming/       # SSE event handling
│   ├── tasks/           # Debate, moderation, and voting tasks
│   ├── utils/           # State helpers and queries
│   ├── workflows/       # Debate workflow orchestration
│   │   └── steps/       # Individual workflow steps
│   ├── main.py          # FastAPI application
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # State management (Zustand)
│   │   └── types/       # TypeScript types
│   └── package.json     # Frontend dependencies
└── debates/             # Debate history/logs
```

## Technologies

### Backend

- **Agno** - LLM API clients

### Frontend
- **React** - UI framework
- **Zustand** - State management
- **Server-Sent Events** - Real-time streaming

## Features

- **Real-time Streaming**: Watch debates unfold in real-time via SSE
- **Dynamic Agent Switching**: Agents are replaced based on peer voting
- **Personality-driven Debates**: Each agent has unique personality and behavior
- **Voting System**: Democratic peer evaluation of debater performance
- **Timer-based Rounds**: Configurable debate duration and exchange counts
- **Event History**: Buffered events for late-joining clients

## Deployment

### Backend 
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend 
```bash
cd frontend
pnpm run dev
```

