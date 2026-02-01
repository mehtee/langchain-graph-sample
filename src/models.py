"""Pydantic models for structured output."""
from typing import List, Optional, TypedDict
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


class GraphState(TypedDict, total=False):
    """State passed through the graph.
    
    Uses TypedDict (not Pydantic BaseModel) as required by LangGraph.
    Includes both data and configuration that agents need.
    """
    # Core data
    problem: str
    analysis: Optional[ProblemAnalysis]
    solution: Optional[Solution]
    verification: Optional[Verification]
    error: Optional[str]
    
    # Configuration (passed through state instead of agent properties)
    system_prompt: Optional[str]
    use_system_prompt: Optional[bool]
    prompt_name: Optional[str]
    analyze_prompt: Optional[str]
    solve_prompt: Optional[str]
    verify_prompt: Optional[str]
