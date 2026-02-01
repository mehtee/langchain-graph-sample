from typing import Callable, Literal
from langgraph.graph import START, END, StateGraph
from langgraph.graph import MessagesState
from IPython.display import display, Image
from langchain_core.runnables.graph import MermaidDrawMethod
from pydantic import BaseModel, Field, RootModel


# Node configs
class CIMConfig(BaseModel):
    k: int = 5


class RelatedMetadataConfig(BaseModel):
    indexes: list[str] | None = None
    sourcetypes: list[str] | None = None
    hosts: list[str] | None = None
    macros: list[str] | None = None
    eventtypes: list[str] | None = None
    tags: list[str] | None = None
    lookups: list[str] | None = None


class FewShotConfig(BaseModel):
    examples: int = 3


class SplDocsConfig(BaseModel):
    top_n: int = 5


class GenerateConfig(BaseModel):
    pass


class SyntaxCheckConfig(BaseModel):
    pass


class ExecuteConfig(BaseModel):
    pass


class ReflectConfig(BaseModel):
    pass


# Use RootModel for cleaner config structure
class GraphConfig(RootModel[dict[str, BaseModel | None]]):
    root: dict[str, BaseModel | None] = {}


# Node functions
def default_node(**config):
    return lambda x: x


def syntax_check_condition(**kw) -> Literal["generate", "NEXT"]:
    return "generate" if kw.get("is_valid") else "NEXT"


def reflect_condition(**kw) -> Literal["generate", "NEXT"]:
    return "generate" if kw.get("needs_reflection") else "NEXT"


# Node definitions: name -> (function_builder, condition)
NODES = {
    "cim": (default_node, None),
    "related_metadata": (default_node, None),
    "few_shot": (default_node, None),
    "spl_docs": (default_node, None),
    "generate": (default_node, None),
    "syntax_check": (default_node, syntax_check_condition),
    "execute": (default_node, None),
    "reflect": (default_node, reflect_condition),
}

# Node categories
IR_NODES = ["cim", "related_metadata", "few_shot", "spl_docs"]
PIPELINE_NODES = ["syntax_check", "execute", "reflect"]

# Connection rules: node -> (should_connect_from_prev, next_node_lookup, is_conditional)
CONNECTION_RULES = {
    "syntax_check": (
        lambda prev, _: True,  # Always connect from previous
        lambda cfg: "execute" if cfg.get("execute") else "reflect" if cfg.get("reflect") else END,
        True  # Has conditional edge
    ),
    "execute": (
        lambda prev, _: prev == "generate",  # Only connect if previous is generate
        lambda _: END,
        False
    ),
    "reflect": (
        lambda prev, _: prev != "generate",  # Connect if not from generate
        lambda _: END,
        True  # Has conditional edge
    ),
}

# Nodes that should connect to END when they're the last node
TERMINAL_NODES = {"generate", "execute"}


def get_graph(config: GraphConfig) -> StateGraph:
    graph = StateGraph(MessagesState)
    
    # Always add generate node
    generate_config = config.root.get("generate", GenerateConfig())
    func_builder, _ = NODES["generate"]
    graph.add_node("generate", func_builder(**generate_config.model_dump()))
    
    current_node = "generate"
    
    # Add pipeline nodes
    for node_name in PIPELINE_NODES:
        if node_conf := config.root.get(node_name):
            func_builder, condition = NODES[node_name]
            graph.add_node(node_name, func_builder(**node_conf.model_dump()))
            
            # Apply connection rules
            should_connect, next_lookup, is_conditional = CONNECTION_RULES[node_name]
            
            if should_connect(current_node, config.root):
                graph.add_edge(current_node, node_name)
            
            if is_conditional:
                next_node = next_lookup(config.root)
                graph.add_conditional_edges(
                    node_name,
                    condition,
                    {"generate": "generate", "NEXT": next_node}
                )
            
            current_node = node_name
    
    # Add IR nodes and connect to generate
    has_ir_nodes = False
    for ir_node in IR_NODES:
        if ir_conf := config.root.get(ir_node):
            has_ir_nodes = True
            func_builder, _ = NODES[ir_node]
            graph.add_node(ir_node, func_builder(**ir_conf.model_dump()))
            graph.add_edge(START, ir_node)
            graph.add_edge(ir_node, "generate")
    
    # Connect START to generate if no IR nodes
    if not has_ir_nodes:
        graph.add_edge(START, "generate")
    
    # Connect final node to END if needed
    if current_node in TERMINAL_NODES:
        graph.add_edge(current_node, END)
    
    return graph
