"""
Moderate Task Module

Provides task templates for debate moderation and summarization.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DebateMessage(BaseModel):
    """A message in the debate transcript"""
    speaker: str
    role: str  # 'proposition' or 'opposition'
    content: str


class VoteEvent(BaseModel):
    """A vote/switch event during the debate"""
    voter: str
    voted_for: str
    vote_type: str  # 'in' or 'out'
    reasoning: Optional[str] = None


class ModerateSummaryTask(BaseModel):
    """
    Task template for moderating and summarizing debates.
    
    The moderator provides objective summaries of debate proceedings.
    """
    topic: str = Field(..., description="The debate topic")
    full_debate_transcript: List[DebateMessage] = Field(
        default_factory=list,
        description="All messages from the debate"
    )
    vote_history: List[VoteEvent] = Field(
        default_factory=list,
        description="All votes and switches that occurred"
    )
    duration_seconds: int = Field(
        default=0,
        description="Total debate duration in seconds"
    )
    
    def build_prompt(self) -> str:
        """Build the moderation summary prompt"""
        
        # Format transcript
        transcript_text = ""
        if self.full_debate_transcript:
            transcript_lines = [
                f"[{msg.role.upper()}] {msg.speaker}: {msg.content}"
                for msg in self.full_debate_transcript
            ]
            transcript_text = "\n\n".join(transcript_lines)
        else:
            transcript_text = "(No transcript available)"
        
        # Format vote history
        vote_text = ""
        if self.vote_history:
            vote_lines = [
                f"- {v.voter} voted '{v.vote_type}' for {v.voted_for}"
                + (f" ({v.reasoning})" if v.reasoning else "")
                for v in self.vote_history
            ]
            vote_text = "\n".join(vote_lines)
        else:
            vote_text = "(No votes recorded)"
        
        # Format duration
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        duration_text = f"{minutes} minutes, {seconds} seconds" if minutes else f"{seconds} seconds"
        
        prompt = f"""MODERATOR SUMMARY TASK

Provide an objective, balanced summary of this debate.

DEBATE TOPIC: {self.topic}

DURATION: {duration_text}

FULL TRANSCRIPT:
{transcript_text}

VOTING EVENTS:
{vote_text}

REQUIRED SUMMARY STRUCTURE:

1. **Overview** (2-3 sentences)
   Briefly describe what the debate was about and how it unfolded.

2. **Key Proposition Arguments** (bullet points)
   List the strongest arguments made in favor of the proposition.

3. **Key Opposition Arguments** (bullet points)
   List the strongest arguments made against the proposition.

4. **Notable Moments** (if any)
   Highlight any switches, particularly strong performances, or turning points.

5. **Conclusion**
   Provide a fair assessment of which side presented the stronger case and why.
   Be objective and acknowledge strengths from both sides.

Remember: You are a neutral moderator. Present facts fairly without personal bias."""

        return prompt
    
    def get_instructions(self) -> List[str]:
        """Get agent instructions for moderation"""
        return [
            "You are a neutral, objective debate moderator.",
            f"Summarize the debate on: {self.topic}",
            "Be fair and balanced in your assessment.",
            "Follow the required summary structure exactly.",
            "Acknowledge strong points from both sides.",
        ]


def create_moderate_task(
    topic: str,
    full_debate_transcript: List[dict] = None,
    vote_history: List[dict] = None,
    duration_seconds: int = 0
) -> ModerateSummaryTask:
    """
    Factory function to create a ModerateSummaryTask.
    
    Args:
        topic: The debate topic
        full_debate_transcript: List of dicts with 'speaker', 'role', 'content'
        vote_history: List of dicts with 'voter', 'voted_for', 'vote_type', 'reasoning'
        duration_seconds: Total debate duration
        
    Returns:
        ModerateSummaryTask instance
    """
    transcript = []
    if full_debate_transcript:
        transcript = [
            DebateMessage(
                speaker=msg.get('speaker', 'Unknown'),
                role=msg.get('role', 'unknown'),
                content=msg.get('content', '')
            )
            for msg in full_debate_transcript
        ]
    
    votes = []
    if vote_history:
        votes = [
            VoteEvent(
                voter=v.get('voter', 'Unknown'),
                voted_for=v.get('voted_for', 'Unknown'),
                vote_type=v.get('vote_type', 'in'),
                reasoning=v.get('reasoning')
            )
            for v in vote_history
        ]
    
    return ModerateSummaryTask(
        topic=topic,
        full_debate_transcript=transcript,
        vote_history=votes,
        duration_seconds=duration_seconds
    )

