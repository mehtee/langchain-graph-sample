"""Pydantic models for structured output."""
from typing import List, Optional
from pydantic import BaseModel, Field


class ProblemAnalysis(BaseModel):
    """Analysis of the problem."""
    problem_type: str = Field(description="Type of problem (e.g., mathematical, logical, creative)")
    key_constraints: List[str] = Field(description="List of key constraints or requirements")
    approach: str = Field(description="Suggested approach to solve the problem")


class Solution(BaseModel):
    """Solution to the problem."""
    answer: str = Field(description="The final answer or solution")
    reasoning_steps: List[str] = Field(description="Step-by-step reasoning that led to the answer")
    confidence: str = Field(description="Confidence level: high, medium, or low")


class Verification(BaseModel):
    """Verification of the solution."""
    is_correct: bool = Field(description="Whether the solution appears correct")
    issues_found: List[str] = Field(description="Any issues or concerns identified")
    final_answer: str = Field(description="The verified final answer")


class GraphState(BaseModel):
    """State passed through the graph."""
    problem: str
    analysis: Optional[ProblemAnalysis] = None
    solution: Optional[Solution] = None
    verification: Optional[Verification] = None
    error: Optional[str] = None
