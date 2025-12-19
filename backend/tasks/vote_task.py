"""
Vote Task Module

Provides task templates for vote evaluation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import json
import re


class DebateExchange(BaseModel):
    """A single exchange in the debate"""
    speaker: str
    argument: str


class VoteResult(BaseModel):
    """The result of a vote evaluation"""
    vote: str = Field(..., description="'in' or 'out'")
    reasoning: str = Field(..., description="Brief explanation for the vote")


class VoteEvaluationTask(BaseModel):
    """
    Task template for evaluating debate performance and casting votes.
    
    Agents use this to decide whether a debater should stay 'in' or be voted 'out'.
    """
    current_debater_name: str = Field(..., description="Name of the debater being evaluated")
    recent_exchanges: List[DebateExchange] = Field(
        default_factory=list,
        description="Last 3-5 debate turns"
    )
    evaluation_criteria: str = Field(
        default="argument strength, evidence quality, persuasiveness, and response to opponent",
        description="What to evaluate"
    )
    voter_personality: str = Field(
        default="analytical",
        description="How this voter judges (their personality type)"
    )
    
    def build_prompt(self) -> str:
        """Build the vote evaluation prompt"""
        
        # Format recent exchanges
        exchanges_text = ""
        if self.recent_exchanges:
            exchange_lines = [
                f"- {ex.speaker}: {ex.argument}"
                for ex in self.recent_exchanges[-5:]
            ]
            exchanges_text = "\n".join(exchange_lines)
        else:
            exchanges_text = "(No exchanges yet)"
        
        prompt = f"""VOTE EVALUATION TASK

You are evaluating {self.current_debater_name}'s debate performance.

RECENT EXCHANGES:
{exchanges_text}

EVALUATION CRITERIA:
Judge based on: {self.evaluation_criteria}

YOUR PERSPECTIVE:
Vote from YOUR perspective as a {self.voter_personality} personality. 
Consider what matters most to someone with your viewpoint.

RESPONSE FORMAT:
You MUST respond ONLY with valid JSON in this exact format:
{{"vote": "in", "reasoning": "Your 1-2 sentence explanation"}}

OR

{{"vote": "out", "reasoning": "Your 1-2 sentence explanation"}}

Respond with ONLY the JSON, no other text."""

        return prompt
    
    def get_instructions(self) -> List[str]:
        """Get agent instructions for voting"""
        return [
            f"You are evaluating {self.current_debater_name}'s performance.",
            f"Judge as a {self.voter_personality} personality.",
            "Respond ONLY with valid JSON.",
            'Format: {"vote": "in" or "out", "reasoning": "brief explanation"}',
        ]
    
    @staticmethod
    def parse_vote_response(response: str) -> Optional[VoteResult]:
        """
        Parse the agent's vote response into a VoteResult.
        
        Args:
            response: The raw response string from the agent
            
        Returns:
            VoteResult if parsing successful, None otherwise
        """
        try:
            # Try to extract JSON from the response
            # Handle cases where there might be extra text
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                vote = data.get('vote', '').lower().strip()
                reasoning = data.get('reasoning', '')
                
                if vote in ['in', 'out']:
                    return VoteResult(vote=vote, reasoning=reasoning)
            
            return None
        except (json.JSONDecodeError, KeyError, AttributeError):
            return None


def create_vote_task(
    current_debater_name: str,
    recent_exchanges: List[dict] = None,
    evaluation_criteria: str = None,
    voter_personality: str = "analytical"
) -> VoteEvaluationTask:
    """
    Factory function to create a VoteEvaluationTask.
    
    Args:
        current_debater_name: Name of the debater being evaluated
        recent_exchanges: List of dicts with 'speaker' and 'argument' keys
        evaluation_criteria: What to evaluate
        voter_personality: The voter's personality type
        
    Returns:
        VoteEvaluationTask instance
    """
    exchanges = []
    if recent_exchanges:
        exchanges = [
            DebateExchange(
                speaker=ex.get('speaker', 'Unknown'),
                argument=ex.get('argument', '')
            )
            for ex in recent_exchanges
        ]
    
    criteria = evaluation_criteria or (
        "argument strength, evidence quality, persuasiveness, and response to opponent"
    )
    
    return VoteEvaluationTask(
        current_debater_name=current_debater_name,
        recent_exchanges=exchanges,
        evaluation_criteria=criteria,
        voter_personality=voter_personality
    )

