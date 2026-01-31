"""Main runner for benchmarking."""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import Config
from src.provider import LLMProvider
from src.graph import WorkflowGraph


class BenchmarkRunner:
    """Orchestrates benchmark execution across providers."""
    
    def __init__(self, config_path: str = "config.yaml", prompts_dir: str = "prompts",
                 rerun_existing: bool = False):
        self.config = Config(config_path, prompts_dir)
        self.results: List[Dict[str, Any]] = []
        self.rerun_existing = rerun_existing
        # Track which prompt/model combinations have already been run
        self._run_tracker = set()
        # Load previously completed runs from existing results files
        self._completed_runs = self._load_completed_runs()
    
    def run(self) -> None:
        """Run benchmark across all providers and models."""
        print("="*70)
        print("LLM BENCHMARK WITH LANGGRAPH")
        print("="*70)
        print(f"\nAvailable prompt files: {', '.join(self.config.available_prompts)}")
        print("="*70)
        
        # Iterate through all available prompt files
        for prompt_name in self.config.available_prompts:
            prompt_config = self.config.get_prompt(prompt_name)
            
            if not prompt_config:
                continue
            
            test_prompt = prompt_config.get('test_prompt', 'N/A')
            system_prompt = prompt_config.get('system_prompt', 'N/A')
            
            print(f"\n{'='*70}")
            print(f"PROMPT: {prompt_name}")
            print(f"{'='*70}")
            print(f"\nSystem Prompt: {system_prompt}")
            print(f"\nTest Problem: {test_prompt}")
            print(f"\nWorkflow: Analyze → Solve → Verify")
            print("="*70)
            
            # Collect all tasks to run
            tasks = []
            for provider_name, provider_config in self.config.providers.items():
                for model_name in provider_config['models']:
                    run_id = f"{prompt_name}_{provider_name}_{model_name}"
                    
                    # Check if already completed
                    if not self.rerun_existing:
                        if run_id in self._run_tracker or run_id in self._completed_runs:
                            tasks.append({
                                'prompt_name': prompt_name,
                                'provider_name': provider_name,
                                'model_name': model_name,
                                'skip': True,
                                'reason': 'Already run' if run_id in self._run_tracker else 'Already completed'
                            })
                            continue
                    
                    tasks.append({
                        'prompt_name': prompt_name,
                        'provider_name': provider_name,
                        'model_name': model_name,
                        'skip': False,
                        'prompt_config': prompt_config
                    })
            
            # Run tasks concurrently
            self._run_tasks_concurrently(tasks)
        
        self._save_results()
        self._print_summary()
    
    def _run_tasks_concurrently(self, tasks: List[Dict[str, Any]]) -> None:
        """Run benchmark tasks concurrently using ThreadPoolExecutor."""
        # Filter out skipped tasks
        runnable_tasks = [t for t in tasks if not t.get('skip', False)]
        skipped_tasks = [t for t in tasks if t.get('skip', False)]
        
        # Print skipped tasks
        for task in skipped_tasks:
            print(f"\n→ Testing model: {task['model_name']}")
            print(f"  → Skipped: {task['reason']}")
            result = {
                'prompt': task['prompt_name'],
                'provider': task['provider_name'],
                'model': task['model_name'],
                'status': 'skipped',
                'reason': task['reason']
            }
            self.results.append(result)
        
        if not runnable_tasks:
            return
        
        # Print provider header
        provider_name = runnable_tasks[0]['provider_name']
        print(f"\n{'='*70}")
        print(f"PROVIDER: {provider_name.upper()}")
        print(f"{'='*70}")
        print(f"\nRunning {len(runnable_tasks)} model(s) concurrently...")
        
        # Run tasks concurrently
        max_workers = self.config.max_workers
        if max_workers is None:
            max_workers = len(runnable_tasks)  # Use all available workers if not specified
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for task in runnable_tasks:
                # Mark as tracked before submitting to prevent duplicate runs
                run_id = f"{task['prompt_name']}_{task['provider_name']}_{task['model_name']}"
                self._run_tracker.add(run_id)
                
                future = executor.submit(
                    self._run_single_task,
                    task['provider_name'],
                    task['model_name'],
                    task['prompt_name'],
                    task['prompt_config']
                )
                future_to_task[future] = task
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    self._print_result(result)
                except Exception as e:
                    error_result = {
                        'prompt': task['prompt_name'],
                        'provider': task['provider_name'],
                        'model': task['model_name'],
                        'status': 'error',
                        'error': str(e)
                    }
                    self.results.append(error_result)
                    self._print_result(error_result)
    
    def _run_single_task(self, provider_name: str, model_name: str, 
                        prompt_name: str, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single benchmark task."""
        provider = LLMProvider(self.config, provider_name, model_name)
        return self._run_workflow(provider, prompt_name, prompt_config)
    
    def _print_result(self, result: Dict[str, Any]) -> None:
        """Print a single result."""
        print(f"\n→ Testing model: {result['model']}")
        
        if result['status'] == 'success':
            print(f"  ✓ Analysis: {result['response']['analysis']['problem_type']}")
            print(f"  ✓ Solution: {result['response']['solution']['answer'][:80]}...")
            print(f"  ✓ Verified: {result['response']['verification']['is_correct']}")
        elif result['status'] == 'skipped':
            print(f"  → Skipped: {result['reason']}")
        else:
            print(f"  ✗ Error: {result['error']}")
    
    def _load_completed_runs(self) -> set:
        """Load previously completed runs from existing results files."""
        completed = set()
        results_dir = Path(self.config.results_dir)
        
        if not results_dir.exists():
            return completed
        
        for results_file in results_dir.glob("benchmark_results_*.json"):
            try:
                with open(results_file, 'r') as f:
                    data = json.load(f)
                    for result in data.get('results', []):
                        if result.get('status') == 'success':
                            run_id = f"{result['prompt']}_{result['provider']}_{result['model']}"
                            completed.add(run_id)
            except Exception:
                # If we can't read a file, just skip it
                continue
        
        return completed

    def _run_workflow(self, provider: LLMProvider, prompt_name: str, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the LangGraph workflow for a provider with specific prompts."""
        # Create a unique identifier for this prompt/model combination
        run_id = f"{prompt_name}_{provider.provider_name}_{provider.model_name}"
        
        # Check if already completed in previous runs (not forcing rerun)
        # Note: _run_tracker is checked before submitting tasks, not here
        if not self.rerun_existing and run_id in self._completed_runs:
            provider.get_logger().info(f"Skipping previously completed combination: {run_id}")
            return {
                "prompt": prompt_name,
                "provider": provider.provider_name,
                "model": provider.model_name,
                "status": "skipped",
                "reason": "Already completed in previous run"
            }
        
        try:
            # Check if this provider supports system prompts
            use_system_prompt = provider.supports_system_prompt()
            
            # Get system prompt from prompt config
            system_prompt = prompt_config.get('system_prompt', '')
            test_prompt = prompt_config.get('test_prompt', '')
            
            # Create workflow graph
            graph = WorkflowGraph(
                llm_client=provider.get_client(),
                logger=provider.get_logger(),
                system_prompt=system_prompt,
                use_system_prompt=use_system_prompt,
                prompt_config=prompt_config,
                prompt_name=prompt_name
            )
            
            # Execute workflow
            final_state = graph.run(test_prompt)
            
            # Access error from dict-like object (LangGraph returns AddableValuesDict)
            error = final_state.get("error")
            if error:
                return {
                    "prompt": prompt_name,
                    "provider": provider.provider_name,
                    "model": provider.model_name,
                    "status": "error",
                    "error": error
                }
            
            return {
                "prompt": prompt_name,
                "provider": provider.provider_name,
                "model": provider.model_name,
                "status": "success",
                "response": {
                    "analysis": final_state["analysis"].model_dump(),
                    "solution": final_state["solution"].model_dump(),
                    "verification": final_state["verification"].model_dump()
                }
            }
            
        except Exception as e:
            provider.get_logger().error(f"Workflow error: {str(e)}", exc_info=True)
            return {
                "prompt": prompt_name,
                "provider": provider.provider_name,
                "model": provider.model_name,
                "status": "error",
                "error": str(e)
            }
    
    def _save_results(self) -> None:
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(self.config.results_dir) / f"benchmark_results_{timestamp}.json"
        
        # Collect all prompts used
        prompts_used = []
        for result in self.results:
            if result['status'] == 'success':
                prompt_name = result.get('prompt', 'unknown')
                if prompt_name not in prompts_used:
                    prompts_used.append(prompt_name)
        
        output = {
            "timestamp": timestamp,
            "prompts_used": prompts_used,
            "workflow": "analyze -> solve -> verify",
            "results": self.results,
            "summary": self._generate_summary()
        }
        
        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'success')
        skipped = sum(1 for r in self.results if r['status'] == 'skipped')
        failed = total - successful - skipped
        
        # Count correct verifications
        verified_correct = sum(
            1 for r in self.results 
            if r['status'] == 'success' and r['response']['verification']['is_correct']
        )
        
        # Count unique prompts tested (excluding skipped)
        prompts_used = set(r.get('prompt', 'unknown') for r in self.results 
                          if r.get('status') != 'skipped')
        
        return {
            "total_prompts": len(prompts_used),
            "total_models": total,
            "successful": successful,
            "skipped": skipped,
            "failed": failed,
            "verified_correct": verified_correct,
            "success_rate": f"{(successful/(total-skipped)*100):.1f}%" if (total-skipped) > 0 else "0%",
            "accuracy_rate": f"{(verified_correct/successful*100):.1f}%" if successful > 0 else "0%"
        }
    
    def _print_summary(self) -> None:
        """Print summary to console."""
        summary = self._generate_summary()
        
        print(f"\n{'='*70}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*70}")
        print(f"Total Prompts Tested: {summary['total_prompts']}")
        print(f"Total Models Tested: {summary['total_models']}")
        print(f"Successful: {summary['successful']}")
        if summary['skipped'] > 0:
            print(f"Skipped: {summary['skipped']}")
        print(f"Failed: {summary['failed']}")
        print(f"Verified Correct: {summary['verified_correct']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Accuracy Rate: {summary['accuracy_rate']}")
        print(f"\nResults saved to: {self.config.results_dir}")
        print(f"Logs saved to: {self.config.logs_dir}")
        print(f"{'='*70}")
