"""
SwarmForge Tests
Unit and integration tests for the framework
"""

import pytest
import asyncio
from langchain_openai import ChatOpenAI
from agents import Agent, AgentPool, AgentConfig, AgentRole, ExecutionMode
from graph import SwarmGraph, MemoryManager, EvaluationEngine
from tools import get_tools, web_search, code_execution


# Mock LLM for testing
class MockLLM:
    def __call__(self, *args, **kwargs):
        return "Mock response"


@pytest.fixture
def mock_llm():
    return MockLLM()


class TestMemoryManager:
    """Test memory management"""
    
    def test_short_term_storage(self):
        memory = MemoryManager()
        memory.store_short_term("test_key", "test_value")
        assert memory.retrieve_short_term("test_key") == "test_value"
    
    def test_long_term_storage(self):
        memory = MemoryManager()
        memory.store_long_term("key1", "value1", category="test")
        assert memory.retrieve_long_term("key1", category="test") == "value1"
    
    def test_memory_search(self):
        memory = MemoryManager()
        memory.store_long_term("task_001", "data1", category="tasks")
        memory.store_long_term("task_002", "data2", category="tasks")
        
        results = memory.search_memory("task", category="tasks")
        assert len(results) == 2
    
    def test_memory_stats(self):
        memory = MemoryManager()
        memory.store_short_term("key1", "value1")
        memory.store_long_term("key2", "value2", category="test")
        
        stats = memory.get_memory_stats()
        assert stats["short_term_size"] == 1
        assert "test" in stats["long_term_categories"]


class TestEvaluationEngine:
    """Test evaluation engine"""
    
    def test_evaluate_output(self, mock_llm):
        evaluator = EvaluationEngine(mock_llm)
        criteria = {"relevance": "Is it relevant?"}
        
        result = evaluator.evaluate_output("test output", criteria)
        assert "overall_score" in result
        assert result["overall_score"] >= 0
    
    def test_batch_evaluate(self, mock_llm):
        evaluator = EvaluationEngine(mock_llm)
        outputs = ["output1", "output2"]
        criteria = {"quality": "Is it good?"}
        
        result = evaluator.batch_evaluate(outputs, criteria)
        assert len(result["evaluations"]) == 2
        assert "average_score" in result


class TestAgent:
    """Test individual agents"""
    
    @pytest.mark.asyncio
    async def test_agent_execution(self, mock_llm):
        config = AgentConfig(
            name="test_agent",
            role=AgentRole.RESEARCHER
        )
        agent = Agent(config, mock_llm)
        
        result = await agent.execute("test task")
        assert "test_agent" in result
        assert len(agent.execution_log) == 1
    
    def test_agent_memory(self, mock_llm):
        config = AgentConfig(name="test_agent", role=AgentRole.RESEARCHER)
        agent = Agent(config, mock_llm)
        
        agent.store_memory("key", "value")
        assert agent.retrieve_memory("key") == "value"


class TestAgentPool:
    """Test agent pool coordination"""
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self, mock_llm):
        pool = AgentPool(mock_llm)
        pool.add_agent(AgentConfig(name="agent1", role=AgentRole.RESEARCHER))
        pool.add_agent(AgentConfig(name="agent2", role=AgentRole.ANALYZER))
        
        pool.set_execution_mode(ExecutionMode.SEQUENTIAL)
        results = await pool.execute("test task")
        
        assert len(results) == 2
        assert "agent1" in results
        assert "agent2" in results
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, mock_llm):
        pool = AgentPool(mock_llm)
        pool.add_agent(AgentConfig(name="agent1", role=AgentRole.RESEARCHER))
        pool.add_agent(AgentConfig(name="agent2", role=AgentRole.ANALYZER))
        
        pool.set_execution_mode(ExecutionMode.PARALLEL)
        results = await pool.execute("test task")
        
        assert len(results) == 2


class TestSwarmGraph:
    """Test LangGraph workflow"""
    
    def test_graph_initialization(self, mock_llm):
        graph = SwarmGraph(mock_llm)
        assert graph.graph is not None
        assert graph.memory is not None
        assert graph.evaluator is not None
    
    def test_graph_execution(self, mock_llm):
        graph = SwarmGraph(mock_llm)
        result = graph.run("test task")
        
        assert result["status"] == "completed"
        assert result["task"] == "test task"


class TestTools:
    """Test tool functions"""
    
    def test_get_all_tools(self):
        tools = get_tools()
        assert len(tools) > 0
    
    def test_get_specific_tools(self):
        tools = get_tools(["web_search", "code_execution"])
        assert len(tools) == 2


# Run tests with: pytest tests.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
