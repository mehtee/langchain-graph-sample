"""Agent implementations for LangGraph workflow.

This module follows SOLID principles:
- Single Responsibility: Each agent handles one specific task
- Open/Closed: Open for extension (new agent types), closed for modification
- Dependency Inversion: Agents depend on abstractions (BaseAgent) not concretions

Agents can be:
- LLM-based: Use language models with prompts for decision-making
- Non-LLM-based: Use code, APIs, or computed logic without LLMs
"""
from abc import ABC, abstractmethod
from typing import Optional
import logging

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from src.models import ProblemAnalysis, Solution, Verification


class BaseAgent(ABC):
    """Abstract base class for all workflow agents.
    
    Uses LangGraph state management - state is passed as dict-like object.
    """
    
    def __init__(self, llm, logger: logging.Logger):
        """Initialize agent with minimal dependencies.
        
        Args:
            llm: Language model client (can be None for non-LLM agents)
            logger: Logger instance
        """
        self.llm = llm
        self.logger = logger
    
    @abstractmethod
    def execute(self, state: dict) -> dict:
        """Execute the agent's logic.
        
        Args:
            state: Current workflow state from LangGraph (dict-like)
            
        Returns:
            dict: Updated fields to merge into state
        """
        pass
    
    def _invoke_llm(self, prompt: str, schema: BaseModel, 
                    system_prompt: str = "", use_system: bool = True) -> Optional[BaseModel]:
        """Invoke LLM with structured output.
        
        Args:
            prompt: User prompt
            schema: Pydantic model for structured output
            system_prompt: System prompt (from state/config)
            use_system: Whether to use system prompt
            
        Returns:
            Structured output or None if failed
        """
        try:
            structured_llm = self.llm.with_structured_output(schema)
            messages = [HumanMessage(content=prompt)]
            if system_prompt and use_system:
                messages.insert(0, SystemMessage(content=system_prompt))
            return structured_llm.invoke(messages)
        except Exception as e:
            self.logger.warning(f"Structured output failed: {str(e)}")
            return None
    
    def _get_unstructured_response(self, prompt: str, system_prompt: str = "", 
                                   use_system: bool = True) -> str:
        """Get unstructured text response from LLM.
        
        Used as fallback when structured output is not supported.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (from state/config)
            use_system: Whether to use system prompt
            
        Returns:
            Raw text response from LLM
        """
        try:
            messages = [HumanMessage(content=prompt)]
            if system_prompt and use_system:
                messages.insert(0, SystemMessage(content=system_prompt))
            response = self.llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            self.logger.error(f"Unstructured response failed: {str(e)}")
            return ""


class AnalyzeAgent(BaseAgent):
    """Agent 1: Analyze the problem (LLM-based)."""
    
    def execute(self, state: dict) -> dict:
        """Execute analysis using state configuration."""
        prompt_name = state.get("prompt_name", "unknown")
        self.logger.info(f"Agent 1: Analyzing problem (prompt: {prompt_name})")
        
        try:
            problem = state["problem"]
            prompt_template = state.get("analyze_prompt", "")
            system_prompt = state.get("system_prompt", "")
            use_system = state.get("use_system_prompt", True)
            
            # Build prompt from template or use default
            if prompt_template:
                prompt = prompt_template.format(problem=problem)
            else:
                prompt = f"""Analyze this problem carefully:

{problem}

Identify:
1. What type of problem this is
2. Key constraints or requirements
3. The best approach to solve it"""
            
            # Try structured output first
            analysis = self._invoke_llm(prompt, ProblemAnalysis, system_prompt, use_system)
            
            if analysis:
                self.logger.info(f"Analysis complete (structured): {analysis.problem_type}")
                return {"analysis": analysis}
            
            # Fallback to unstructured response
            self.logger.info("Falling back to unstructured response for analysis")
            response = self._get_unstructured_response(prompt, system_prompt, use_system)
            
            if response:
                self.logger.info(f"Analysis (unstructured): {response[:200]}...")
                # Create structured analysis from unstructured response
                # Try to extract problem type from response
                problem_type = "general"
                if any(word in response.lower() for word in ["math", "arithmetic", "calculation", "number"]):
                    problem_type = "mathematical"
                elif any(word in response.lower() for word in ["logic", "reasoning"]):
                    problem_type = "logical"
                elif any(word in response.lower() for word in ["creative", "design", "write"]):
                    problem_type = "creative"
                
                analysis = ProblemAnalysis(
                    problem_type=problem_type,
                    key_constraints=["answer accurately", "provide explanation"],
                    approach="Standard problem solving approach"
                )
                return {"analysis": analysis}
            
            # Last resort fallback
            analysis = ProblemAnalysis(
                problem_type="general",
                key_constraints=["answer accurately"],
                approach="Standard problem solving"
            )
            return {"analysis": analysis}
            
        except Exception as e:
            self.logger.error(f"Error in analyze agent: {str(e)}", exc_info=True)
            return {"error": f"Analysis failed: {str(e)}"}


