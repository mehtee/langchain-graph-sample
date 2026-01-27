"""Configuration management."""
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import json
from dotenv import load_dotenv


class Config:
    """Configuration loader and manager."""
    
    def __init__(self, config_path: str = "config.yaml", prompts_dir: str = "prompts"):
        load_dotenv()
        self.config_path = Path(config_path)
        self.prompts_dir = Path(prompts_dir)
        self._config = self._load_config()
        self._prompts_cache = {}
        self._available_prompts = self._scan_prompt_files()
        self._setup_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _scan_prompt_files(self) -> List[str]:
        """Scan the prompts directory for JSON files."""
        if not self.prompts_dir.exists():
            return []
        
        files = []
        for file_path in self.prompts_dir.glob("*.json"):
            if file_path.is_file():
                files.append(file_path.stem)  # Store without .json extension
        return sorted(files)
    
    def _load_prompt_file(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a specific prompt file."""
        file_path = self.prompts_dir / f"{name}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _setup_directories(self) -> None:
        """Create output directories if they don't exist."""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
    
    @property
    def available_prompts(self) -> List[str]:
        """Get list of available prompt file names (without .json)."""
        return self._available_prompts
    
    def get_prompt(self, name: str) -> Optional[Dict[str, Any]]:
        """Get prompt configuration by name (without .json extension)."""
        if name not in self._prompts_cache:
            prompt_data = self._load_prompt_file(name)
            if prompt_data:
                self._prompts_cache[name] = prompt_data
            else:
                return None
        return self._prompts_cache[name]
    
    def get_default_prompt(self) -> Dict[str, Any]:
        """Get the first available prompt file."""
        if self._available_prompts:
            return self.get_prompt(self._available_prompts[0])
        return None
    
    def get_node_prompt(self, prompt_name: str, node_name: str, 
                       default_template: str = "") -> str:
        """Get prompt template for a specific node."""
        prompt_data = self.get_prompt(prompt_name)
        if not prompt_data:
            return default_template
        
        nodes = prompt_data.get('nodes', {})
        node_config = nodes.get(node_name, {})
        return node_config.get('prompt', default_template)
    
    def get_node_system_prompt_flag(self, prompt_name: str, node_name: str) -> bool:
        """Check if system prompt should be included for a node."""
        prompt_data = self.get_prompt(prompt_name)
        if not prompt_data:
            return True  # Default to True
        
        nodes = prompt_data.get('nodes', {})
        node_config = nodes.get(node_name, {})
        return node_config.get('system_prompt_included', True)
    
    @property
    def providers(self) -> Dict[str, Any]:
        return self._config['providers']
    
    @property
    def results_dir(self) -> str:
        return self._config['output']['results_dir']
    
    @property
    def logs_dir(self) -> str:
        return self._config['output']['logs_dir']
    
    def get_api_key(self, env_var: str) -> str:
        """Get API key from environment variable."""
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"API key not found for {env_var}. Please set it in .env file.")
        return api_key
