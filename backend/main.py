"""
FastAPI Backend for Debate Workflow

Provides REST API and SSE streaming endpoints for the debate system.
"""

import sys
import os
from typing import Optional
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from workflows import DebateWorkflow, create_debate_workflow, DebateEventType
from streaming import SSEHandler, EventBuffer, event_to_sse
from agents import get_agent_info
from state import DebateState

# Initialize FastAPI app
app = FastAPI(
    title="LLM Congress - Debate API",
    description="Multi-agent debate simulation with streaming events",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
active_workflow: Optional[DebateWorkflow] = None
event_buffer = EventBuffer(max_size=500)


# === Request/Response Models ===

class DebateRequest(BaseModel):
    """Request to start a new debate"""
    topic: str = Field(..., description="The debate topic")
    duration: int = Field(default=300, description="Duration in seconds")
    exchanges_per_round: int = Field(default=5, description="Exchanges before voting")
    first_agent_id: Optional[str] = Field(default=None, description="First agent ID")


class DebateStatus(BaseModel):
    """Current debate status"""
    is_running: bool
    topic: Optional[str] = None
    phase: Optional[str] = None
    elapsed_seconds: int = 0
    total_messages: int = 0
    total_rounds: int = 0


class AgentInfo(BaseModel):
    """Agent information"""
    id: str
    name: str
    personality: str


class AgentsResponse(BaseModel):
    """Response with all available agents"""
    total_agents: int
    proposition_count: int
    proposition_agents: list
    opposition: dict
    moderator: dict


# === Endpoints ===

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "LLM Congress Debate API",
        "version": "1.0.0",
        "endpoints": {
            "agents": "/agents",
            "debate": "/debate",
            "stream": "/debate/stream",
            "status": "/debate/status",
        }
    }


@app.get("/agents", response_model=AgentsResponse)
async def get_agents():
    """Get information about available agents"""
    try:
        info = get_agent_info()
        return AgentsResponse(**info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debate/status", response_model=DebateStatus)
async def get_debate_status():
    """Get current debate status"""
    global active_workflow
    
    if not active_workflow:
        return DebateStatus(is_running=False)
    
    state = active_workflow.get_state()
    return DebateStatus(
        is_running=active_workflow.is_running,
        topic=state.get("topic"),
        phase=state.get("phase"),
        elapsed_seconds=state.get("elapsed_seconds", 0),
        total_messages=len(state.get("messages", [])),
        total_rounds=state.get("current_round", 1),
    )


@app.post("/debate/start")
async def start_debate(request: DebateRequest, background_tasks: BackgroundTasks):
    """
    Start a new debate (non-streaming).
    
    For streaming, use /debate/stream instead.
    """
    global active_workflow
    
    if active_workflow and active_workflow.is_running:
        raise HTTPException(status_code=409, detail="A debate is already in progress")
    
    # Clear event buffer
    event_buffer.clear()
    
    # Create new workflow
    active_workflow = create_debate_workflow()
    
    # Run in background
    async def run_debate():
        global active_workflow
        try:
            final_state = active_workflow.run_sync(
                topic=request.topic,
                duration=request.duration,
                exchanges_per_round=request.exchanges_per_round,
                first_agent_id=request.first_agent_id
            )
        except Exception as e:
            print(f"Debate error: {e}")
    
    background_tasks.add_task(run_debate)
    
    return {
        "status": "started",
        "topic": request.topic,
        "duration": request.duration,
        "message": "Debate started. Use /debate/stream for live events."
    }


@app.get("/debate/stream")
async def stream_debate(
    topic: str,
    duration: int = 300,
    exchanges_per_round: int = 3,
    first_agent_id: Optional[str] = None
):
    """
    Start a debate and stream events via Server-Sent Events.
    
    Connect to this endpoint to receive real-time debate events.
    
    Event types include:
    - debate_started
    - agent_message_chunk
    - agent_message_complete
    - voting_initiated
    - vote_cast
    - voting_complete
    - agent_switch
    - timer_update
    - debate_complete
    """
    global active_workflow
    
    if active_workflow and active_workflow.is_running:
        raise HTTPException(status_code=409, detail="A debate is already in progress")
    
    # Clear event buffer
    event_buffer.clear()
    
    # Create workflow
    active_workflow = create_debate_workflow()
    
    # Create SSE handler
    sse_handler = SSEHandler()
    
    async def event_generator():
        """Generate SSE events from workflow"""
        try:
            # Initial connection message
            yield sse_handler.format_event("connected", {
                "message": "Connected to debate stream",
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            })
            
            # Run workflow and stream events
            gen = active_workflow.run(
                topic=topic,
                duration=duration,
                exchanges_per_round=exchanges_per_round,
                first_agent_id=first_agent_id,
                stream=True
            )
            
            async for sse_message in sse_handler.stream_events(gen):
                event_buffer.add(sse_message)
                yield sse_message
                
        except Exception as e:
            yield sse_handler.format_event("error", {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        finally:
            yield sse_handler.format_event("stream_end", {
                "message": "Stream ended",
                "timestamp": datetime.now().isoformat()
            })
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@app.post("/debate/stop")
async def stop_debate():
    """Stop the current debate"""
    global active_workflow
    
    if not active_workflow:
        raise HTTPException(status_code=404, detail="No active debate")
    
    active_workflow.stop()
    
    return {
        "status": "stopped",
        "message": "Debate stopped"
    }


@app.get("/debate/events")
async def get_buffered_events(since: Optional[str] = None):
    """
    Get buffered events (for late-joining clients).
    
    Args:
        since: ISO timestamp to get events after
    """
    if since:
        events = event_buffer.get_since(since)
    else:
        events = event_buffer.get_all()
    
    return {
        "count": len(events),
        "events": events
    }


@app.get("/debate/state")
async def get_debate_state():
    """Get full current debate state"""
    global active_workflow
    
    if not active_workflow:
        raise HTTPException(status_code=404, detail="No active debate")
    
    return active_workflow.get_state()


# === Health Check ===

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_debate": active_workflow.is_running if active_workflow else False
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

