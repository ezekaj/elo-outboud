"""
MCP (Model Context Protocol) Client Implementation
Provides standardized interface for connecting to MCP servers
"""

import json
import asyncio
import subprocess
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

class MCPServerStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True

@dataclass
class MCPTool:
    """Represents an MCP tool/function"""
    name: str
    description: str
    parameters: Dict[str, Any]
    server_name: str

class MCPClient:
    """Client for managing MCP server connections"""
    
    def __init__(self, config_path: str = None):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.server_processes: Dict[str, subprocess.Popen] = {}
        self.server_status: Dict[str, MCPServerStatus] = {}
        self.available_tools: Dict[str, MCPTool] = {}
        self.logger = logging.getLogger(__name__)
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load MCP server configuration from file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            for server_name, server_config in config_data.get("servers", {}).items():
                self.servers[server_name] = MCPServerConfig(
                    name=server_config["name"],
                    command=server_config["command"],
                    args=server_config["args"],
                    env=server_config.get("env", {}),
                    timeout=server_config.get("timeout", 30),
                    max_retries=server_config.get("max_retries", 3),
                    enabled=server_config.get("enabled", True)
                )
                self.server_status[server_name] = MCPServerStatus.STOPPED
            
            self.logger.info(f"Loaded configuration for {len(self.servers)} MCP servers")
            
        except Exception as e:
            self.logger.error(f"Failed to load MCP config: {e}")
    
    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server"""
        if server_name not in self.servers:
            self.logger.error(f"Server {server_name} not found in configuration")
            return False
        
        config = self.servers[server_name]
        if not config.enabled:
            self.logger.info(f"Server {server_name} is disabled")
            return False
        
        if self.server_status[server_name] == MCPServerStatus.RUNNING:
            self.logger.info(f"Server {server_name} is already running")
            return True
        
        try:
            self.server_status[server_name] = MCPServerStatus.STARTING
            self.logger.info(f"Starting MCP server: {server_name}")
            
            # Prepare environment
            env = dict(os.environ)
            env.update(config.env)
            
            # Start the server process
            process = subprocess.Popen(
                [config.command] + config.args,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.server_processes[server_name] = process
            
            # Wait for server to be ready (simplified check)
            await asyncio.sleep(2)
            
            if process.poll() is None:  # Process is still running
                self.server_status[server_name] = MCPServerStatus.RUNNING
                self.logger.info(f"MCP server {server_name} started successfully")
                
                # Discover available tools
                await self._discover_tools(server_name)
                return True
            else:
                self.server_status[server_name] = MCPServerStatus.ERROR
                self.logger.error(f"MCP server {server_name} failed to start")
                return False
                
        except Exception as e:
            self.server_status[server_name] = MCPServerStatus.ERROR
            self.logger.error(f"Failed to start MCP server {server_name}: {e}")
            return False
    
    async def stop_server(self, server_name: str) -> bool:
        """Stop an MCP server"""
        if server_name not in self.server_processes:
            return True
        
        try:
            process = self.server_processes[server_name]
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process(process)),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                # Force kill if graceful shutdown fails
                process.kill()
                await asyncio.create_task(self._wait_for_process(process))
            
            del self.server_processes[server_name]
            self.server_status[server_name] = MCPServerStatus.STOPPED
            
            # Remove tools from this server
            tools_to_remove = [
                tool_name for tool_name, tool in self.available_tools.items()
                if tool.server_name == server_name
            ]
            for tool_name in tools_to_remove:
                del self.available_tools[tool_name]
            
            self.logger.info(f"MCP server {server_name} stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop MCP server {server_name}: {e}")
            return False
    
    async def _wait_for_process(self, process: subprocess.Popen):
        """Wait for process to terminate"""
        while process.poll() is None:
            await asyncio.sleep(0.1)
    
    async def _discover_tools(self, server_name: str):
        """Discover available tools from an MCP server"""
        # This is a simplified implementation
        # In practice, you'd use the MCP protocol to query available tools
        
        try:
            # Simulate tool discovery based on server type
            if "filesystem" in server_name:
                tools = [
                    MCPTool("read_file", "Read a file", {"path": "string"}, server_name),
                    MCPTool("write_file", "Write to a file", {"path": "string", "content": "string"}, server_name),
                    MCPTool("list_directory", "List directory contents", {"path": "string"}, server_name)
                ]
            elif "brave_search" in server_name:
                tools = [
                    MCPTool("web_search", "Search the web", {"query": "string", "count": "number"}, server_name)
                ]
            elif "github" in server_name:
                tools = [
                    MCPTool("list_repos", "List repositories", {"user": "string"}, server_name),
                    MCPTool("get_file", "Get file content", {"repo": "string", "path": "string"}, server_name),
                    MCPTool("create_issue", "Create an issue", {"repo": "string", "title": "string", "body": "string"}, server_name)
                ]
            elif "sqlite" in server_name:
                tools = [
                    MCPTool("query", "Execute SQL query", {"sql": "string"}, server_name),
                    MCPTool("schema", "Get database schema", {}, server_name)
                ]
            else:
                tools = []
            
            for tool in tools:
                self.available_tools[f"{server_name}.{tool.name}"] = tool
            
            self.logger.info(f"Discovered {len(tools)} tools from server {server_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to discover tools from {server_name}: {e}")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        if tool_name not in self.available_tools:
            return {"error": f"Tool {tool_name} not found"}
        
        tool = self.available_tools[tool_name]
        server_name = tool.server_name
        
        if self.server_status.get(server_name) != MCPServerStatus.RUNNING:
            return {"error": f"Server {server_name} is not running"}
        
        try:
            # This is a simplified implementation
            # In practice, you'd use the MCP protocol to call the tool
            
            # Simulate tool execution based on tool type
            if tool.name == "read_file":
                return await self._simulate_read_file(parameters)
            elif tool.name == "web_search":
                return await self._simulate_web_search(parameters)
            elif tool.name == "query":
                return await self._simulate_sql_query(parameters)
            else:
                return {"error": f"Tool {tool.name} not implemented"}
                
        except Exception as e:
            self.logger.error(f"Failed to call tool {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def _simulate_read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate file reading (placeholder)"""
        file_path = parameters.get("path")
        if not file_path:
            return {"error": "Missing path parameter"}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    async def _simulate_web_search(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate web search (placeholder)"""
        query = parameters.get("query")
        if not query:
            return {"error": "Missing query parameter"}
        
        # Placeholder response
        return {
            "success": True,
            "results": [
                {"title": f"Result for {query}", "url": "https://example.com", "description": "Sample result"}
            ]
        }
    
    async def _simulate_sql_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate SQL query (placeholder)"""
        sql = parameters.get("sql")
        if not sql:
            return {"error": "Missing sql parameter"}
        
        # Placeholder response
        return {
            "success": True,
            "rows": [],
            "columns": [],
            "affected_rows": 0
        }
    
    def get_server_status(self, server_name: str) -> MCPServerStatus:
        """Get the status of an MCP server"""
        return self.server_status.get(server_name, MCPServerStatus.STOPPED)
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        tools = []
        for tool_name, tool in self.available_tools.items():
            tools.append({
                "name": tool_name,
                "description": tool.description,
                "parameters": tool.parameters,
                "server": tool.server_name
            })
        return tools
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all servers"""
        health_status = {}
        
        for server_name in self.servers:
            status = self.server_status.get(server_name, MCPServerStatus.STOPPED)
            
            if status == MCPServerStatus.RUNNING:
                # Check if process is still alive
                process = self.server_processes.get(server_name)
                if process and process.poll() is None:
                    health_status[server_name] = "healthy"
                else:
                    health_status[server_name] = "unhealthy"
                    self.server_status[server_name] = MCPServerStatus.ERROR
            else:
                health_status[server_name] = status.value
        
        return health_status
    
    async def start_all_enabled_servers(self) -> Dict[str, bool]:
        """Start all enabled servers"""
        results = {}
        
        for server_name, config in self.servers.items():
            if config.enabled:
                results[server_name] = await self.start_server(server_name)
            else:
                results[server_name] = False
        
        return results
    
    async def stop_all_servers(self) -> Dict[str, bool]:
        """Stop all running servers"""
        results = {}
        
        for server_name in list(self.server_processes.keys()):
            results[server_name] = await self.stop_server(server_name)
        
        return results

# Global MCP client instance
mcp_client = MCPClient()
