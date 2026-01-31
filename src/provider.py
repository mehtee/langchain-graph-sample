"""Provider abstraction for LLM clients."""
import logging
from typing import Dict, Any
from pathlib import Path
from langchain_openai import ChatOpenAI

from src.config import Config


class LLMProvider:
    """Abstract provider for LLM interactions."""
    
    def __init__(self, config: Config, provider_name: str, model_name: str):
        self.config = config
        self.provider_name = provider_name
        self.model_name = model_name
        self.provider_config = config.providers[provider_name]
        self.logger = self._setup_logger()
        self.client = self._create_client()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for this provider and model."""
        logger = logging.getLogger(f"{self.provider_name}.{self.model_name}")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = Path(self.config.logs_dir) / f"{self.provider_name}_{self.model_name.replace('/', '_').replace(':', '_')}.log"
        handler = logging.FileHandler(log_file, mode='w')
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def _create_client(self) -> ChatOpenAI:
        """Create OpenAI-compatible client."""
        api_key = self.config.get_api_key(self.provider_config['api_key_env'])
        
        self.logger.info(f"Initializing client for {self.provider_name}/{self.model_name}")
        
        # Get timeout from config, default to 60 seconds
        timeout_seconds = self.provider_config.get('timeout', 60)
        
        # Get default headers from config (for providers that require specific headers like ArvanCloud)
        default_headers = self.provider_config.get('default_headers', {})
        
        return ChatOpenAI(
            model=self.model_name,
            api_key=api_key,
            base_url=self.provider_config['base_url'],
            temperature=0.7,
            request_timeout=timeout_seconds,
            default_headers=default_headers if default_headers else None,
        )
    
    def get_client(self) -> ChatOpenAI:
        """Get the LLM client."""
        return self.client
    
    def get_logger(self) -> logging.Logger:
        """Get the logger."""
        return self.logger
    
    def supports_system_prompt(self) -> bool:
        """Check if this provider supports system prompts."""
        # Default is True, can be overridden in config
        return self.provider_config.get('supports_system_prompt', True)
