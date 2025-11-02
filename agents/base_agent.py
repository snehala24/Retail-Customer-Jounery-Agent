from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from models import Customer, ConversationSession, AgentTask
import asyncio
import uuid
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.active_tasks: Dict[str, AgentTask] = {}
    
    @abstractmethod
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a task and return results"""
        pass
    
    async def execute_task(self, customer_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results"""
        task = AgentTask(
            id=str(uuid.uuid4()),
            agent_type=self.agent_type,
            customer_id=customer_id,
            task_data=task_data,
            status="processing"
        )
        
        self.active_tasks[task.id] = task
        
        try:
            result = await self.process_task(task)
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now()
            return result
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            task.completed_at = datetime.now()
            raise e
        finally:
            # Clean up completed task after 1 hour
            asyncio.create_task(self._cleanup_task(task.id, 3600))
    
    async def _cleanup_task(self, task_id: str, delay: int):
        """Clean up completed task after delay"""
        await asyncio.sleep(delay)
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
    
    def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """Get status of a specific task"""
        return self.active_tasks.get(task_id)
    
    def get_active_tasks(self) -> List[AgentTask]:
        """Get all active tasks for this agent"""
        return list(self.active_tasks.values())
