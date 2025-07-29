"""
Autonomous AI Agent Configuration with MCP Integration
Optimized for Claude Code development
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, Field, validator
from enum import Enum

class AgentMode(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class MCPServerConfig(BaseSettings):
    """Configuration for MCP servers"""
    name: str
    command: str
    args: List[str] = []
    env: Dict[str, str] = {}
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3

class AutonomousAgentConfig(BaseSettings):
    """Main configuration for autonomous agent"""
    
    # Core Settings
    agent_name: str = Field(default="AutonomousAgent", description="Agent identifier")
    mode: AgentMode = Field(default=AgentMode.DEVELOPMENT, description="Operating mode")
    debug: bool = Field(default=True, description="Enable debug logging")
    
    # Claude Code Integration
    claude_api_key: str = Field(default="", description="Claude API key")
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model to use")
    claude_max_tokens: int = Field(default=4096, description="Max tokens per request")
    claude_temperature: float = Field(default=0.7, description="Response creativity")
    
    # MCP Configuration
    mcp_servers: Dict[str, MCPServerConfig] = Field(default_factory=dict)
    mcp_timeout: int = Field(default=30, description="MCP connection timeout")
    mcp_max_connections: int = Field(default=10, description="Max concurrent MCP connections")
    
    # Agent Capabilities
    enable_memory: bool = Field(default=True, description="Enable persistent memory")
    enable_learning: bool = Field(default=True, description="Enable learning from interactions")
    enable_planning: bool = Field(default=True, description="Enable multi-step planning")
    enable_reflection: bool = Field(default=True, description="Enable self-reflection")
    
    # Memory Configuration
    memory_backend: str = Field(default="sqlite", description="Memory storage backend")
    memory_db_path: str = Field(default="agent_memory.db", description="Memory database path")
    memory_max_entries: int = Field(default=10000, description="Max memory entries")
    memory_retention_days: int = Field(default=30, description="Memory retention period")
    
    # Performance Settings
    max_concurrent_tasks: int = Field(default=5, description="Max concurrent tasks")
    task_timeout: int = Field(default=300, description="Task timeout in seconds")
    response_cache_ttl: int = Field(default=3600, description="Response cache TTL")
    
    # Security Settings
    allowed_domains: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    rate_limit_requests: int = Field(default=100, description="Requests per minute limit")
    enable_sandbox: bool = Field(default=True, description="Enable code execution sandbox")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="autonomous_agent.log", description="Log file path")
    log_max_size: int = Field(default=10 * 1024 * 1024, description="Max log file size")
    log_backup_count: int = Field(default=5, description="Number of log backups")
    
    # Monitoring and Health
    health_check_interval: int = Field(default=60, description="Health check interval")
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=8080, description="Metrics server port")
    
    @validator('mode')
    def validate_mode(cls, v):
        if v not in AgentMode:
            raise ValueError(f'mode must be one of {list(AgentMode)}')
        return v
    
    @validator('claude_temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('claude_temperature must be between 0.0 and 1.0')
        return v
    
    def get_mcp_server_configs(self) -> List[MCPServerConfig]:
        """Get enabled MCP server configurations"""
        return [config for config in self.mcp_servers.values() if config.enabled]
    
    def add_mcp_server(self, name: str, command: str, args: List[str] = None, env: Dict[str, str] = None):
        """Add a new MCP server configuration"""
        self.mcp_servers[name] = MCPServerConfig(
            name=name,
            command=command,
            args=args or [],
            env=env or {}
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = "AGENT_"

# Default MCP server configurations
DEFAULT_MCP_SERVERS = {
    "filesystem": MCPServerConfig(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"],
        env={}
    ),
    "brave_search": MCPServerConfig(
        name="brave_search",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")}
    ),
    "github": MCPServerConfig(
        name="github",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")}
    ),
    "postgres": MCPServerConfig(
        name="postgres",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres"],
        env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL", "")}
    ),
    "sqlite": MCPServerConfig(
        name="sqlite",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "./agent_data.db"],
        env={}
    )
}

def create_default_config() -> AutonomousAgentConfig:
    """Create default configuration with recommended MCP servers"""
    config = AutonomousAgentConfig()
    config.mcp_servers = DEFAULT_MCP_SERVERS.copy()
    return config

def load_config(config_path: Optional[str] = None) -> AutonomousAgentConfig:
    """Load configuration from file or environment"""
    if config_path and Path(config_path).exists():
        # Load from JSON/YAML file if needed
        pass
    return AutonomousAgentConfig()
