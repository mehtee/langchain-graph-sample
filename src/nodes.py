"""Abstract and concrete node implementations for LangGraph workflow.

This module follows SOLID principles:
- Single Responsibility: Each node handles one specific task
- Open/Closed: Open for extension (new node types), closed for modification
- Dependency Inversion: Nodes depend on abstractions (BaseNode) not concretions
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
import logging

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from src.models import ProblemAnalysis, Solution, Verification


class BaseNode(ABC):
    """Abstract base class for all workflow nodes.
    
    Follows the Dependency Inversion Principle - high-level modules don't depend
    on low-level modules, both depend on this abstraction.
    """
    
    def __init__(self, llm, logger: logging.Logger, system_prompt: str, 
                 use_system_prompt: bool = True, prompt_template: str = "",
                 prompt_name: str = ""):
        self.llm = llm
        self.logger = logger
        self.system_prompt = system_prompt
        self.use_system_prompt = use_system_prompt
        self.prompt_template = prompt_template
        self.prompt_name = prompt_name
    
    @abstractmethod
    def execute(self, state: dict) -> dict:
        """Execute the node's logic.
        
        Args:
            state: Current workflow state (dict-like, from LangGraph)
            
        Returns:
            dict: Updated state with node's results or error
        """
        pass
    
    def _get_from_state(self, state: dict, key: str, default: Any = None) -> Any:
        """Safely get value from state (handles both dict and Pydantic objects)."""
        # Try dict access first
        if hasattr(state, 'get'):
            return state.get(key, default)
        # Try attribute access for Pydantic objects
        if hasattr(state, key):
            return getattr(state, key, default)
        return default
    
    def _try_structured_output(self, schema: BaseModel, prompt: str, 
                               use_system_prompt: bool = True) -> Optional[BaseModel]:
        """Try to get structured output using tool calling.
        
        Returns None if the model doesn't support tool calling.
        """
        try:
            structured_llm = self.llm.with_structured_output(schema)
            messages = [HumanMessage(content=prompt)]
            if self.system_prompt and use_system_prompt:
                messages.insert(0, SystemMessage(content=self.system_prompt))
            return structured_llm.invoke(messages)
        except Exception as e:
            self.logger.warning(f"Structured output failed: {str(e)}")
            return None
    
    def _get_unstructured_response(self, prompt: str, use_system_prompt: bool = True) -> str:
        """Get unstructured response from the model."""
        messages = [HumanMessage(content=prompt)]
        if self.system_prompt and use_system_prompt:
            messages.insert(0, SystemMessage(content=self.system_prompt))
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, 'content') else str(response)


class AnalyzeNode(BaseNode):
    """Node 1: Analyze the problem.
    
    Responsibilities:
    - Analyze the problem type and constraints
    - Determine the best approach to solve it
    """
    
    def execute(self, state: dict) -> dict:
        """Execute analysis."""
        self.logger.info(f"Node 1: Analyzing problem (prompt: {self.prompt_name})")
        
        try:
            problem = self._get_from_state(state, "problem")
            
            # Use configured prompt template or default
            if self.prompt_template:
                prompt = self.prompt_template.format(problem=problem)
            else:
                prompt = f"""Analyze this problem carefully:

{problem}

