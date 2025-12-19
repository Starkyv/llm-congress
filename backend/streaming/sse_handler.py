"""
SSE (Server-Sent Events) Handler

Handles streaming events to clients via Server-Sent Events protocol.
Compatible with Agno's event streaming and custom events.
"""

import json
import asyncio
from typing import AsyncGenerator, Generator, Any, Dict, Optional, Union
from datetime import datetime
from dataclasses import asdict, is_dataclass

from .events import (
    DebateEventType,
    event_to_sse,
    CustomEvent,
)


class SSEHandler:
    """
    Handler for Server-Sent Events streaming.
    
    Converts debate events to SSE format and manages client connections.
    
    Usage:
        handler = SSEHandler()
        
        # Stream events
        async for sse_message in handler.stream_events(event_generator):
            yield sse_message
    """
    
    def __init__(self, heartbeat_interval: float = 15.0):
        """
        Initialize SSE handler.
        
        Args:
            heartbeat_interval: Seconds between keepalive pings
        """
        self.heartbeat_interval = heartbeat_interval
        self.is_streaming = False
    
    def format_event(
        self,
        event_type: str,
        data: Union[Dict[str, Any], str, Any],
        event_id: Optional[str] = None
    ) -> str:
        """
        Format data as SSE message.
        
        Args:
            event_type: The event type name
            data: Event data (dict, string, or dataclass)
            event_id: Optional event ID
            
        Returns:
            SSE formatted string
        """
        lines = []
        
        if event_id:
            lines.append(f"id: {event_id}")
        
        lines.append(f"event: {event_type}")
        
        # Handle different data types
        if is_dataclass(data):
            data_str = json.dumps(asdict(data), default=str)
        elif isinstance(data, dict):
            data_str = json.dumps(data, default=str)
        elif isinstance(data, str):
            data_str = data
        else:
            data_str = json.dumps({"value": str(data)})
        
        lines.append(f"data: {data_str}")
        lines.append("")  # Empty line to end message
        lines.append("")
        
        return "\n".join(lines)
    
    def format_custom_event(self, event: CustomEvent) -> str:
        """
        Format an Agno CustomEvent as SSE message.
        
        Args:
            event: The custom event
            
        Returns:
            SSE formatted string
        """
        return event_to_sse(event)
    
    def heartbeat(self) -> str:
        """
        Generate a heartbeat/keepalive message.
        
        Returns:
            SSE comment for keepalive
        """
        return f": heartbeat {datetime.now().isoformat()}\n\n"
    
    async def stream_events(
        self,
        event_source: Union[Generator, AsyncGenerator],
        include_heartbeat: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Stream events from a generator as SSE messages.
        
        Args:
            event_source: Generator yielding events
            include_heartbeat: Whether to send periodic heartbeats
            
        Yields:
            SSE formatted strings
        """
        self.is_streaming = True
        last_heartbeat = datetime.now()
        
        try:
            # Handle both sync and async generators
            if hasattr(event_source, '__anext__'):
                # Async generator
                async for event in event_source:
                    yield self._process_event(event)
                    
                    # Check heartbeat
                    if include_heartbeat:
                        now = datetime.now()
                        if (now - last_heartbeat).seconds >= self.heartbeat_interval:
                            yield self.heartbeat()
                            last_heartbeat = now
            else:
                # Sync generator - wrap in async
                for event in event_source:
                    yield self._process_event(event)
                    
                    # Allow other tasks to run
                    await asyncio.sleep(0)
                    
                    # Check heartbeat
                    if include_heartbeat:
                        now = datetime.now()
                        if (now - last_heartbeat).seconds >= self.heartbeat_interval:
                            yield self.heartbeat()
                            last_heartbeat = now
                            
        finally:
            self.is_streaming = False
    
    def _process_event(self, event: Any) -> str:
        """
        Process an event into SSE format.
        
        Args:
            event: Event to process
            
        Returns:
            SSE formatted string
        """
        # Handle Agno CustomEvent
        if isinstance(event, CustomEvent):
            return self.format_custom_event(event)
        
        # Handle dict with event_type
        if isinstance(event, dict):
            event_type = event.get('event_type', event.get('type', 'message'))
            data = event.get('data', event)
            return self.format_event(event_type, data)
        
        # Handle object with event_type attribute
        if hasattr(event, 'event_type'):
            event_type = event.event_type
            if hasattr(event_type, 'value'):
                event_type = event_type.value
            
            if hasattr(event, 'data'):
                data = event.data
            elif is_dataclass(event):
                data = asdict(event)
            else:
                data = {"event": str(event)}
            
            return self.format_event(event_type, data)
        
        # Fallback: treat as generic message
        return self.format_event("message", {"content": str(event)})
    
    def stop(self):
        """Stop streaming (sets flag for graceful shutdown)"""
        self.is_streaming = False


class EventBuffer:
    """
    Buffer for collecting and replaying events.
    
    Useful for:
    - Late-joining clients
    - Event logging
    - Debugging
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize event buffer.
        
        Args:
            max_size: Maximum events to store
        """
        self.events: list = []
        self.max_size = max_size
    
    def add(self, event: Any):
        """Add an event to the buffer"""
        self.events.append({
            "event": event,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim if over limit
        if len(self.events) > self.max_size:
            self.events = self.events[-self.max_size:]
    
    def get_all(self) -> list:
        """Get all buffered events"""
        return [e["event"] for e in self.events]
    
    def get_since(self, timestamp: str) -> list:
        """Get events since a timestamp"""
        return [
            e["event"] for e in self.events
            if e["timestamp"] > timestamp
        ]
    
    def clear(self):
        """Clear all events"""
        self.events = []
    
    def __len__(self) -> int:
        return len(self.events)

