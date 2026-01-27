# Configuration Changes Summary

## New Directory Created

### `prompts/` Directory
Contains JSON files with prompts for all workflow nodes:

**`general_knowledge.json`:**
```json
{
  "system_prompt": "You are a helpful AI assistant...",
  "test_prompt": "What is the capital of France?",
  "nodes": {
    "analyze": {
      "prompt": "Analyze this problem carefully:\n\n{problem}\n\n...",
      "system_prompt_included": true
    },
    "solve": { ... },
    "verify": { ... }
  }
}
```

**`math_problems.json`:**
```json
{
  "system_prompt": "You are a math expert...",
  "test_prompt": "What is 3^3?",
  "nodes": {
    "analyze": { ... },
    "solve": { ... },
    "verify": { ... }
  }
}
```

## Modified Files

### 1. `config.yaml`
**Removed from config.yaml:**
```yaml
system_prompt: "..."  # ❌ REMOVED
test_prompt: "..."    # ❌ REMOVED
```

**Added to config.yaml:**
```yaml
providers:
  avvalai:
    supports_system_prompt: false  # ✅ NEW
```

### 2. `src/config.py`
**Major Changes:**
```python
# Before
def __init__(self, config_path: str = "config.yaml"):
    self._prompts = self._load_prompts()  # Single file

# After
def __init__(self, config_path: str = "config.yaml", prompts_dir: str = "prompts"):
    self.prompts_dir = Path(prompts_dir)
    self._available_prompts = self._scan_prompt_files()  # Multiple files

def _scan_prompt_files(self) -> List[str]:
    """Scan directory for all JSON files."""
    return sorted([f.stem for f in self.prompts_dir.glob("*.json")])

def get_prompt(self, name: str) -> Optional[Dict[str, Any]]:
    """Load specific prompt file by name."""
    return self._load_prompt_file(name)

def get_node_prompt(self, prompt_name: str, node_name: str, default: str = "") -> str:
    """Get prompt template for specific node."""
    prompt_data = self.get_prompt(prompt_name)
    return prompt_data['nodes'][node_name]['prompt']
```

**New Properties:**
- `available_prompts`: List of all JSON files in prompts directory
- `get_prompt(name)`: Load specific prompt file
- `get_node_prompt(...)`: Get node-specific prompt template

### 3. `src/nodes.py`
**Added prompt template support:**
```python
class BaseNode:
    def __init__(self, ..., prompt_template: str = "", prompt_name: str = ""):
        self.prompt_template = prompt_template
        self.prompt_name = prompt_name

class AnalyzeNode(BaseNode):
    def execute(self, state: dict) -> dict:
        # Use configured template or default
        if self.prompt_template:
            prompt = self.prompt_template.format(problem=problem)
        else:
            prompt = f"""Analyze this problem..."""
```

### 4. `src/graph.py`
**Added prompt config parameter:**
```python
class WorkflowGraph:
    def __init__(self, ..., prompt_config: Dict[str, Any] = None, prompt_name: str = ""):
        self.prompt_config = prompt_config or {}
        self.prompt_name = prompt_name
    
    def _build_graph(self) -> StateGraph:
        nodes_config = self.prompt_config.get('nodes', {})
        # Pass node-specific prompts to nodes
```

### 5. `src/runner.py`
**Iterates through all prompt files:**
```python
def __init__(self, ..., prompts_dir: str = "prompts"):
    self.config = Config(config_path, prompts_dir)

def run(self):
    for prompt_name in self.config.available_prompts:
        prompt_config = self.config.get_prompt(prompt_name)
        # Run benchmark for each prompt file
```

### 6. `main.py`
**Changed to use prompts directory:**
```python
# Before
runner = BenchmarkRunner(prompts_path="prompts.json")

# After
runner = BenchmarkRunner(prompts_dir="prompts")  # Loads all JSON files
```

## Benefits of Directory-Based Prompts

### 1. **Multiple Prompt Sets**
```bash
prompts/
├── general_knowledge.json  # General questions
├── math_problems.json      # Math calculations
└── coding.json             # Programming tasks
```