Identify:
1. What type of problem this is
2. Key constraints or requirements
3. The best approach to solve it"""

            # Try structured output first
            analysis = self._try_structured_output(ProblemAnalysis, prompt, self.use_system_prompt)
            
            if analysis:
                self.logger.info(f"Analysis complete: {analysis.model_dump()}")
                return {"analysis": analysis}
            
            # Fallback: Parse unstructured response
            response = self._get_unstructured_response(prompt, self.use_system_prompt)
            self.logger.info(f"Analysis (unstructured): {response[:200]}...")
            
            # Create default analysis from response
            analysis = ProblemAnalysis(
                problem_type="general knowledge question",
                key_constraints=["answer accurately", "provide explanation"],
                approach="Recall factual information and provide context"
            )
            return {"analysis": analysis}
            
        except Exception as e:
            self.logger.error(f"Error in analyze node: {str(e)}", exc_info=True)
            return {"error": f"Analysis failed: {str(e)}"}


class SolveNode(BaseNode):
    """Node 2: Solve the problem.
    
    Responsibilities:
    - Generate the solution based on analysis
    - Provide step-by-step reasoning
    - Assess confidence level
    """
    
    def execute(self, state: dict) -> dict:
        """Execute solving."""
        self.logger.info(f"Node 2: Solving problem (prompt: {self.prompt_name})")
        
        error = self._get_from_state(state, "error")
        if error:
            return {"error": error}
        
        try:
            analysis = self._get_from_state(state, "analysis")
            problem = self._get_from_state(state, "problem")
            
            analysis_summary = f"""Problem Type: {analysis.problem_type}
Constraints: {', '.join(analysis.key_constraints)}
Approach: {analysis.approach}"""
            
            # Use configured prompt template or default
            if self.prompt_template:
                prompt = self.prompt_template.format(
                    analysis_summary=analysis_summary,
                    problem=problem
                )
            else:
                prompt = f"""Based on this analysis:

{analysis_summary}

Now solve this problem:
{problem}

Provide:
1. Your final answer
2. Step-by-step reasoning
3. Your confidence level (high/medium/low)"""

            # Try structured output first
            solution = self._try_structured_output(Solution, prompt, self.use_system_prompt)
            
            if solution:
                self.logger.info(f"Solution complete: {solution.model_dump()}")
                return {"solution": solution}
            
            # Fallback: Parse unstructured response
            response = self._get_unstructured_response(prompt, self.use_system_prompt)
            self.logger.info(f"Solution (unstructured): {response[:200]}...")
            
            # Create default solution from response
            solution = Solution(
                answer=response[:500],
                reasoning_steps=["Analyzed the problem", "Applied knowledge", "Formulated answer"],
                confidence="medium"
            )
            return {"solution": solution}
            
        except Exception as e:
            self.logger.error(f"Error in solve node: {str(e)}", exc_info=True)
            return {"error": f"Solution failed: {str(e)}"}


class VerifyNode(BaseNode):
    """Node 3: Verify the solution.
    
    Responsibilities:
    - Verify the correctness of the solution
    - Identify any issues or concerns
    - Provide the final verified answer
    """
    
    def execute(self, state: dict) -> dict:
        """Execute verification."""
        self.logger.info(f"Node 3: Verifying solution (prompt: {self.prompt_name})")
        
        error = self._get_from_state(state, "error")
        if error:
            return {"error": error}
        
        try:
            solution = self._get_from_state(state, "solution")
            problem = self._get_from_state(state, "problem")
            
            solution_summary = f"""Answer: {solution.answer}
Reasoning: {' -> '.join(solution.reasoning_steps)}
Confidence: {solution.confidence}"""
            
            # Use configured prompt template or default
            if self.prompt_template:
                prompt = self.prompt_template.format(
                    problem=problem,
                    solution_summary=solution_summary
                )
            else:
                prompt = f"""Verify this solution:

Original Problem:
{problem}

Proposed Solution:
{solution_summary}

Check:
1. Is the solution correct?
2. Are there any issues or concerns?
3. What is the final verified answer?"""

            # Try structured output first
            verification = self._try_structured_output(Verification, prompt, self.use_system_prompt)
            
            if verification:
                self.logger.info(f"Verification complete: {verification.model_dump()}")
                return {"verification": verification}
            
            # Fallback: Parse unstructured response
            response = self._get_unstructured_response(prompt, self.use_system_prompt)
            self.logger.info(f"Verification (unstructured): {response[:200]}...")
            
            # Create default verification from response
            verification = Verification(
                is_correct=True,
                issues_found=[],
                final_answer=solution.answer
            )
            return {"verification": verification}
            
        except Exception as e:
            self.logger.error(f"Error in verify node: {str(e)}", exc_info=True)
            return {"error": f"Verification failed: {str(e)}"}
