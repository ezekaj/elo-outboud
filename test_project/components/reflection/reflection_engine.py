"""
Self-Reflection Engine for Autonomous Agents
Provides capabilities for self-assessment, learning, and continuous improvement
"""

import json
import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

class ReflectionType(Enum):
    TASK_COMPLETION = "task_completion"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE_REVIEW = "performance_review"
    LEARNING_INSIGHT = "learning_insight"
    STRATEGY_EVALUATION = "strategy_evaluation"
    GOAL_ASSESSMENT = "goal_assessment"

class ImprovementArea(Enum):
    EFFICIENCY = "efficiency"
    ACCURACY = "accuracy"
    COMMUNICATION = "communication"
    PLANNING = "planning"
    PROBLEM_SOLVING = "problem_solving"
    KNOWLEDGE = "knowledge"
    TOOL_USAGE = "tool_usage"

@dataclass
class ReflectionEntry:
    """Represents a single reflection entry"""
    id: str
    type: ReflectionType
    timestamp: datetime.datetime
    context: str
    observations: List[str]
    insights: List[str]
    improvement_areas: List[ImprovementArea]
    action_items: List[str]
    confidence_score: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['type'] = self.type.value
        data['timestamp'] = self.timestamp.isoformat()
        data['improvement_areas'] = [area.value for area in self.improvement_areas]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReflectionEntry':
        """Create from dictionary"""
        data['type'] = ReflectionType(data['type'])
        data['timestamp'] = datetime.datetime.fromisoformat(data['timestamp'])
        data['improvement_areas'] = [ImprovementArea(area) for area in data['improvement_areas']]
        return cls(**data)

@dataclass
class PerformanceMetrics:
    """Performance metrics for reflection analysis"""
    task_completion_rate: float
    average_task_duration: float
    error_rate: float
    user_satisfaction: float
    goal_achievement_rate: float
    efficiency_score: float
    learning_rate: float

