"""
Debate Task Module

Provides task templates for debate arguments.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DebateContext(BaseModel):
    """Context for a debate exchange"""
    speaker: str
    argument: str


class DebateArgumentTask(BaseModel):
    """
    Task template for generating debate arguments.
    
    This task creates prompts for agents to respond to in a debate context.
    """
    topic: str = Field(..., description="The debate topic")
    stance: str = Field(..., description="'for' or 'against' the topic")
    debate_history: List[DebateContext] = Field(
        default_factory=list,
        description="Previous exchanges (last 5-10 messages)"
    )
    opponent_last_argument: Optional[str] = Field(
        default=None,
        description="What the opponent just argued"
    )
    personality_note: str = Field(
        default="analytical",
        description="Reminder of agent's argumentation style"
    )
    
    def build_prompt(self) -> str:
        """Build the debate prompt for the agent"""
        
        # Format debate history
        history_text = ""
        if self.debate_history:
            history_lines = [
                f"- {ctx.speaker}: {ctx.argument}"
                for ctx in self.debate_history[-5:]  # Last 5 exchanges
            ]
            history_text = "\n".join(history_lines)
        else:
            history_text = "(This is the opening argument)"
        
        # Build the prompt
        prompt_parts = [
            f"DEBATE TOPIC: {self.topic}",
            f"\nYOUR STANCE: You are arguing {'IN FAVOR OF' if self.stance == 'for' else 'AGAINST'} the proposition.",
            f"\nRECENT DEBATE CONTEXT:\n{history_text}",
        ]
        
        if self.opponent_last_argument:
            prompt_parts.append(
                f"\nOPPONENT'S LAST ARGUMENT:\n{self.opponent_last_argument}"
            )
            prompt_parts.append(
                "\nYOUR TASK: Respond with a strong counter-argument that directly addresses "
                f"the opponent's points. Use your {self.personality_note} style."
            )
        else:
            prompt_parts.append(
                f"\nYOUR TASK: Make a compelling opening argument using your {self.personality_note} style."
            )
        
        prompt_parts.append(
            "\nGUIDELINES:\n"
            "- Keep your response to just once sentence\n"
            "- Be specific and impactful\n"
            "- Stay in character with your personality\n"
            "- Make every word count"
        )
        
        return "\n".join(prompt_parts)
    
    def get_instructions(self) -> List[str]:
        """Get agent instructions for this task"""
        return [
            f"You are participating in a formal debate on: {self.topic}",
            f"Your stance is {'FOR' if self.stance == 'for' else 'AGAINST'} the proposition.",
            f"Argue using your {self.personality_note} style.",
            "Keep responses to just once sentence.",
            "Be persuasive, specific, and impactful.",
        ]


def create_debate_task(
    topic: str,
    stance: str,
    debate_history: List[dict] = None,
    opponent_last_argument: str = None,
    personality_note: str = "analytical"
) -> DebateArgumentTask:
    """
    Factory function to create a DebateArgumentTask.
    
    Args:
        topic: The debate topic
        stance: 'for' or 'against'
        debate_history: List of dicts with 'speaker' and 'argument' keys
        opponent_last_argument: The opponent's last argument
        personality_note: The agent's personality style
        
    Returns:
        DebateArgumentTask instance
    """
    history = []
    if debate_history:
        history = [
            DebateContext(speaker=h.get('speaker', 'Unknown'), argument=h.get('argument', ''))
            for h in debate_history
        ]
    
    return DebateArgumentTask(
        topic=topic,
        stance=stance,
        debate_history=history,
        opponent_last_argument=opponent_last_argument,
        personality_note=personality_note
    )

