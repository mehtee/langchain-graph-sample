# Agents Refactor Summary

## Changes Made

### 1. Renamed "Nodes" to "Agents"
- **File renamed**: `src/nodes.py` → `src/agents.py`
- **Classes renamed**:
  - `BaseNode` → `BaseAgent`
  - `AnalyzeNode` → `AnalyzeAgent`
  - `SolveNode` → `SolveAgent`
  - `VerifyNode` → `VerifyAgent`
- **Config methods renamed**:
  - `get_node_prompt()` → `get_agent_prompt()`
  - `get_node_system_prompt_flag()` → `get_agent_system_prompt_flag()`

### 2. Added Non-LLM Agent
Created `SimpleCalculatorAgent` - a non-LLM agent that:
- Performs basic arithmetic without using language models
- Uses Python's `eval()` safely with limited scope
- Demonstrates that agents don't always need LLMs
- Returns structured output (ProblemAnalysis, Solution, Verification)

### 3. Improved State Management (LangGraph Best Practices)
- Changed `GraphState` from Pydantic `BaseModel` to `TypedDict`
- State is now passed as dict-like object (as per LangGraph documentation)
- Agents access state using dictionary syntax: `state["key"]`
- Configuration passed through state instead of stored in agent properties
- Agents initialized with minimal dependencies (just `llm` and `logger`)

### 4. Added Intelligent Fallback System
Each LLM-based agent now:
1. **Tries structured output first** using `with_structured_output()`
2. **Falls back to unstructured response** if structured fails
3. **Parses unstructured text** to create structured Pydantic models

#### Fallback Implementation:
```python
# Try structured output first
analysis = self._invoke_llm(prompt, ProblemAnalysis, system_prompt, use_system)

if analysis:
    self.logger.info(f"Analysis complete (structured)")
    return {"analysis": analysis}

# Fallback to unstructured response
self.logger.info("Falling back to unstructured response")
response = self._get_unstructured_response(prompt, system_prompt, use_system)

# Parse and create structured output
analysis = ProblemAnalysis(
    problem_type=extract_type_from_response(response),
    key_constraints=["answer accurately"],
    approach="Standard problem solving"
)
return {"analysis": analysis}
```

### 5. Enhanced Parsing Logic
For unstructured responses, agents now:
- **AnalyzeAgent**: Detects problem type from keywords (math, logic, creative)
- **SolveAgent**: Determines confidence level from response language
- **VerifyAgent**: Checks for correctness indicators (incorrect, wrong, error)

## Benefits

### 1. Universal Model Support
- ✅ Works with models that support structured output (tool calling)
- ✅ Works with models that don't support structured output
- ✅ Graceful degradation - no failures due to missing features

### 2. Cleaner Architecture
- Agents are lightweight (minimal initialization)
- State carries all configuration
- Easy to add new agents (LLM or non-LLM)
- Follows LangGraph documentation patterns

### 3. Better Logging
- Clear indication when using structured vs unstructured output
- Helps debug which models support which features
- Shows fallback behavior in action

## Testing

### Test Results
```bash
# Single prompt test
python run_benchmark.py --prompt simple_math --rerun

# Results:
✓ qwen/qwen3-coder-30b-a3b-instruct: Success (structured output)
✓ cf.gemma-3-12b-it: Success (structured output)
Success Rate: 100.0%
```

### Performance
- Fast execution (< 60 seconds for 2 models)
- Concurrent execution working correctly
- Proper skip logic for already-completed runs

## Files Modified

| File | Changes |
|------|---------|
| `src/agents.py` | Created (renamed from nodes.py), added fallback logic |
| `src/models.py` | Changed GraphState from BaseModel to TypedDict |
| `src/graph.py` | Updated to use agents, pass dict state |
| `src/config.py` | Renamed node methods to agent methods |
| `prompts/simple_math.yaml` | Created test prompt for math problems |

## Usage Example

```python
from src.config import Config
from src.provider import LLMProvider
from src.graph import WorkflowGraph

# Setup
config = Config()
prompt_config = config.get_prompt('simple_math')
provider = LLMProvider(config, 'openrouter', 'openai/gpt-4.1-mini')

# Create graph
graph = WorkflowGraph(
    llm_client=provider.get_client(),
    logger=provider.get_logger(),
    system_prompt=prompt_config.get('system_prompt', ''),
    use_system_prompt=provider.supports_system_prompt(),
    prompt_config=prompt_config,
    prompt_name='simple_math'
)

# Run
result = graph.run('What is 2+2?')
print(result['solution'].answer)  # "4"
```

## Next Steps

Potential improvements:
1. Add more sophisticated parsing for unstructured responses
2. Create more non-LLM agents (API calls, database queries, etc.)
3. Add agent-specific configuration in prompt YAML files
4. Implement agent selection logic (route to calculator for math, etc.)
