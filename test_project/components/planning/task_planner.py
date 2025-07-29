"""
Task Planning Component for Autonomous Agents
Provides multi-step planning, execution tracking, and adaptive planning capabilities
"""

import json
import uuid
import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Represents a single task in a plan"""
    id: str
    name: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    dependencies: List[str]
    estimated_duration: int  # in minutes
    actual_duration: Optional[int] = None
    created_at: datetime.datetime = None
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create from dictionary"""
        data['status'] = TaskStatus(data['status'])
        data['priority'] = TaskPriority(data['priority'])
        if data.get('created_at'):
            data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            data['started_at'] = datetime.datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.datetime.fromisoformat(data['completed_at'])
        return cls(**data)

@dataclass
class Plan:
    """Represents a complete execution plan"""
    id: str
    name: str
    description: str
    tasks: List[Task]
    created_at: datetime.datetime
    status: TaskStatus
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class TaskPlanner:
    """Advanced task planning and execution management"""
    
    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.task_executors: Dict[str, Callable] = {}
        self.current_plan: Optional[Plan] = None
    
    def create_plan(self, name: str, description: str, goal: str) -> str:
        """Create a new execution plan"""
        plan_id = str(uuid.uuid4())
        
        plan = Plan(
            id=plan_id,
            name=name,
            description=description,
            tasks=[],
            created_at=datetime.datetime.now(),
            status=TaskStatus.PENDING,
            metadata={'goal': goal}
        )
        
        self.plans[plan_id] = plan
        return plan_id
    
    def add_task(self, 
                plan_id: str,
                name: str,
                description: str,
                priority: TaskPriority = TaskPriority.MEDIUM,
                dependencies: List[str] = None,
                estimated_duration: int = 30,
                metadata: Dict[str, Any] = None) -> str:
        """Add a task to a plan"""
        
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=name,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            dependencies=dependencies or [],
            estimated_duration=estimated_duration,
            metadata=metadata or {}
        )
        
        self.plans[plan_id].tasks.append(task)
        return task_id
    
    def decompose_complex_task(self, 
                              plan_id: str,
                              complex_task_description: str,
                              max_subtasks: int = 10) -> List[str]:
        """Decompose a complex task into smaller subtasks"""
        
        # This is a simplified decomposition - in practice, you'd use
        # more sophisticated planning algorithms or LLM-based decomposition
        
        subtasks = []
        
        # Basic decomposition patterns
        if "research" in complex_task_description.lower():
            subtasks.extend([
                "Define research objectives and scope",
                "Identify relevant sources and databases",
                "Gather initial information",
                "Analyze and synthesize findings",
                "Prepare research report"
            ])
        elif "develop" in complex_task_description.lower() or "code" in complex_task_description.lower():
            subtasks.extend([
                "Analyze requirements and specifications",
                "Design system architecture",
                "Implement core functionality",
                "Write tests and documentation",
                "Review and optimize code"
            ])
        elif "analyze" in complex_task_description.lower():
            subtasks.extend([
                "Collect and prepare data",
                "Perform exploratory analysis",
                "Apply analytical methods",
                "Interpret results",
                "Generate insights and recommendations"
            ])
        else:
            # Generic decomposition
            subtasks.extend([
                "Plan and prepare for task",
                "Execute main task activities",
                "Review and validate results",
                "Document outcomes and learnings"
            ])
        
        # Add subtasks to plan
        task_ids = []
        for i, subtask in enumerate(subtasks[:max_subtasks]):
            task_id = self.add_task(
                plan_id=plan_id,
                name=f"Subtask {i+1}: {subtask}",
                description=subtask,
                priority=TaskPriority.MEDIUM,
                dependencies=task_ids[-1:] if task_ids else [],
                estimated_duration=20
            )
            task_ids.append(task_id)
        
        return task_ids
    
    def get_next_tasks(self, plan_id: str) -> List[Task]:
        """Get the next tasks that can be executed"""
        if plan_id not in self.plans:
            return []
        
        plan = self.plans[plan_id]
        available_tasks = []
        
        for task in plan.tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                dependencies_met = all(
                    self._get_task_by_id(plan_id, dep_id).status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                )
                
                if dependencies_met:
                    available_tasks.append(task)
        
        # Sort by priority and creation time
        available_tasks.sort(
            key=lambda t: (t.priority.value, t.created_at),
            reverse=True
        )
        
        return available_tasks
    
    def start_task(self, plan_id: str, task_id: str) -> bool:
        """Mark a task as started"""
        task = self._get_task_by_id(plan_id, task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.datetime.now()
            return True
        return False
    
    def complete_task(self, plan_id: str, task_id: str, result: Any = None) -> bool:
        """Mark a task as completed"""
        task = self._get_task_by_id(plan_id, task_id)
        if task and task.status == TaskStatus.IN_PROGRESS:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.datetime.now()
            
            if task.started_at:
                duration = (task.completed_at - task.started_at).total_seconds() / 60
                task.actual_duration = int(duration)
            
            if result is not None:
                task.metadata['result'] = result
            
            # Check if plan is complete
            self._update_plan_status(plan_id)
            return True
        return False
    
    def fail_task(self, plan_id: str, task_id: str, error_message: str) -> bool:
        """Mark a task as failed"""
        task = self._get_task_by_id(plan_id, task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = error_message
            task.completed_at = datetime.datetime.now()
            
            if task.started_at:
                duration = (task.completed_at - task.started_at).total_seconds() / 60
                task.actual_duration = int(duration)
            
            return True
        return False
    
    def get_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        """Get progress statistics for a plan"""
        if plan_id not in self.plans:
            return {}
        
        plan = self.plans[plan_id]
        total_tasks = len(plan.tasks)
        
        if total_tasks == 0:
            return {'progress': 0, 'total_tasks': 0}
        
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(
                1 for task in plan.tasks if task.status == status
            )
        
        completed = status_counts.get(TaskStatus.COMPLETED.value, 0)
        progress = (completed / total_tasks) * 100
        
        estimated_total_time = sum(task.estimated_duration for task in plan.tasks)
        actual_total_time = sum(
            task.actual_duration for task in plan.tasks 
            if task.actual_duration is not None
        )
        
        return {
            'progress': round(progress, 2),
            'total_tasks': total_tasks,
            'status_counts': status_counts,
            'estimated_total_time': estimated_total_time,
            'actual_total_time': actual_total_time
        }
    
    def _get_task_by_id(self, plan_id: str, task_id: str) -> Optional[Task]:
        """Get a task by ID from a plan"""
        if plan_id not in self.plans:
            return None
        
        for task in self.plans[plan_id].tasks:
            if task.id == task_id:
                return task
        return None
    
    def _update_plan_status(self, plan_id: str):
        """Update the overall plan status based on task statuses"""
        if plan_id not in self.plans:
            return
        
        plan = self.plans[plan_id]
        if not plan.tasks:
            return
        
        all_completed = all(task.status == TaskStatus.COMPLETED for task in plan.tasks)
        any_failed = any(task.status == TaskStatus.FAILED for task in plan.tasks)
        any_in_progress = any(task.status == TaskStatus.IN_PROGRESS for task in plan.tasks)
        
        if all_completed:
            plan.status = TaskStatus.COMPLETED
        elif any_failed:
            plan.status = TaskStatus.FAILED
        elif any_in_progress:
            plan.status = TaskStatus.IN_PROGRESS
        else:
            plan.status = TaskStatus.PENDING
    
    def export_plan(self, plan_id: str, file_path: str):
        """Export a plan to JSON file"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.plans[plan_id]
        plan_data = {
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'created_at': plan.created_at.isoformat(),
            'status': plan.status.value,
            'metadata': plan.metadata,
            'tasks': [task.to_dict() for task in plan.tasks]
        }
        
        with open(file_path, 'w') as f:
            json.dump(plan_data, f, indent=2)
