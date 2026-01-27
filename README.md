# LLM Benchmark Framework with LangGraph

A clean, modular framework for benchmarking multiple LLM providers using LangGraph workflows with structured output.

## Features

- **Multi-Provider Support**: OpenRouter, AvvalAI, and Ollama
- **LangGraph Workflow**: Multi-node reasoning pipeline (Analyze → Solve → Verify)
- **Structured Output**: Uses Pydantic models for consistent response format at each node
- **Graceful Fallbacks**: Automatically falls back to unstructured output for models without tool support
- **Comprehensive Logging**: Individual log files for each model with node-level tracking
- **JSON Results**: Timestamped results with success/failure and accuracy tracking
- **Clean Architecture**: Modular, extensible, and follows SOLID principles
- **OpenAI-Compatible**: Uses `langchain-openai` for all providers
- **Extensible Node System**: Each workflow node is a separate class (easy to add/modify nodes)

## Architecture (SOLID Principles)

### Single Responsibility
- **`src/nodes.py`**: Each node class has one job (AnalyzeNode, SolveNode, VerifyNode)
- **`src/config.py`**: Handles configuration only
- **`src/provider.py`**: Manages LLM client creation only

### Open/Closed Principle
- Nodes can be extended without modifying existing code
- Add new node types by creating new classes that inherit from `BaseNode`

### Dependency Inversion
- `WorkflowGraph` depends on `BaseNode` abstraction, not concrete implementations
- Nodes are injected via dependency injection in the graph builder

### Code Flow
```
main.py → BenchmarkRunner → WorkflowGraph → BaseNode (concrete nodes)
              ↓                    ↓
          Provider            LangGraph State
              ↓
          ChatOpenAI (with fallbacks)
```

## Project Structure

```
.
├── config.yaml              # Provider configuration (base URLs, API keys, etc.)
├── prompts/                 # Directory with JSON prompt files
│   ├── general_knowledge.json  # General knowledge prompts
│   ├── math_problems.json      # Math problem prompts
│   └── coding.json             # Programming prompts (example)
├── .env                     # API keys (create from .env.example)
├── .env.example            # Example environment variables
├── pyproject.toml          # Poetry dependencies
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── models.py           # Pydantic models for structured output
│   ├── provider.py         # Provider abstraction
│   ├── nodes.py            # Workflow nodes (Analyze, Solve, Verify)
│   ├── graph.py            # LangGraph workflow definition
│   └── runner.py           # Benchmark orchestration
├── results/                # JSON output files (auto-created)
└── logs/                   # Log files per model (auto-created)
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)

### Install Poetry

```bash
# On Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -

# On Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Setup Project

1. Clone or navigate to the project directory

2. Install dependencies:
```bash
poetry install
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

4. Edit `.env` and add your API keys:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
AVVALAI_API_KEY=your_avvalai_api_key_here
OLLAMA_API_KEY=your_ollama_api_key_here
```

## Configuration

The framework uses two separate configuration files:

### 1. `config.yaml` - Provider Configuration

Configure providers, base URLs, and model settings:

```yaml
providers:
  openrouter:
    base_url: "https://openrouter.ai/api/v1"
    api_key_env: "OPENROUTER_API_KEY"
    supports_system_prompt: true  # Optional: defaults to true
    models:
      - "openai/gpt-4.1-mini"
      - "google/gemma-3-4b-it"
  
  avvalai:
    base_url: "https://api.avalai.ir/v1"
    api_key_env: "AVVALAI_API_KEY"
    supports_system_prompt: false  # Models without system prompt support
    models:
      - "cf.gemma-3-12b-it"
      - "gemma-3-4b-it"

output:
  results_dir: "results"
  logs_dir: "logs"
```

**Provider Options:**
- **`supports_system_prompt`**: `true` (default) or `false`
  - Set to `false` for providers that don't support system messages (e.g., AvvalAI)

### 2. `prompts/` Directory - Prompt Configuration

Each JSON file in the `prompts/` directory contains prompts for all workflow nodes:

