"""LangGraph workflow definition."""
from typing import Any, Dict
from langgraph.graph import StateGraph, END

from src.models import GraphState
from src.agents import AnalyzeAgent, SolveAgent, VerifyAgent


class WorkflowGraph:
    """LangGraph workflow for multi-step problem solving.
    
    Uses an agent-based architecture following SOLID principles:
    - Each agent is a separate class with single responsibility
    - Agents can be extended without modifying this class (Open/Closed)
    - Agents depend on abstractions (BaseAgent), not concrete implementations
    
    Configuration is passed through state instead of stored in agent properties.
    """
    
    def __init__(self, llm_client, logger, system_prompt: str, 
                 use_system_prompt: bool = True, prompt_config: Dict[str, Any] = None,
                 prompt_name: str = ""):
        self.llm = llm_client
        self.logger = logger
        self.system_prompt = system_prompt
        self.use_system_prompt = use_system_prompt
        self.prompt_config = prompt_config or {}
        self.prompt_name = prompt_name
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow with independent agent classes."""
        workflow = StateGraph(GraphState)
        
        # Create agent instances with minimal dependencies
        # Configuration will be passed through state
        analyze_agent = AnalyzeAgent(self.llm, self.logger)
        solve_agent = SolveAgent(self.llm, self.logger)
        verify_agent = VerifyAgent(self.llm, self.logger)
        
        # Add agents as nodes
        workflow.add_node("analyze", analyze_agent.execute)
        workflow.add_node("solve", solve_agent.execute)
        workflow.add_node("verify", verify_agent.execute)
        
        # Add edges
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "solve")
        workflow.add_edge("solve", "verify")
        workflow.add_edge("verify", END)
        
        return workflow.compile()
    
    def run(self, problem: str) -> dict:
        """Execute the workflow with configuration in state."""
        self.logger.info(f"Starting workflow with prompt: {self.prompt_name}, problem: {problem}")
        
        # Get agent-specific configurations
        agents_config = self.prompt_config.get('agents', {})
        analyze_config = agents_config.get('analyze', {})
        solve_config = agents_config.get('solve', {})
        verify_config = agents_config.get('verify', {})
        
        # Build initial state as a dict (not Pydantic model)
        initial_state: GraphState = {
            "problem": problem,
            # Pass configuration through state
            "system_prompt": self.system_prompt,
            "use_system_prompt": self.use_system_prompt,
            "prompt_name": self.prompt_name,
            # Agent-specific prompts
            "analyze_prompt": analyze_config.get('prompt', ''),
            "solve_prompt": solve_config.get('prompt', ''),
            "verify_prompt": verify_config.get('prompt', '')
        }
        
        final_state = self.graph.invoke(initial_state)
        self.logger.info("Workflow completed")
        return final_state