**Framework automatically runs ALL JSON files in the directory.**

### 2. **Node-Specific Prompts**
Each JSON file can customize prompts for each workflow node:
```json
{
  "nodes": {
    "analyze": {
      "prompt": "Custom analyze prompt...",
      "system_prompt_included": true
    },
    "solve": {
      "prompt": "Custom solve prompt...",
      "system_prompt_included": true
    }
  }
}
```

### 3. **Template Variables**
Use placeholders in prompts:
- `{problem}` - The test problem
- `{analysis_summary}` - Analysis results from previous node
- `{solution_summary}` - Solution results from previous node

### 4. **Automatic Discovery**
- ✅ No need to modify code for new prompts
- ✅ Just add a new JSON file to `prompts/` directory
- ✅ Framework automatically loads and runs it

### 5. **Better Organization**
```bash
# Easy to manage different use cases
prompts/
├── general/
│   ├── simple.json
│   ├── complex.json
├── math/
│   ├── arithmetic.json
│   ├── calculus.json
└── coding/
    ├── python.json
    ├── javascript.json
```

## How to Use

### Default Usage
```bash
python main.py  # Runs all JSON files in prompts/ directory
```

**Output:**
```
LLM BENCHMARK WITH LANGGRAPH
============================
Available prompt files: general_knowledge, math_problems, coding

============================
PROMPT: general_knowledge
============================
System Prompt: You are a helpful AI assistant...
Test Problem: What is the capital of France?
...
```

### Custom Prompts Directory
```python
runner = BenchmarkRunner(
    config_path="config.yaml",
    prompts_dir="prompts"  # Any directory with JSON files
)
```

### Creating New Prompt Sets
Simply add a new JSON file to `prompts/` directory:

**`prompts/coding.json`:**
```json
{
  "system_prompt": "You are an expert programmer...",
  "test_prompt": "Write a Python function to sort a list.",
  "nodes": {
    "analyze": {
      "prompt": "Analyze this coding task:\n\n{problem}\n\n...",
      "system_prompt_included": true
    },
    "solve": {
      "prompt": "Write code for:\n\n{problem}\n\n...",
      "system_prompt_included": true
    },
    "verify": {
      "prompt": "Verify this code:\n\n{problem}\n\n{solution_summary}\n\n...",
      "system_prompt_included": true
    }
  }
}
```

**Next run of `python main.py` will automatically include this new prompt file!**

## Provider Configuration Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `base_url` | string | required | API endpoint |
| `api_key_env` | string | required | Environment variable name |
| `supports_system_prompt` | boolean | `true` | Whether provider supports system messages |
| `models` | list | required | Model names |

## Example Configurations

### OpenRouter (Full Support)
```yaml
openrouter:
  base_url: "https://openrouter.ai/api/v1"
  api_key_env: "OPENROUTER_API_KEY"
  # supports_system_prompt: true  # Default
  models:
    - "openai/gpt-4.1-mini"
    - "google/gemma-3-4b-it"
```

### AvvalAI (No System Prompt Support)
```yaml
avvalai:
  base_url: "https://api.avalai.ir/v1"
  api_key_env: "AVVALAI_API_KEY"
  supports_system_prompt: false  # Must set to false
  models:
    - "gemma-3-4b-it"
```

### Ollama (Self-Hosted)
```yaml
ollama:
  base_url: "http://localhost:8080"
  api_key_env: "OLLAMA_API_KEY"
  # supports_system_prompt: true  # Default for most models
  models:
    - "gemma3:27b"
    - "qwen3-coder:30b"
```

## Migration Guide

If you have an existing config.yaml with prompts, migrate as follows:

**Old config.yaml:**
```yaml
system_prompt: "You are an AI assistant..."
test_prompt: "What is 2+2?"
providers:
  openrouter:
    # ...
```

**New config.yaml:**
```yaml
providers:
  openrouter:
    # ...
```

**New prompts.json:**
```json
{
  "system_prompt": "You are an AI assistant...",
  "test_prompt": "What is 2+2?"
}
```