```json
{
  "system_prompt": "You are a helpful AI assistant. Answer questions accurately and concisely.",
  "test_prompt": "What is the capital of France? Provide the city name and a brief explanation of why it's significant.",
  "nodes": {
    "analyze": {
      "prompt": "Analyze this problem carefully:\n\n{problem}\n\nIdentify:\n1. What type of problem this is\n2. Key constraints or requirements\n3. The best approach to solve it",
      "system_prompt_included": true
    },
    "solve": {
      "prompt": "Based on this analysis:\n\n{analysis_summary}\n\nNow solve this problem:\n{problem}\n\nProvide:\n1. Your final answer\n2. Step-by-step reasoning\n3. Your confidence level (high/medium/low)",
      "system_prompt_included": true
    },
    "verify": {
      "prompt": "Verify this solution:\n\nOriginal Problem:\n{problem}\n\nProposed Solution:\n{solution_summary}\n\nCheck:\n1. Is the solution correct?\n2. Are there any issues or concerns?\n3. What is the final verified answer?",
      "system_prompt_included": true
    }
  }
}
```

**Key Features:**
- ✅ **Separate prompts per node**: Each node (analyze, solve, verify) can have custom prompts
- ✅ **System prompt control**: Per-node `system_prompt_included` flag for fine-grained control
- ✅ **Template variables**: Use `{problem}`, `{analysis_summary}`, `{solution_summary}` in prompts
- ✅ **Easy to add**: Create new JSON files for different domains (math, coding, creative, etc.)
- ✅ **Automatic discovery**: Framework loads all JSON files in the `prompts/` directory

**Example Files:**
- `general_knowledge.json` - General questions
- `math_problems.json` - Math calculations
- `coding.json` - Programming challenges

### 3. Adding New Providers

To add a new OpenAI-compatible provider:

```yaml
providers:
  new_provider:
    base_url: "https://api.newprovider.com/v1"
    api_key_env: "NEW_PROVIDER_API_KEY"
    supports_system_prompt: true  # Optional, defaults to true
    models:
      - "model-name-1"
      - "model-name-2"
```

Then add the API key to `.env`:
```
NEW_PROVIDER_API_KEY=your_key_here
```

### 4. Creating Custom Prompts

To create a custom prompt set, create a new JSON file in the `prompts/` directory:

**Example: `prompts/coding.json`**
```json
{
  "system_prompt": "You are an expert programmer. Write clean, efficient code with clear explanations.",
  "test_prompt": "Write a Python function to find the maximum value in a list.",
  "nodes": {
    "analyze": {
      "prompt": "Analyze this programming task:\n\n{problem}\n\nIdentify:\n1. What programming language is appropriate?\n2. What are the requirements?\n3. What algorithm or approach is best?",
      "system_prompt_included": true
    },
    "solve": {
      "prompt": "Based on this analysis:\n\n{analysis_summary}\n\nNow write code for:\n{problem}\n\nProvide:\n1. The code with clear comments\n2. Explanation of the algorithm\n3. Time and space complexity",
      "system_prompt_included": true
    },
    "verify": {
      "prompt": "Verify this code solution:\n\nOriginal Problem:\n{problem}\n\nProposed Solution:\n{solution_summary}\n\nCheck:\n1. Does the code solve the problem?\n2. Is the code efficient and readable?\n3. Are there any bugs or edge cases?",
      "system_prompt_included": true
    }
  }
}
```

**Framework automatically discovers and runs all JSON files in `prompts/` directory.**

## Usage

### Run Benchmark (All Prompts)

Run all JSON files in the `prompts/` directory:

```bash
poetry run python main.py
```

**Re-run even if already executed in this session:**

```bash
poetry run python main.py --rerun
```

### Run Specific Prompt

Use the interactive runner:

```bash
poetry run python run_benchmark.py
```

This will show a menu to select which prompt to run.

**Or specify a prompt directly:**

```bash
poetry run python run_benchmark.py --prompt general_knowledge
poetry run python run_benchmark.py --prompt math_problems
poetry run python run_benchmark.py --prompt coding
```

**Re-run specific prompt:**

```bash
poetry run python run_benchmark.py --prompt coding --rerun
```

### List Available Prompts

```bash
poetry run python run_benchmark.py --list
```

### Custom Configuration

```bash
poetry run python run_benchmark.py \
  --config custom_config.yaml \
  --prompts-dir custom_prompts
```

### Skip Prevention

By default, if you run the same prompt/model combination multiple times in a session, it will be skipped on subsequent runs to save time and API calls. Use `--rerun` to force re-execution.

### Output

The framework generates:

1. **Console Output**: Real-time progress showing each workflow node
2. **JSON Results**: `results/benchmark_results_YYYYMMDD_HHMMSS.json`
3. **Log Files**: `logs/provider_model.log` for each model

