# Dependency Resolution

## Issue
`poetry lock` failed due to version conflicts:

```
langchain-qwq (>=0.3.0,<0.4.0) requires langchain-openai (>=1.0.2,<2.0.0)
llm-benchmark requires langchain-openai (^0.3.0)
```

## Root Cause
- `langchain-qwq >=0.3.0` depends on `langchain-openai >=1.0.2,<2.0.0`
- We were using `langchain-openai ^0.3.0` (too old)

## Solution
Updated `pyproject.toml` with compatible version ranges:

```toml
[tool.poetry.dependencies]
python = "^3.10"
langchain-openai = ">=1.0.2,<2.0.0"      # OLD: ^0.3.0
langchain-google-genai = ">=2.0.0,<3.0.0"  # OLD: ^2.0.0
langchain-qwq = ">=0.3.0,<0.4.0"           # OLD: ^0.3.0
langgraph = ">=0.2.0,<0.3.0"               # OLD: ^0.2.0
langchain-core = ">=0.3.0,<0.4.0"          # OLD: ^0.3.0
pydantic = ">=2.0.0,<3.0.0"                # OLD: ^2.0.0
pyyaml = ">=6.0,<7.0"                      # OLD: ^6.0
python-dotenv = ">=1.0.0,<2.0.0"           # OLD: ^1.0.0
```

## Version Ranges Explained

### Before (Caret: `^`)
- `^0.3.0` = `>=0.3.0,<0.4.0`
- `^2.0.0` = `>=2.0.0,<3.0.0`

### After (Compatible: `>=,<`)
- `>=1.0.2,<2.0.0` = `>=1.0.2,<2.0.0`
- `>=2.0.0,<3.0.0` = `>=2.0.0,<3.0.0`

## Compatibility Notes

### langchain-openai 1.x Changes
- **Import path**: Same (`from langchain_openai import ChatOpenAI`)
- **Parameters**: Same (`api_key`, `base_url`, `model`, `temperature`)
- **No breaking changes** for our use case

### Our Code Compatibility
Our code uses:
```python
ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0.7,
)
```

This is **fully compatible** with langchain-openai >=1.0.2.

## Commands to Run

```bash
# Update dependencies
poetry lock
poetry install

# Or with pip
pip install -U "langchain-openai>=1.0.2,<2.0.0" \
               "langchain-google-genai>=2.0.0,<3.0.0" \
               "langchain-qwq>=0.3.0,<0.4.0" \
               "langgraph>=0.2.0,<0.3.0" \
               "langchain-core>=0.3.0,<0.4.0" \
               "pydantic>=2.0.0,<3.0.0" \
               "pyyaml>=6.0,<7.0" \
               "python-dotenv>=1.0.0,<2.0.0"
```

## Result
All dependencies are now compatible and should resolve successfully.
