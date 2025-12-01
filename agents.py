"""
SwarmForge Agents Module
Multi-agent orchestration with parallel/sequential execution
"""

from typing import Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import BaseMessage
import asyncio
from datetime import datetime


class ExecutionMode(Enum):
    """Execution modes for agent workflows"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"


class AgentRole(Enum):
    """Types of agent roles"""
    RESEARCHER = "researcher"
    ANALYZER = "analyzer"
    SYNTHESIZER = "synthesizer"
    EXECUTOR = "executor"
    COORDINATOR = "coordinator"


@dataclass
class AgentConfig:
    """Configuration for an agent"""
    name: str
    role: AgentRole
    tools: List[str] = None
    memory_enabled: bool = True
    max_iterations: int = 5
    timeout: int = 30


class Agent:
    """Individual agent in the swarm"""
    
    def __init__(self, config: AgentConfig, llm: BaseLanguageModel):
        self.config = config
        self.llm = llm
        self.messages: List[BaseMessage] = []
        self.execution_log: List[dict] = []
        self.memory: dict = {}
        self.state = "idle"
    
    async def execute(self, task: str, context: Optional[dict] = None) -> str:
        """Execute a task with the given context"""
        self.state = "executing"
        start_time = datetime.now()
        
        try:
            # Simulate task execution
            result = f"Agent {self.config.name} ({self.config.role.value}) processed: {task[:100]}"
            
            # Log execution
            self.execution_log.append({
                "task": task,
                "result": result,
                "duration": (datetime.now() - start_time).total_seconds(),
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            })
            
            self.state = "idle"
            return result
        except Exception as e:
            self.execution_log.append({
                "task": task,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds(),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            })
            self.state = "error"
            raise
    
    def store_memory(self, key: str, value: Any):
        """Store information in agent memory"""
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def retrieve_memory(self, key: str) -> Optional[Any]:
        """Retrieve information from agent memory"""
        if key in self.memory:
            return self.memory[key]["value"]
        return None
    
    def get_execution_stats(self) -> dict:
        """Get agent execution statistics"""
        completed = [log for log in self.execution_log if log["status"] == "completed"]
        failed = [log for log in self.execution_log if log["status"] == "failed"]
        
        total_duration = sum(log["duration"] for log in self.execution_log)
        
        return {
            "agent_name": self.config.name,
            "total_executions": len(self.execution_log),
            "successful": len(completed),
            "failed": len(failed),
            "total_duration": total_duration,
            "avg_duration": total_duration / len(self.execution_log) if self.execution_log else 0
        }


class AgentPool:
    """Pool of agents that can be coordinated"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.agents: dict[str, Agent] = {}
        self.execution_mode = ExecutionMode.SEQUENTIAL
    
    def add_agent(self, config: AgentConfig):
        """Add an agent to the pool"""
        agent = Agent(config, self.llm)
        self.agents[config.name] = agent
        return agent
    
    def remove_agent(self, agent_name: str):
        """Remove an agent from the pool"""
        if agent_name in self.agents:
            del self.agents[agent_name]
    
    def set_execution_mode(self, mode: ExecutionMode):
        """Set the execution mode for the agent pool"""
        self.execution_mode = mode
    
    async def execute_sequential(self, task: str) -> dict:
        """Execute tasks sequentially across agents"""
        results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                result = await agent.execute(task)
                results[agent_name] = {
                    "status": "success",
                    "result": result
                }
            except Exception as e:
                results[agent_name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results
    
    async def execute_parallel(self, task: str) -> dict:
        """Execute tasks in parallel across agents"""
        tasks = [
            agent.execute(task)
            for agent in self.agents.values()
        ]
        
        results = {}
        if tasks:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for agent_name, response in zip(self.agents.keys(), responses):
                if isinstance(response, Exception):
                    results[agent_name] = {
                        "status": "failed",
                        "error": str(response)
                    }
                else:
                    results[agent_name] = {
                        "status": "success",
                        "result": response
                    }
        
        return results
    
    async def execute_hierarchical(self, task: str, coordinator: Optional[str] = None) -> dict:
        """Execute with hierarchical coordination"""
        # Find or designate coordinator
        if not coordinator and self.agents:
            # Default to first agent as coordinator
            coordinator = next(iter(self.agents.keys()))
        
        results = {}
        
        # Coordinator processes first
        if coordinator and coordinator in self.agents:
            coord_agent = self.agents[coordinator]
            try:
                coord_result = await coord_agent.execute(f"Coordinate: {task}")
                results["coordinator"] = {
                    "agent": coordinator,
                    "result": coord_result
                }
            except Exception as e:
                results["coordinator"] = {
                    "error": str(e)
                }
        
        # Other agents execute in parallel
        worker_agents = {
            name: agent for name, agent in self.agents.items()
            if name != coordinator
        }
        
        if worker_agents:
            worker_results = await asyncio.gather(
                *[agent.execute(task) for agent in worker_agents.values()],
                return_exceptions=True
            )
            
            results["workers"] = {}
            for agent_name, response in zip(worker_agents.keys(), worker_results):
                if isinstance(response, Exception):
                    results["workers"][agent_name] = {
                        "status": "failed",
                        "error": str(response)
                    }
                else:
                    results["workers"][agent_name] = {
                        "status": "success",
                        "result": response
                    }
        
        return results
    
    async def execute(self, task: str) -> dict:
        """Execute based on current execution mode"""
        if self.execution_mode == ExecutionMode.SEQUENTIAL:
            return await self.execute_sequential(task)
        elif self.execution_mode == ExecutionMode.PARALLEL:
            return await self.execute_parallel(task)
        elif self.execution_mode == ExecutionMode.HIERARCHICAL:
            return await self.execute_hierarchical(task)
        else:
            raise ValueError(f"Unknown execution mode: {self.execution_mode}")
    
    def get_pool_stats(self) -> dict:
        """Get statistics for all agents in the pool"""
        stats = {
            "total_agents": len(self.agents),
            "execution_mode": self.execution_mode.value,
            "agents": {}
        }
        
        for agent_name, agent in self.agents.items():
            stats["agents"][agent_name] = agent.get_execution_stats()
        
        return stats


class SwarmOrchestrator:
    """High-level orchestration for the entire swarm"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.agent_pools: dict[str, AgentPool] = {}
        self.task_queue: List[dict] = []
        self.execution_history: List[dict] = []
    
    def create_pool(self, pool_name: str) -> AgentPool:
        """Create a new agent pool"""
        pool = AgentPool(self.llm)
        self.agent_pools[pool_name] = pool
        return pool
    
    def get_pool(self, pool_name: str) -> Optional[AgentPool]:
        """Get an agent pool by name"""
        return self.agent_pools.get(pool_name)
    
    async def execute_task(self, pool_name: str, task: str) -> dict:
        """Execute a task on a specific agent pool"""
        pool = self.get_pool(pool_name)
        if not pool:
            raise ValueError(f"Pool '{pool_name}' not found")
        
        start_time = datetime.now()
        result = await pool.execute(task)
        duration = (datetime.now() - start_time).total_seconds()
        
        # Log execution
        execution_record = {
            "pool": pool_name,
            "task": task,
            "result": result,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.execution_history.append(execution_record)
        
        return execution_record
    
    def get_orchestration_stats(self) -> dict:
        """Get comprehensive orchestration statistics"""
        stats = {
            "total_pools": len(self.agent_pools),
            "total_executions": len(self.execution_history),
            "pools": {}
        }
        
        for pool_name, pool in self.agent_pools.items():
            stats["pools"][pool_name] = pool.get_pool_stats()
        
        return stats
