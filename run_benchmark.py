#!/usr/bin/env python3
"""
Interactive script to run benchmarks with selected prompts.

Usage:
    python run_benchmark.py                          # Run all prompts
    python run_benchmark.py --prompt general_knowledge  # Run specific prompt
    python run_benchmark.py --list                   # List available prompts
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.runner import BenchmarkRunner


def list_available_prompts(prompts_dir: str = "prompts"):
    """List all available prompt files."""
    prompts_path = Path(prompts_dir)
    if not prompts_path.exists():
        print(f"Error: Prompts directory '{prompts_dir}' not found")
        return []
    
    files = sorted([f.stem for f in prompts_path.glob("*.json")])
    return files


def main():
    parser = argparse.ArgumentParser(description="Run LLM benchmark with selected prompts")
    parser.add_argument(
        "--prompt", 
        type=str, 
        help="Run specific prompt file (without .json extension)"
    )
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="List available prompt files"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)"
    )
    parser.add_argument(
        "--prompts-dir", 
        type=str, 
        default="prompts",
        help="Path to prompts directory (default: prompts)"
    )
    parser.add_argument(
        "--rerun", 
        action="store_true", 
        help="Re-run even if already executed in this session"
    )
    
    args = parser.parse_args()
    
    # List mode
    if args.list:
        available = list_available_prompts(args.prompts_dir)
        if available:
            print("\nAvailable prompt files:")
            for p in available:
                print(f"  - {p}")
            print()
        else:
            print(f"No prompt files found in '{args.prompts_dir}'")
        return
    
    # Interactive selection mode
    if not args.prompt:
        available = list_available_prompts(args.prompts_dir)
        if not available:
            print(f"No prompt files found in '{args.prompts_dir}'")
            return
        
        print("\nAvailable prompts:")
        for i, p in enumerate(available, 1):
            print(f"  {i}. {p}")
        print(f"  A. All prompts (default)")
        
        choice = input("\nSelect prompt (number, A for all, or Q to quit): ").strip().lower()
        
        if choice == 'q':
            print("Exiting.")
            return
        elif choice == 'a' or choice == '':
            # Run all prompts (default behavior)
            runner = BenchmarkRunner(
                config_path=args.config, 
                prompts_dir=args.prompts_dir,
                rerun_existing=args.rerun
            )
            runner.run()
            return
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(available):
                args.prompt = available[idx]
            else:
                print("Invalid selection")
                return
        else:
            print("Invalid selection")
            return
    
    # Run specific prompt
    print(f"\n{'='*70}")
    print(f"Running benchmark with prompt: {args.prompt}")
    print(f"{'='*70}\n")
    
    runner = BenchmarkRunner(
        config_path=args.config, 
        prompts_dir=args.prompts_dir,
        rerun_existing=args.rerun
    )
    
    # Temporarily filter to just the selected prompt
    original_available = runner.config.available_prompts
    if args.prompt in original_available:
        runner.config._available_prompts = [args.prompt]
        runner.run()
    else:
        print(f"Error: Prompt '{args.prompt}' not found in '{args.prompts_dir}'")
        print(f"Available: {', '.join(original_available)}")


if __name__ == "__main__":
    main()
