"""Main entry point for LLM benchmark."""
import sys
from src.runner import BenchmarkRunner


def main():
    """Run the benchmark."""
    # Check for --rerun flag
    rerun_existing = "--rerun" in sys.argv
    
    runner = BenchmarkRunner(
        config_path="config.yaml",
        prompts_dir="prompts",
        rerun_existing=rerun_existing
    )
    runner.run()


if __name__ == "__main__":
    main()
