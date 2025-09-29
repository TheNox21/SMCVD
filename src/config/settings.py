"""
Enhanced configuration management with validation
"""
import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class APIConfig:
    """API configuration settings"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    cors_origins: str = "*"
    secret_key: str = "dev-secret-change-me"


@dataclass
class AnalysisConfig:
    """Analysis engine configuration"""
    min_confidence: float = 0.65
    enable_ai: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_files_per_analysis: int = 100
    analysis_timeout: int = 300  # 5 minutes


@dataclass
class AIConfig:
    """AI service configuration"""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    max_tokens: int = 1200
    temperature: float = 0.2
    timeout: int = 30


@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_path: str = "smcvd.db"
    cleanup_days: int = 7
    backup_enabled: bool = True


@dataclass
class SecurityConfig:
    """Security configuration"""
    rate_limit_per_minute: int = 10
    rate_limit_window: int = 60
    max_concurrent_analyses: int = 5
    allowed_file_extensions: list = None


class ConfigManager:
    """Configuration manager with validation"""
    
    def __init__(self):
        self.api = self._load_api_config()
        self.analysis = self._load_analysis_config()
        self.ai = self._load_ai_config()
        self.database = self._load_database_config()
        self.security = self._load_security_config()
        
        self._validate_config()
    
    def _load_api_config(self) -> APIConfig:
        return APIConfig(
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', '5000')),
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
            cors_origins=os.getenv('CORS_ORIGINS', '*'),
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-change-me')
        )
    
    def _load_analysis_config(self) -> AnalysisConfig:
        return AnalysisConfig(
            min_confidence=float(os.getenv('MIN_CONFIDENCE', '0.65')),
            enable_ai=os.getenv('ENABLE_AI', 'true').lower() == 'true',
            max_file_size=int(os.getenv('MAX_FILE_SIZE', str(10 * 1024 * 1024))),
            max_files_per_analysis=int(os.getenv('MAX_FILES_PER_ANALYSIS', '100')),
            analysis_timeout=int(os.getenv('ANALYSIS_TIMEOUT', '300'))
        )
    
    def _load_ai_config(self) -> AIConfig:
        return AIConfig(
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            openai_model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '1200')),
            temperature=float(os.getenv('AI_TEMPERATURE', '0.2')),
            timeout=int(os.getenv('AI_TIMEOUT', '30'))
        )
    
    def _load_database_config(self) -> DatabaseConfig:
        return DatabaseConfig(
            db_path=os.getenv('DB_PATH', 'smcvd.db'),
            cleanup_days=int(os.getenv('DB_CLEANUP_DAYS', '7')),
            backup_enabled=os.getenv('DB_BACKUP_ENABLED', 'true').lower() == 'true'
        )
    
    def _load_security_config(self) -> SecurityConfig:
        return SecurityConfig(
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '10')),
            rate_limit_window=int(os.getenv('RATE_LIMIT_WINDOW', '60')),
            max_concurrent_analyses=int(os.getenv('MAX_CONCURRENT_ANALYSES', '5')),
            allowed_file_extensions=['.sol', '.vy', '.fe']  # Solidity, Vyper, Fe
        )
    
    def _validate_config(self):
        """Validate configuration values"""
        if self.analysis.min_confidence < 0 or self.analysis.min_confidence > 1:
            raise ValueError("MIN_CONFIDENCE must be between 0 and 1")
        
        if self.analysis.enable_ai and not self.ai.openai_api_key:
            print("WARNING: AI is enabled but OPENAI_API_KEY is not set")
        
        if self.api.secret_key == "dev-secret-change-me":
            print("WARNING: Using default secret key. Set SECRET_KEY in production")
        
        if self.analysis.max_file_size > 50 * 1024 * 1024:  # 50MB
            print("WARNING: MAX_FILE_SIZE is very large, may impact performance")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'api': self.api.__dict__,
            'analysis': self.analysis.__dict__,
            'ai': {k: v if k != 'openai_api_key' else '***' for k, v in self.ai.__dict__.items()},
            'database': self.database.__dict__,
            'security': self.security.__dict__
        }


# Global configuration instance
config = ConfigManager()
