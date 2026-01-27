"""LangGraph workflow definition."""
from typing import Any, Dict
from langgraph.graph import StateGraph, END

from src.models import GraphState
from src.nodes import AnalyzeNode, SolveNode, VerifyNode


class WorkflowGraph:
    """LangGraph workflow for multi-step problem solving.
    
    Uses a node-based architecture following SOLID principles:
    - Each node is a separate class with single responsibility
    - Nodes can be extended without modifying this class (Open/Closed)
    - Nodes depend on abstractions (BaseNode), not concrete implementations
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
        """Build the LangGraph workflow with independent node classes."""
        workflow = StateGraph(GraphState)
        
        # Get node-specific configurations
        nodes_config = self.prompt_config.get('nodes', {})
        
        # Create node instances (dependency injection)
        analyze_config = nodes_config.get('analyze', {})
        solve_config = nodes_config.get('solve', {})
        verify_config = nodes_config.get('verify', {})
        
        analyze_node = AnalyzeNode(
            self.llm, self.logger, self.system_prompt, 
            self.use_system_prompt and analyze_config.get('system_prompt_included', True),
            analyze_config.get('prompt', ''),
            self.prompt_name
        )
        solve_node = SolveNode(
            self.llm, self.logger, self.system_prompt, 
            self.use_system_prompt and solve_config.get('system_prompt_included', True),
            solve_config.get('prompt', ''),
            self.prompt_name
        )
        verify_node = VerifyNode(
            self.llm, self.logger, self.system_prompt, 
            self.use_system_prompt and verify_config.get('system_prompt_included', True),
            verify_config.get('prompt', ''),
            self.prompt_name
        )
        
        # Add nodes with their execute methods
        workflow.add_node("analyze", analyze_node.execute)
        workflow.add_node("solve", solve_node.execute)
        workflow.add_node("verify", verify_node.execute)
        
        # Add edges
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "solve")
        workflow.add_edge("solve", "verify")
        workflow.add_edge("verify", END)
        
        return workflow.compile()
    
    def run(self, problem: str) -> dict:
        """Execute the workflow."""
        self.logger.info(f"Starting workflow with prompt: {self.prompt_name}, problem: {problem}")
        initial_state = GraphState(problem=problem)
        final_state = self.graph.invoke(initial_state)
        self.logger.info("Workflow completed")
        return final_state
