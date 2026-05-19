from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated, Dict

# Type alias for TraceID
TraceID = UUID

class AgentRole(str, Enum):
    ANALYST = "ANALYST"
    GENERATION = "GENERATION"
    CODING = "CODING"
    CLI = "CLI"
    VALIDATION = "VALIDATION"
    SECURITY = "SECURITY"
    CRITIC = "CRITIC"
    OPTIMIZER = "OPTIMIZER"
    SOLUTION = "SOLUTION"
    AGGREGATOR = "AGGREGATOR"
    TIMELINE = "TIMELINE"
    FIT = "FIT"
    CORRELATION = "CORRELATION"
    GEMMA_A = "GEMMA_A"
    GEMMA_B = "GEMMA_B"

class AgentMode(str, Enum):
    EXECUTION = "EXECUTION"
    DEBATE = "DEBATE"

class Argument(BaseModel):
    agent_id: str
    role: AgentRole
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    round: int
    is_pro: bool = True

class DebateOutcome(BaseModel):
    debate_id: UUID = Field(default_factory=uuid4)
    final_decision: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    rejected_alternatives: List[str] = Field(default_factory=list)
    arguments: List[Argument] = Field(default_factory=list)
    conflict_points: List[str] = Field(default_factory=list)
    reasoning_trace: str = ""
    agent_elo_updates: Dict[str, float] = Field(default_factory=dict)
