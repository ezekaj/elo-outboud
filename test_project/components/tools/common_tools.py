"""
Common Tool Implementations for Autonomous Agents
Provides reusable tools for file operations, web search, data processing, etc.
"""

import os
import json
import requests
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import hashlib
import datetime

class FileOperationsTool:
    """Tool for safe file operations"""
    
    def __init__(self, allowed_paths: List[str] = None, max_file_size: int = 10 * 1024 * 1024):
        self.allowed_paths = allowed_paths or ["./", "../"]
        self.max_file_size = max_file_size
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read a file safely"""
        try:
            path = Path(file_path).resolve()
            
            # Security check
            if not self._is_path_allowed(path):
                return {"error": f"Access denied to path: {file_path}"}
            
            if not path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if path.stat().st_size > self.max_file_size:
                return {"error": f"File too large: {file_path}"}
            
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": len(content),
                "path": str(path)
            }
            
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Write to a file safely"""
        try:
            path = Path(file_path).resolve()
            
            # Security check
            if not self._is_path_allowed(path):
                return {"error": f"Access denied to path: {file_path}"}
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check content size
            if len(content.encode(encoding)) > self.max_file_size:
                return {"error": "Content too large"}
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(path),
                "size": len(content)
            }
            
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}
    
    def list_directory(self, dir_path: str) -> Dict[str, Any]:
        """List directory contents"""
        try:
            path = Path(dir_path).resolve()
            
            if not self._is_path_allowed(path):
                return {"error": f"Access denied to path: {dir_path}"}
            
            if not path.exists():
                return {"error": f"Directory not found: {dir_path}"}
            
            if not path.is_dir():
                return {"error": f"Not a directory: {dir_path}"}
            
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            return {
                "success": True,
                "path": str(path),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is within allowed directories"""
        path_str = str(path)
        return any(path_str.startswith(allowed) for allowed in self.allowed_paths)

class WebSearchTool:
    """Tool for web search operations"""
    
    def __init__(self, api_key: str = None, search_engine: str = "brave"):
        self.api_key = api_key
        self.search_engine = search_engine
    
    def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform web search"""
        try:
            if self.search_engine == "brave" and self.api_key:
                return self._brave_search(query, num_results)
            else:
                return self._fallback_search(query, num_results)
                
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
    
    def _brave_search(self, query: str, num_results: int) -> Dict[str, Any]:
        """Search using Brave Search API"""
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            "count": num_results
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "published": item.get("age", "")
            })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    def _fallback_search(self, query: str, num_results: int) -> Dict[str, Any]:
        """Fallback search method (placeholder)"""
        return {
            "success": False,
            "error": "No search API configured",
            "suggestion": "Configure Brave Search API key for web search functionality"
        }

class DataProcessingTool:
    """Tool for data processing operations"""
    
    def __init__(self):
        pass
    
    def parse_json(self, json_string: str) -> Dict[str, Any]:
        """Parse JSON string safely"""
        try:
            data = json.loads(json_string)
            return {
                "success": True,
                "data": data,
                "type": type(data).__name__
            }
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}"}
    
    def format_json(self, data: Any, indent: int = 2) -> Dict[str, Any]:
        """Format data as JSON"""
        try:
            json_string = json.dumps(data, indent=indent, default=str)
            return {
                "success": True,
                "json": json_string,
                "size": len(json_string)
            }
        except Exception as e:
            return {"error": f"Failed to format JSON: {str(e)}"}
    
    def calculate_hash(self, content: str, algorithm: str = "sha256") -> Dict[str, Any]:
        """Calculate hash of content"""
        try:
            if algorithm == "md5":
                hash_obj = hashlib.md5()
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1()
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256()
            else:
                return {"error": f"Unsupported hash algorithm: {algorithm}"}
            
            hash_obj.update(content.encode('utf-8'))
            hash_value = hash_obj.hexdigest()
            
            return {
                "success": True,
                "hash": hash_value,
                "algorithm": algorithm,
                "content_length": len(content)
            }
            
        except Exception as e:
            return {"error": f"Failed to calculate hash: {str(e)}"}

class CodeExecutionTool:
    """Tool for safe code execution"""
    
    def __init__(self, allowed_languages: List[str] = None, timeout: int = 30):
        self.allowed_languages = allowed_languages or ["python", "javascript", "bash"]
        self.timeout = timeout
    
    def execute_python(self, code: str, capture_output: bool = True) -> Dict[str, Any]:
        """Execute Python code safely"""
        if "python" not in self.allowed_languages:
            return {"error": "Python execution not allowed"}
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute code
            result = subprocess.run(
                ["python", temp_file],
                capture_output=capture_output,
                text=True,
                timeout=self.timeout
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": f"Code execution timed out after {self.timeout} seconds"}
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}
    
    def execute_bash(self, command: str, capture_output: bool = True) -> Dict[str, Any]:
        """Execute bash command safely"""
        if "bash" not in self.allowed_languages:
            return {"error": "Bash execution not allowed"}
        
        # Basic security checks
        dangerous_commands = ["rm -rf", "sudo", "chmod 777", "dd if=", "> /dev/"]
        if any(dangerous in command for dangerous in dangerous_commands):
            return {"error": "Potentially dangerous command blocked"}
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {self.timeout} seconds"}
        except Exception as e:
            return {"error": f"Command failed: {str(e)}"}

class ToolRegistry:
    """Registry for managing and accessing tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        self.tools["file_operations"] = FileOperationsTool()
        self.tools["web_search"] = WebSearchTool()
        self.tools["data_processing"] = DataProcessingTool()
        self.tools["code_execution"] = CodeExecutionTool()
    
    def register_tool(self, name: str, tool: Any):
        """Register a custom tool"""
        self.tools[name] = tool
    
    def get_tool(self, name: str) -> Any:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List available tools"""
        return list(self.tools.keys())
    
    def execute_tool_function(self, tool_name: str, function_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool function with parameters"""
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                return {"error": f"Tool not found: {tool_name}"}
            
            if not hasattr(tool, function_name):
                return {"error": f"Function not found: {function_name}"}
            
            function = getattr(tool, function_name)
            result = function(**kwargs)
            
            return {
                "success": True,
                "tool": tool_name,
                "function": function_name,
                "result": result
            }
            
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

# Global tool registry instance
tool_registry = ToolRegistry()