class ReflectionEngine:
    """Engine for self-reflection and continuous improvement"""
    
    def __init__(self, memory_manager=None):
        self.reflections: List[ReflectionEntry] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.memory_manager = memory_manager
        self.improvement_strategies: Dict[ImprovementArea, List[str]] = {
            ImprovementArea.EFFICIENCY: [
                "Break down complex tasks into smaller steps",
                "Use parallel processing when possible",
                "Cache frequently used information",
                "Optimize tool usage patterns"
            ],
            ImprovementArea.ACCURACY: [
                "Double-check critical information",
                "Use multiple sources for verification",
                "Implement validation steps",
                "Learn from past errors"
            ],
            ImprovementArea.COMMUNICATION: [
                "Ask clarifying questions when uncertain",
                "Provide clear explanations of reasoning",
                "Use appropriate level of detail",
                "Confirm understanding before proceeding"
            ],
            ImprovementArea.PLANNING: [
                "Spend more time on initial planning",
                "Consider multiple approaches",
                "Identify potential obstacles early",
                "Build in contingency plans"
            ],
            ImprovementArea.PROBLEM_SOLVING: [
                "Apply systematic problem-solving methods",
                "Consider alternative perspectives",
                "Break problems into components",
                "Learn from similar past problems"
            ],
            ImprovementArea.KNOWLEDGE: [
                "Identify knowledge gaps proactively",
                "Seek additional information when needed",
                "Update knowledge base regularly",
                "Cross-reference information sources"
            ],
            ImprovementArea.TOOL_USAGE: [
                "Learn advanced features of existing tools",
                "Explore new tools for specific tasks",
                "Optimize tool selection for each task",
                "Automate repetitive tool operations"
            ]
        }
    
    def reflect_on_task_completion(self, 
                                  task_context: str,
                                  success: bool,
                                  duration: float,
                                  challenges: List[str],
                                  outcomes: List[str]) -> str:
        """Reflect on a completed task"""
        
        observations = []
        insights = []
        improvement_areas = []
        action_items = []
        
        # Analyze task completion
        if success:
            observations.append(f"Task completed successfully in {duration:.1f} minutes")
            if duration > 60:  # If task took longer than expected
                insights.append("Task took longer than typical - consider better planning")
                improvement_areas.append(ImprovementArea.EFFICIENCY)
                action_items.append("Analyze time-consuming steps for optimization")
        else:
            observations.append("Task was not completed successfully")
            insights.append("Need to analyze failure points and prevention strategies")
            improvement_areas.append(ImprovementArea.PROBLEM_SOLVING)
            action_items.append("Develop contingency plans for similar tasks")
        
        # Analyze challenges
        for challenge in challenges:
            observations.append(f"Challenge encountered: {challenge}")
            if "unclear" in challenge.lower() or "ambiguous" in challenge.lower():
                improvement_areas.append(ImprovementArea.COMMUNICATION)
                action_items.append("Ask more clarifying questions upfront")
            elif "knowledge" in challenge.lower() or "information" in challenge.lower():
                improvement_areas.append(ImprovementArea.KNOWLEDGE)
                action_items.append("Identify and fill knowledge gaps")
        
        # Generate insights from outcomes
        for outcome in outcomes:
            insights.append(f"Outcome achieved: {outcome}")
        
        # Calculate confidence score based on success and challenges
        confidence_score = 0.8 if success else 0.3
        confidence_score -= len(challenges) * 0.1
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        reflection_id = self._generate_reflection_id()
        reflection = ReflectionEntry(
            id=reflection_id,
            type=ReflectionType.TASK_COMPLETION,
            timestamp=datetime.datetime.now(),
            context=task_context,
            observations=observations,
            insights=insights,
            improvement_areas=list(set(improvement_areas)),
            action_items=action_items,
            confidence_score=confidence_score,
            metadata={
                'success': success,
                'duration': duration,
                'challenges_count': len(challenges),
                'outcomes_count': len(outcomes)
            }
        )
        
        self.reflections.append(reflection)
        
        # Store in memory if available
        if self.memory_manager:
            self.memory_manager.store_memory(
                content=f"Task reflection: {task_context}",
                memory_type="reflection",
                metadata=reflection.to_dict(),
                importance=confidence_score,
                tags=["reflection", "task_completion"]
            )
        
        return reflection_id
    
    def reflect_on_error(self, 
                        error_context: str,
                        error_message: str,
                        attempted_solutions: List[str],
                        resolution: Optional[str] = None) -> str:
        """Reflect on an error and learning opportunities"""
        
        observations = [
            f"Error occurred: {error_message}",
            f"Context: {error_context}",
            f"Attempted {len(attempted_solutions)} solutions"
        ]
        
        insights = []
        improvement_areas = []
        action_items = []
        
        # Analyze error type and generate insights
        if "syntax" in error_message.lower() or "format" in error_message.lower():
            insights.append("Syntax or format error - need better validation")
            improvement_areas.append(ImprovementArea.ACCURACY)
            action_items.append("Implement pre-execution validation checks")
        elif "permission" in error_message.lower() or "access" in error_message.lower():
            insights.append("Permission/access error - need better environment setup")
            improvement_areas.append(ImprovementArea.PLANNING)
            action_items.append("Verify permissions before attempting operations")
        elif "timeout" in error_message.lower():
            insights.append("Timeout error - need better resource management")
            improvement_areas.append(ImprovementArea.EFFICIENCY)
            action_items.append("Optimize operations for better performance")
        else:
            insights.append("Unexpected error - need deeper analysis")
            improvement_areas.append(ImprovementArea.PROBLEM_SOLVING)
            action_items.append("Research error patterns and prevention strategies")
        
        # Analyze attempted solutions
        for solution in attempted_solutions:
            observations.append(f"Attempted solution: {solution}")
        
        if resolution:
            insights.append(f"Resolution found: {resolution}")
            action_items.append("Document successful resolution for future reference")
        
        confidence_score = 0.6 if resolution else 0.2
        
        reflection_id = self._generate_reflection_id()
        reflection = ReflectionEntry(
            id=reflection_id,
            type=ReflectionType.ERROR_ANALYSIS,
            timestamp=datetime.datetime.now(),
            context=error_context,
            observations=observations,
            insights=insights,
            improvement_areas=list(set(improvement_areas)),
            action_items=action_items,
            confidence_score=confidence_score,
            metadata={
                'error_message': error_message,
                'solutions_attempted': len(attempted_solutions),
                'resolved': resolution is not None
            }
        )
        
        self.reflections.append(reflection)
        
        if self.memory_manager:
            self.memory_manager.store_memory(
                content=f"Error reflection: {error_message}",
                memory_type="reflection",
                metadata=reflection.to_dict(),
                importance=0.8,  # Errors are important for learning
                tags=["reflection", "error", "learning"]
            )
        
        return reflection_id
    
    def generate_performance_review(self, time_period_days: int = 7) -> Dict[str, Any]:
        """Generate a comprehensive performance review"""
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=time_period_days)
        recent_reflections = [
            r for r in self.reflections 
            if r.timestamp >= cutoff_date
        ]
        
        if not recent_reflections:
            return {"message": "No recent reflections available for review"}
        
        # Analyze reflection patterns
        reflection_types = {}
        improvement_areas = {}
        confidence_scores = []
        
        for reflection in recent_reflections:
            # Count reflection types
            reflection_types[reflection.type.value] = reflection_types.get(reflection.type.value, 0) + 1
            
            # Count improvement areas
            for area in reflection.improvement_areas:
                improvement_areas[area.value] = improvement_areas.get(area.value, 0) + 1
            
            confidence_scores.append(reflection.confidence_score)
        
        # Calculate metrics
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
        
        # Identify top improvement areas
        top_improvement_areas = sorted(
            improvement_areas.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        # Generate recommendations
        recommendations = []
        for area_name, count in top_improvement_areas:
            area = ImprovementArea(area_name)
            strategies = self.improvement_strategies.get(area, [])
            recommendations.extend(strategies[:2])  # Top 2 strategies per area
        
        review = {
            'period_days': time_period_days,
            'total_reflections': len(recent_reflections),
            'average_confidence': round(avg_confidence, 2),
            'reflection_types': reflection_types,
            'top_improvement_areas': dict(top_improvement_areas),
            'recommendations': recommendations[:5],  # Top 5 recommendations
            'generated_at': datetime.datetime.now().isoformat()
        }
        
        return review
    
    def get_learning_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent learning insights from reflections"""
        
        learning_reflections = [
            r for r in self.reflections 
            if r.type in [ReflectionType.LEARNING_INSIGHT, ReflectionType.ERROR_ANALYSIS]
        ]
        
        # Sort by timestamp, most recent first
        learning_reflections.sort(key=lambda x: x.timestamp, reverse=True)
        
        insights = []
        for reflection in learning_reflections[:limit]:
            insight = {
                'timestamp': reflection.timestamp.isoformat(),
                'context': reflection.context,
                'key_insights': reflection.insights,
                'improvement_areas': [area.value for area in reflection.improvement_areas],
                'confidence': reflection.confidence_score
            }
            insights.append(insight)
        
        return insights
    
    def _generate_reflection_id(self) -> str:
        """Generate a unique reflection ID"""
        import uuid
        return str(uuid.uuid4())[:8]
