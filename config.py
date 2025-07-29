"""
Configuration management for Elo Dental Clinic system
"""
import os
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import List, Dict, Optional

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[+] Loaded environment variables from {env_path}")
except ImportError:
    print("[!] python-dotenv not available, skipping .env file loading")


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    path: str = Field(default="clinic.db", description="SQLite database file path")
    echo: bool = Field(default=False, description="Enable SQL query logging")
    
    class Config:
        env_prefix = "DB_"


class SecuritySettings(BaseSettings):
    """Security and rate limiting configuration"""
    max_calls_per_hour: int = Field(default=30, description="Maximum calls per hour")
    call_duration_limit: int = Field(default=300, description="Maximum call duration in seconds")
    allowed_hours: Dict[str, List[int]] = Field(default_factory=lambda: {
        "monday": [9, 10, 11, 14, 15, 16, 17],
        "tuesday": [9, 10, 11, 14, 15, 16, 17],
        "wednesday": [9, 10, 11, 14, 15, 16, 17],
        "thursday": [9, 10, 11, 14, 15, 16, 17],
        "friday": [9, 10, 11, 14, 15, 16, 17],
        "saturday": [9, 10, 11, 12, 13],
        "sunday": []
    })
    
    @field_validator('max_calls_per_hour')
    @classmethod
    def validate_max_calls(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('max_calls_per_hour must be between 1 and 100')
        return v

    @field_validator('call_duration_limit')
    @classmethod
    def validate_duration(cls, v):
        if v < 60 or v > 1800:  # 1 minute to 30 minutes
            raise ValueError('call_duration_limit must be between 60 and 1800 seconds')
        return v
    
    class Config:
        env_prefix = "SECURITY_"


class ClinicSettings(BaseSettings):
    """Clinic information configuration"""
    name: str = Field(default="Romi Dental Clinic", description="Clinic name")
    location: str = Field(default="Albania", description="Clinic location")
    services: List[str] = Field(default_factory=lambda: [
        "Regular check-ups and cleanings",
        "Cosmetic dentistry and whitening",
        "Emergency dental care",
        "Children's dentistry",
        "Dental implants and prosthetics"
    ])
    payment_methods: List[str] = Field(default_factory=lambda: [
        "Cash (Euro)",
        "Credit Cards",
        "Debit Cards",
        "Bank Transfers"
    ])
    working_hours: Dict[str, str] = Field(default_factory=lambda: {
        "monday": "9 AM - 6 PM",
        "tuesday": "9 AM - 6 PM",
        "wednesday": "9 AM - 6 PM",
        "thursday": "9 AM - 6 PM",
        "friday": "9 AM - 6 PM",
        "saturday": "9 AM - 2 PM",
        "sunday": "Closed"
    })
    consultation_fee: float = Field(default=50.0, description="Default consultation fee in EUR")
    
    class Config:
        env_prefix = "CLINIC_"


class LiveKitSettings(BaseSettings):
    """LiveKit configuration"""
    url: str = Field(default="wss://test.livekit.cloud", description="LiveKit server URL")
    api_key: str = Field(default="test-key", description="LiveKit API key")
    api_secret: str = Field(default="test-secret", description="LiveKit API secret")
    
    class Config:
        env_prefix = "LIVEKIT_"


class GoogleSettings(BaseSettings):
    """Google API configuration"""
    api_key: str = Field(default="test-google-key", description="Google Cloud API key")
    
    class Config:
        env_prefix = "GOOGLE_"


class LoggingSettings(BaseSettings):
    """Logging configuration"""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    file_path: Optional[str] = Field(default="elo_clinic.log", description="Log file path")
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Max log file size in bytes")
    backup_count: int = Field(default=5, description="Number of backup log files")
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f'level must be one of {valid_levels}')
        return v.upper()
    
    class Config:
        env_prefix = "LOG_"


class AppSettings(BaseSettings):
    """Main application settings"""
    # Environment
    environment: str = Field(default="development", description="Application environment")

    # API Keys - MUST be set via environment variables
    openai_api_key: str = Field(default="sk-placeholder", description="OpenAI API key (required for production)")
    lm_studio_api_key: str = Field(default="lm-studio", description="LM Studio API key")
    lm_studio_base_url: str = Field(default="http://localhost:1234/v1", description="LM Studio base URL")

    # Database
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Security
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    # Clinic
    clinic: ClinicSettings = Field(default_factory=ClinicSettings)

    # LiveKit
    livekit: LiveKitSettings = Field(default_factory=LiveKitSettings)

    # Google
    google: GoogleSettings = Field(default_factory=GoogleSettings)

    # Logging
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        valid_envs = {'development', 'staging', 'production'}
        if v.lower() not in valid_envs:
            raise ValueError(f'environment must be one of {valid_envs}')
        return v.lower()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = AppSettings()


def get_settings() -> AppSettings:
    """Get application settings"""
    return settings


def reload_settings():
    """Reload settings from environment"""
    global settings
    settings = AppSettings()
    return settings