### Example Output Structure

```json
{
  "timestamp": "20250127_143022",
  "system_prompt": "You are an expert problem solver...",
  "test_problem": "A farmer has 17 sheep...",
  "workflow": "analyze -> solve -> verify",
  "results": [
    {
      "provider": "openrouter",
      "model": "openai/gpt-4.1-mini",
      "status": "success",
      "response": {
        "analysis": {
          "problem_type": "logical reasoning",
          "key_constraints": ["17 total sheep", "all but 9 die"],
          "approach": "Parse the phrase 'all but 9' carefully"
        },
        "solution": {
          "answer": "9 sheep are left alive",
          "reasoning_steps": [
            "Start with 17 sheep total",
            "'All but 9 die' means 9 survive",
            "Therefore, 9 sheep remain alive"
          ],
          "confidence": "high"
        },
        "verification": {
          "is_correct": true,
          "issues_found": [],
          "final_answer": "9 sheep"
        }
      }
    }
  ],
  "summary": {
    "total_models": 12,
    "successful": 11,
    "failed": 1,
    "verified_correct": 10,
    "success_rate": "91.7%",
    "accuracy_rate": "90.9%"
  }
}
```

### LangGraph Workflow

The framework uses a 3-node workflow with intelligent fallbacks:

1. **Analyze Node** (`AnalyzeNode`): Identifies problem type, constraints, and approach
2. **Solve Node** (`SolveNode`): Generates solution with step-by-step reasoning
3. **Verify Node** (`VerifyNode`): Validates the solution and provides final answer

#### Intelligent Fallback System

Each node attempts to use **structured output** (Pydantic models with tool calling) first. If the model doesn't support tool calling (404 errors), it automatically falls back to **unstructured output** with intelligent parsing:

```python
# Try structured output first
analysis = self._try_structured_output(ProblemAnalysis, prompt)

if analysis:
    return {"analysis": analysis}

# Fallback to unstructured output
response = self._get_unstructured_response(prompt)
# Parse and create default analysis
analysis = ProblemAnalysis(
    problem_type="factual knowledge question",
    key_constraints=["answer accurately", "provide explanation"],
    approach="Recall factual information"
)
```

This ensures the framework works with **all models**, regardless of their tool-calling capabilities.

## Extending the Framework

### Custom Response Models

Edit `src/models.py` to define your own Pydantic models:

```python
class CustomResponse(BaseModel):
    field1: str = Field(description="Description")
    field2: int = Field(description="Description")
```

Then update `src/provider.py` to use your model:

```python
structured_llm = self.client.with_structured_output(CustomResponse)
```

### Custom Workflow Nodes

To add new nodes, create a new class in `src/nodes.py`:

```python
from src.nodes import BaseNode

class CustomNode(BaseNode):
    """Custom workflow node."""
    
    def execute(self, state: dict) -> dict:
        """Execute custom node logic."""
        # Your implementation here
        return {"custom_result": result}
```

Then register it in `src/graph.py`:

```python
def _build_graph(self) -> StateGraph:
    workflow = StateGraph(GraphState)
    
    # Add new node
    custom_node = CustomNode(self.llm, self.logger, self.system_prompt)
    workflow.add_node("custom", custom_node.execute)
    
    # Modify edges
    workflow.add_edge("analyze", "custom")
    workflow.add_edge("custom", "solve")
    
    return workflow.compile()
```

This follows the Open/Closed Principle - open for extension, closed for modification.

### Custom Prompts

Modify `config.yaml`:

```yaml
system_prompt: "Your custom system prompt"
test_prompt: "Your custom test problem"
```

## Architecture

The framework follows SOLID principles:

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Open for extension (new providers), closed for modification
- **Dependency Inversion**: Depends on abstractions (OpenAI-compatible interface)
- **Consistency**: All providers use the same `ChatOpenAI` client

## Troubleshooting

### API Key Errors

If you see "API key not found" errors:
1. Ensure `.env` file exists in project root
2. Check that API keys are set correctly
3. Verify environment variable names match `config.yaml`

### Connection Errors

For Ollama or custom endpoints:
1. Verify the base URL is accessible
2. Check firewall/network settings
3. Ensure the API endpoint is running

### Model Not Found

If a model returns errors:
1. Check the model name is correct for that provider
2. Verify your API key has access to that model
3. Review the log file for detailed error messages

## License

MIT
