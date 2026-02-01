"""
Example: How to extend the graph builder with new nodes

This demonstrates the extensibility of the registry-based approach.
Adding a new node requires ZERO changes to existing code!
"""

from simple_graph_builder import (
    Node, NodeConfig, NodeRegistry, GraphConfig, get_graph,
    MessagesState
)
from pydantic import Field
from IPython.display import display, Image
from langchain_core.runnables.graph import MermaidDrawMethod


# ============================================================================
# Example 1: Add a simple preprocessing node
# ============================================================================

class PreprocessConfig(NodeConfig):
    normalize: bool = Field(default=True)
    remove_stopwords: bool = Field(default=False)


@NodeRegistry.register("preprocess")
class PreprocessNode(Node):
    @classmethod
    def get_config_class(cls):
        return PreprocessConfig
    
    @classmethod
    def get_node_type(cls):
        return "ir"  # Runs before generate
    
    def execute(self, state: MessagesState) -> MessagesState:
        # Your preprocessing logic here
        print(f"Preprocessing with normalize={self.config.normalize}")
        return state


# ============================================================================
# Example 2: Add a validation node with conditional logic
# ============================================================================

class ValidateConfig(NodeConfig):
    max_length: int = Field(default=1000)
    check_format: bool = Field(default=True)


@NodeRegistry.register("validate")
class ValidateNode(Node):
    @classmethod
    def get_config_class(cls):
        return ValidateConfig
    
    @classmethod
    def get_node_type(cls):
        return "processing"
    
    @classmethod
    def get_condition(cls):
        def condition(state: MessagesState):
            return "generate" if state.get("validation_failed") else "NEXT"
        return condition
    
    def execute(self, state: MessagesState) -> MessagesState:
        # Your validation logic here
        print(f"Validating with max_length={self.config.max_length}")
        return state


# ============================================================================
# Example 3: Add a logging/monitoring node
# ============================================================================

class MonitorConfig(NodeConfig):
    log_level: str = Field(default="INFO")
    track_metrics: bool = Field(default=True)


@NodeRegistry.register("monitor")
class MonitorNode(Node):
    @classmethod
    def get_config_class(cls):
        return MonitorConfig
    
    @classmethod
    def get_node_type(cls):
        return "terminal"  # Runs at the end
    
    def execute(self, state: MessagesState) -> MessagesState:
        # Your monitoring logic here
        print(f"Monitoring at level={self.config.log_level}")
        return state


# ============================================================================
# Usage: Create graph with new nodes (NO CODE CHANGES NEEDED!)
# ============================================================================

if __name__ == "__main__":
    # Example 1: Use only new nodes
    config1 = GraphConfig.create_with_nodes(
        preprocess=PreprocessConfig(normalize=True),
        generate=None,  # Use default config
        validate=ValidateConfig(max_length=500),
        monitor=MonitorConfig(log_level="DEBUG"),
    )
    
    # Example 2: Mix old and new nodes
    from simple_graph_builder import CIMConfig, FewShotConfig, ReflectConfig
    
    config2 = GraphConfig.create_with_nodes(
        preprocess=PreprocessConfig(),
        cim=CIMConfig(k=10),
        few_shot=FewShotConfig(examples=5),
        generate=None,
        validate=ValidateConfig(),
        reflect=ReflectConfig(),
        monitor=MonitorConfig(),
    )
    
    # Build and visualize
    g = get_graph(config2).compile()
    display(
        Image(
            g.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API,
            )
        )
    )
    
    print("\n✅ Added 3 new nodes without modifying any existing code!")
    print("✅ SOLID principles maintained!")
    print("✅ Fully extensible and modular!")
