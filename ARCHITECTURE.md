# Graph Builder Architecture

## Overview

This is a clean, SOLID-based, registry-pattern architecture for building LangGraph workflows. It's fully extensible without modifying existing code.

## Key Design Principles

### 1. **Single Responsibility Principle (SRP)**
- `Node`: Handles node execution logic
- `NodeConfig`: Manages node configuration
- `NodeRegistry`: Manages node registration
- `GraphBuilder`: Handles graph construction
- `GraphConfig`: Manages overall configuration

### 2. **Open/Closed Principle (OCP)**
- **Open for extension**: Add new nodes by creating new classes
- **Closed for modification**: No need to change existing code

### 3. **Liskov Substitution Principle (LSP)**
- All nodes inherit from `Node` base class
- Any node can be substituted without breaking the system

### 4. **Interface Segregation Principle (ISP)**
- Nodes only implement what they need
- Optional methods (like `get_condition()`) return `None` by default

### 5. **Dependency Inversion Principle (DIP)**
- Depends on abstractions (`Node`, `NodeConfig`)
- Not on concrete implementations

## Architecture Components

### Node Types

Nodes are categorized by their role in the graph:

1. **IR Nodes** (`ir`): Information Retrieval
   - Run in parallel from START
   - All connect to "generate" node
   - Examples: `cim`, `related_metadata`, `few_shot`, `spl_docs`

2. **Processing Nodes** (`processing`): Main workflow
   - Run sequentially after generate
   - Can have conditional edges
   - Examples: `generate`, `syntax_check`, `execute`

3. **Terminal Nodes** (`terminal`): Final steps
   - Run at the end of the workflow
   - Can loop back to generate
   - Examples: `reflect`, `monitor`

### Registry Pattern

The `NodeRegistry` enables:
- **Decoupled registration**: Nodes register themselves
- **Dynamic discovery**: Find nodes by type
- **Zero configuration**: No manual mapping needed

```python
@NodeRegistry.register("my_node")
class MyNode(Node):
    # Implementation
```

### Graph Building

The `GraphBuilder` automatically:
1. Adds IR nodes in parallel
2. Connects them to generate
3. Chains processing nodes sequentially
4. Handles conditional edges
5. Connects to END appropriately

## How to Add a New Node

### Step 1: Create Config Class

```python
class MyNodeConfig(NodeConfig):
    my_param: int = Field(default=10)
```

### Step 2: Create Node Class

```python
@NodeRegistry.register("my_node")
class MyNode(Node):
    @classmethod
    def get_config_class(cls):
        return MyNodeConfig
    
    @classmethod
    def get_node_type(cls):
        return "ir"  # or "processing" or "terminal"
    
    def execute(self, state: MessagesState) -> MessagesState:
        # Your logic here
        return state
```

### Step 3: Use It (Optional Conditional)

```python
@classmethod
def get_condition(cls):
    def condition(state: MessagesState):
        return "generate" if state.get("retry") else "NEXT"
    return condition
```

### Step 4: Configure and Run

```python
config = GraphConfig.create_with_nodes(
    my_node=MyNodeConfig(my_param=20),
    generate=None,
)

graph = get_graph(config).compile()
```

**That's it! No other code changes needed!**

## Benefits

### ✅ Extensibility
- Add unlimited nodes without touching existing code
- Each node is self-contained

### ✅ Maintainability
- Clear separation of concerns
- Easy to understand and debug
- Each component has one job

### ✅ Testability
- Mock individual nodes easily
- Test graph building separately
- Test node logic in isolation

### ✅ Flexibility
- Mix and match any nodes
- Dynamic configuration
- Runtime node discovery

### ✅ Type Safety
- Pydantic validation for configs
- Type hints throughout
- Compile-time error detection

## Comparison: Before vs After

### Before (Problems)
```python
# Adding a new node required changes in:
1. GraphConfig class definition
2. nodes dictionary
3. get_graph() function logic
4. condition_edges dictionary (if conditional)
5. Multiple if/elif blocks
```

### After (Solution)
```python
# Adding a new node requires:
1. Create config class
2. Create node class with @NodeRegistry.register()
3. Done! ✅
```

## Advanced Usage

### Custom Processing Order

```python
builder = GraphBuilder(config)
builder.processing_order = ["generate", "my_custom", "syntax_check", "execute"]
graph = builder.build()
```

### Conditional Node Inclusion

```python
config = GraphConfig.create_with_nodes(
    cim=CIMConfig() if use_cim else None,
    generate=GenerateConfig(),
)
```

### Dynamic Node Discovery

```python
# Get all IR nodes
ir_nodes = NodeRegistry.get_by_type("ir")

# Get specific node
node_class = NodeRegistry.get("cim")
```

## Best Practices

1. **Keep nodes focused**: Each node should do one thing well
2. **Use meaningful names**: Node names should describe their purpose
3. **Document configs**: Add descriptions to config fields
4. **Handle errors gracefully**: Validate state in execute()
5. **Test independently**: Unit test each node separately

## Migration Guide

To migrate existing code:

1. Identify your nodes and their types (ir/processing/terminal)
2. Create config classes for each node
3. Create node classes with `@NodeRegistry.register()`
4. Replace old GraphConfig with new one
5. Test the graph builds correctly

See `example_extension.py` for complete examples!
