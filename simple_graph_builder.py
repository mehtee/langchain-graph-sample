from dataclasses import dataclass
from sre_parse import State
from typing import Any, Callable, Generic, Literal, Optional, TypeVar
from langgraph.graph import START, END, StateGraph
from langgraph.graph import MessagesState
from IPython.display import display, Image
from langchain_core.runnables.graph import MermaidDrawMethod
from pydantic import BaseModel, Field, RootModel
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph.state import StateNode


# Node configs
class NodeConfig(BaseModel):
    pass


class CIMConfig(NodeConfig):
    k: int = 5


class RelatedMetadataConfig(NodeConfig):
    indexes: Optional[list[str]] = None
    sourcetypes: Optional[list[str]] = None
    hosts: Optional[list[str]] = None
    macros: Optional[list[str]] = None
    eventtypes: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    lookups: Optional[list[str]] = None


class FewShotConfig(NodeConfig):
    examples: int = 3


class SPLDocsConfig(NodeConfig):
    top_n: int = 5


class GenerateConfig(NodeConfig):
    pass


class SyntaxCheckConfig(NodeConfig):
    pass


class ExecuteConfig(NodeConfig):
    pass


class ReflectConfig(NodeConfig):
    pass


# Use RootModel for cleaner config structure
class GraphConfig(RootModel[dict[str, NodeConfig]]):
    pass


class GraphState(MessagesState):
    pass


Condition = Callable[[GraphState], Literal["generate", "NEXT"]]

C = TypeVar("C", bound=NodeConfig)


def node_gen_cim(config: CIMConfig) -> StateNode:
    return lambda state: {}


def node_gen_related_metadata(config: RelatedMetadataConfig) -> StateNode:
    return lambda state: {}


def node_gen_few_shot(config: FewShotConfig) -> StateNode:
    return lambda state: {}


def node_gen_spl_docs(config: SPLDocsConfig) -> StateNode:
    return lambda state: {}


def node_gen_generate(config: GenerateConfig) -> StateNode:
    return lambda state: {}


def node_gen_syntax_check(config: SyntaxCheckConfig) -> StateNode:
    return lambda state: {}


def node_gen_execute(config: ExecuteConfig) -> StateNode:
    return lambda state: {}


def node_gen_reflect(config: ReflectConfig) -> StateNode:
    return lambda state: {}


# =========================
# Conditions
# =========================


def syntax_check_condition(state: GraphState) -> Literal["generate", "NEXT"]:
    return "generate" if state.get("is_valid") else "NEXT"


def reflect_condition(state: GraphState) -> Literal["generate", "NEXT"]:
    return "generate" if state.get("needs_reflection") else "NEXT"


# =========================
# NodeSpec (GENERIC + SAFE)
# =========================


@dataclass(frozen=True)
class NodeSpec(Generic[C]):
    node_func_generator: Callable[[C], StateNode]
    condition: Optional[Condition] = None


# =========================
# Node registry
# =========================

NODES: dict[str, NodeSpec] = {
    "cim": NodeSpec(node_func_generator=node_gen_cim),
    "related_metadata": NodeSpec(node_func_generator=node_gen_related_metadata),
    "few_shot": NodeSpec(node_func_generator=node_gen_few_shot),
    "spl_docs": NodeSpec(node_func_generator=node_gen_spl_docs),
    "generate": NodeSpec(node_func_generator=node_gen_generate),
    "syntax_check": NodeSpec(
        node_func_generator=node_gen_syntax_check,
        condition=syntax_check_condition,
    ),
    "execute": NodeSpec(node_func_generator=node_gen_execute),
    "reflect": NodeSpec(
        node_func_generator=node_gen_reflect,
        condition=reflect_condition,
    ),
}

# Node categories
IR_NODES = ["cim", "related_metadata", "few_shot", "spl_docs"]
PIPELINE_NODES = ["syntax_check", "execute", "reflect"]


# TODO: convert it to type based code
# Connection rules: node -> (should_connect_from_prev, next_node_lookup, is_conditional)
CONNECTION_RULES = {
    "syntax_check": (
        lambda prev, _: True,  # Always connect from previous
        lambda cfg: (
            "execute"
            if cfg.get("execute")
            else "reflect" if cfg.get("reflect") else END
        ),
        True,  # Has conditional edge
    ),
    "execute": (
        lambda prev, _: prev == "generate",  # Only connect if previous is generate
        lambda _: END,
        False,
    ),
    "reflect": (
        lambda prev, _: prev != "generate",  # Connect if not from generate
        lambda _: END,
        True,  # Has conditional edge
    ),
}

# Nodes that should connect to END when they're the last node
TERMINAL_NODES = {"generate", "execute"}


def get_graph(config: GraphConfig) -> StateGraph:
    graph = StateGraph(MessagesState)

    # Always add generate node
    generate_config = config.root.get("generate", GenerateConfig())
    graph.add_node("generate", NODES["generate"].node_func_generator(generate_config))

    current_node = "generate"

    # Add pipeline nodes
    for node_name in PIPELINE_NODES:
        if node_conf := config.root.get(node_name):
            node_spec = NODES[node_name]
            graph.add_node(node_name, node_spec.node_func_generator(node_conf))

            # Apply connection rules
            should_connect, next_lookup, is_conditional = CONNECTION_RULES[node_name]

            if should_connect(current_node, config.root):
                graph.add_edge(current_node, node_name)

            if node_spec.condition:
                next_node = next_lookup(config.root)
                graph.add_conditional_edges(
                    node_name,
                    node_spec.condition,
                    {"generate": "generate", "NEXT": next_node},
                )

            current_node = node_name

    # Add IR nodes and connect to generate
    has_ir_nodes = False
    for ir_node in IR_NODES:
        if ir_conf := config.root.get(ir_node):
            has_ir_nodes = True
            node_spec = NODES[ir_node]
            graph.add_node(ir_node, node_spec.node_func_generator(ir_conf))
            graph.add_edge(START, ir_node)
            graph.add_edge(ir_node, "generate")

    # Connect START to generate if no IR nodes
    if not has_ir_nodes:
        graph.add_edge(START, "generate")

    # Connect final node to END if needed
    if current_node in TERMINAL_NODES:
        graph.add_edge(current_node, END)

    return graph