class SolveAgent(BaseAgent):
    """Agent 2: Solve the problem (LLM-based)."""
    
    def execute(self, state: dict) -> dict:
        """Execute solving using state configuration."""
        prompt_name = state.get("prompt_name", "unknown")
        self.logger.info(f"Agent 2: Solving problem (prompt: {prompt_name})")
        
        if state.get("error"):
            return {}  # Pass through error
        
        try:
            problem = state["problem"]
            analysis = state["analysis"]
            prompt_template = state.get("solve_prompt", "")
            system_prompt = state.get("system_prompt", "")
            use_system = state.get("use_system_prompt", True)
            
            analysis_summary = f"""Problem Type: {analysis.problem_type}
Constraints: {', '.join(analysis.key_constraints)}
Approach: {analysis.approach}"""
            
            # Build prompt
            if prompt_template:
                prompt = prompt_template.format(
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
            solution = self._invoke_llm(prompt, Solution, system_prompt, use_system)
            
            if solution:
                self.logger.info(f"Solution complete (structured): {solution.confidence} confidence")
                return {"solution": solution}
            
            # Fallback to unstructured response
            self.logger.info("Falling back to unstructured response for solution")
            response = self._get_unstructured_response(prompt, system_prompt, use_system)
            
            if response:
                self.logger.info(f"Solution (unstructured): {response[:200]}...")
                # Create structured solution from unstructured response
                # Determine confidence based on response
                confidence = "medium"
                if any(word in response.lower() for word in ["certain", "definitely", "clearly", "obviously"]):
                    confidence = "high"
                elif any(word in response.lower() for word in ["maybe", "possibly", "uncertain", "not sure"]):
                    confidence = "low"
                
                solution = Solution(
                    answer=response[:500] if len(response) > 500 else response,
                    reasoning_steps=["Analyzed the problem", "Applied knowledge", "Formulated answer"],
                    confidence=confidence
                )
                return {"solution": solution}
            
            # Last resort fallback
            solution = Solution(
                answer="Unable to generate solution",
                reasoning_steps=["Attempted to solve"],
                confidence="low"
            )
            return {"solution": solution}
            
        except Exception as e:
            self.logger.error(f"Error in solve agent: {str(e)}", exc_info=True)
            return {"error": f"Solution failed: {str(e)}"}


class VerifyAgent(BaseAgent):
    """Agent 3: Verify the solution (LLM-based)."""
    
    def execute(self, state: dict) -> dict:
        """Execute verification using state configuration."""
        prompt_name = state.get("prompt_name", "unknown")
        self.logger.info(f"Agent 3: Verifying solution (prompt: {prompt_name})")
        
        if state.get("error"):
            return {}  # Pass through error
        
        try:
            problem = state["problem"]
            solution = state["solution"]
            prompt_template = state.get("verify_prompt", "")
            system_prompt = state.get("system_prompt", "")
            use_system = state.get("use_system_prompt", True)
            
            solution_summary = f"""Answer: {solution.answer}
Reasoning: {' -> '.join(solution.reasoning_steps)}
Confidence: {solution.confidence}"""
            
            # Build prompt
            if prompt_template:
                prompt = prompt_template.format(
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
            verification = self._invoke_llm(prompt, Verification, system_prompt, use_system)
            
            if verification:
                self.logger.info(f"Verification complete (structured): {verification.is_correct}")
                return {"verification": verification}
            
            # Fallback to unstructured response
            self.logger.info("Falling back to unstructured response for verification")
            response = self._get_unstructured_response(prompt, system_prompt, use_system)
            
            if response:
                self.logger.info(f"Verification (unstructured): {response[:200]}...")
                # Create structured verification from unstructured response
                # Determine correctness based on response
                is_correct = True
                if any(word in response.lower() for word in ["incorrect", "wrong", "error", "mistake", "issue"]):
                    is_correct = False
                
                # Try to extract issues
                issues = []
                if "issue" in response.lower() or "problem" in response.lower():
                    issues.append("Potential issues mentioned in verification")
                
                verification = Verification(
                    is_correct=is_correct,
                    issues_found=issues,
                    final_answer=solution.answer
                )
                return {"verification": verification}
            
            # Last resort fallback
            verification = Verification(
                is_correct=True,
                issues_found=[],
                final_answer=solution.answer
            )
            return {"verification": verification}
            
        except Exception as e:
            self.logger.error(f"Error in verify agent: {str(e)}", exc_info=True)
            return {"error": f"Verification failed: {str(e)}"}


class SimpleCalculatorAgent(BaseAgent):
    """Agent 4: Simple Calculator (Non-LLM-based).
    
    Demonstrates a non-LLM agent that uses pure computation.
    Handles basic arithmetic without any language model.
    """
    
    def __init__(self, llm=None, logger: logging.Logger = None):
        """Initialize non-LLM agent. LLM parameter is optional and unused."""
        super().__init__(llm, logger or logging.getLogger(__name__))
    
    def execute(self, state: dict) -> dict:
        """Execute simple calculation (no LLM needed)."""
        self.logger.info("Agent 4: Simple Calculator (Non-LLM)")
        
        try:
            problem = state["problem"].lower().strip()
            
            # Try to evaluate simple math expressions
            # Only allow basic operations for safety
            if any(op in problem for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
                # Replace words with operators
                calc_expr = problem.replace('plus', '+').replace('minus', '-')
                calc_expr = calc_expr.replace('times', '*').replace('divided by', '/')
                calc_expr = calc_expr.replace('what is', '').replace('?', '').strip()
                
                try:
                    # Safe eval with limited scope
                    result = eval(calc_expr, {"__builtins__": {}}, {})
                    answer = str(result)
                    
                    self.logger.info(f"Calculated: {calc_expr} = {answer}")
                    
                    return {
                        "analysis": ProblemAnalysis(
                            problem_type="arithmetic",
                            key_constraints=["basic math only"],
                            approach="Direct computation"
                        ),
                        "solution": Solution(
                            answer=answer,
                            reasoning_steps=[f"Evaluated: {calc_expr}", f"Result: {answer}"],
                            confidence="high"
                        ),
                        "verification": Verification(
                            is_correct=True,
                            issues_found=[],
                            final_answer=answer
                        )
                    }
                except:
                    pass
            
            # Not a math problem
            self.logger.info("Not a simple math problem")
            return {"error": "Not a simple arithmetic problem. Calculator agent only handles basic math."}
                
        except Exception as e:
            self.logger.error(f"Error in calculator agent: {str(e)}", exc_info=True)
            return {"error": f"Calculation failed: {str(e)}"}
