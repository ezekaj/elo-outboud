#!/usr/bin/env python3
"""
Test Agent - Autonomous AI Agent
Generated from template: autonomous_agent
"""

import asyncio
import json
import logging
from pathlib import Path

# Import components
from components.memory.memory_manager import MemoryManager
from components.planning.task_planner import TaskPlanner
from components.reflection.reflection_engine import ReflectionEngine
from components.tools.common_tools import tool_registry
from components.mcp_clients.mcp_client import MCPClient

class TestAgentAgent:
    """Main agent class"""
    
    def __init__(self, config_path: str = "agent_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.memory = MemoryManager()
        self.planner = TaskPlanner()
        self.reflection = ReflectionEngine(self.memory)
        self.mcp_client = MCPClient("mcp_servers.json")
        
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, self.config.get("logging", {}).get("level", "INFO")),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> dict:
        """Load agent configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            return {}
    
    async def start(self):
        """Start the agent"""
        self.logger.info("Starting Test Agent agent...")
        
        # Start MCP servers
        await self.mcp_client.start_all_enabled_servers()
        
        # Main agent loop
        await self.run()
    
    async def run(self):
        """Main agent execution loop"""
        self.logger.info("Agent is running...")
        
        # Example: Create a simple task plan
        plan_id = self.planner.create_plan(
            name="Initial Setup",
            description="Set up the agent and perform initial tasks",
            goal="Get the agent ready for operation"
        )
        
        # Add some example tasks
        self.planner.add_task(
            plan_id=plan_id,
            name="Initialize Memory",
            description="Set up memory management system"
        )
        
        self.planner.add_task(
            plan_id=plan_id,
            name="Test MCP Connections",
            description="Verify MCP server connections"
        )
        
        # Execute tasks
        while True:
            next_tasks = self.planner.get_next_tasks(plan_id)
            if not next_tasks:
                break
            
            for task in next_tasks[:1]:  # Execute one task at a time
                self.logger.info(f"Executing task: {task.name}")
                self.planner.start_task(plan_id, task.id)
                
                # Simulate task execution
                await asyncio.sleep(1)
                
                # Complete task
                self.planner.complete_task(plan_id, task.id)
                
                # Reflect on task completion
                self.reflection.reflect_on_task_completion(
                    task_context=task.description,
                    success=True,
                    duration=1.0,
                    challenges=[],
                    outcomes=[f"Completed {task.name}"]
                )
        
        self.logger.info("All tasks completed!")
    
    async def stop(self):
        """Stop the agent"""
        self.logger.info("Stopping agent...")
        await self.mcp_client.stop_all_servers()

async def main():
    """Main entry point"""
    agent = TestAgentAgent()
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
