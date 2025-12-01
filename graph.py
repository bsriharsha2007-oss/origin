"""
SwarmForge Graph Module
LangGraph workflow orchestration with memory and evaluation
"""

from typing import Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models.base import BaseLanguageModel
import json
from datetime import datetime


class SwarmState(TypedDict):
    """State management for the swarm"""
    task: str
    messages: list[BaseMessage]
    agent_results: dict[str, Any]
    evaluation_results: dict[str, Any]
    short_term_memory: dict[str, Any]
    long_term_memory: dict[str, Any]
    status: str


class MemoryManager:
    """Manages short-term and long-term memory"""
    
    def __init__(self, memory_type: str = "chroma"):
        self.memory_type = memory_type
        self.short_term: dict = {}
        self.long_term: dict = {}
        self.memory_index: dict = {}
    
    def store_short_term(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store in short-term memory with optional TTL"""
        self.short_term[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "ttl": ttl
        }
    
    def retrieve_short_term(self, key: str) -> Optional[Any]:
        """Retrieve from short-term memory"""
        if key in self.short_term:
            data = self.short_term[key]
            # Check TTL
            if data.get("ttl"):
                # Implement TTL check if needed
                pass
            return data["value"]
        return None
    
    def store_long_term(self, key: str, value: Any, category: str = "general"):
        """Store in long-term memory with categorization"""
        if category not in self.long_term:
            self.long_term[category] = {}
        
        self.long_term[category][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update index
        if category not in self.memory_index:
            self.memory_index[category] = []
        self.memory_index[category].append(key)
    
    def retrieve_long_term(self, key: str, category: str = "general") -> Optional[Any]:
        """Retrieve from long-term memory"""
        if category in self.long_term and key in self.long_term[category]:
            return self.long_term[category][key]["value"]
        return None
    
    def search_memory(self, query: str, category: str = "general") -> list[tuple]:
        """Search long-term memory by key"""
        results = []
        if category in self.long_term:
            for key, data in self.long_term[category].items():
                if query.lower() in key.lower():
                    results.append((key, data["value"]))
        return results
    
    def clear_short_term(self):
        """Clear short-term memory"""
        self.short_term = {}
    
    def get_memory_stats(self) -> dict:
        """Get memory statistics"""
        return {
            "short_term_size": len(self.short_term),
            "long_term_categories": list(self.long_term.keys()),
            "long_term_total": sum(len(v) for v in self.long_term.values())
        }


class EvaluationEngine:
    """Evaluates agent outputs and task completion"""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        self.llm = llm
        self.evaluation_history: list = []
    
    def evaluate_output(self, output: str, criteria: dict) -> dict:
        """
        Evaluate agent output against criteria.
        
        Criteria example:
        {
            "relevance": "Is the output relevant to the task?",
            "completeness": "Does it address all aspects?",
            "accuracy": "Is the information accurate?"
        }
        """
        evaluation = {
            "output": output[:100] + "..." if len(output) > 100 else output,
            "criteria_scores": {},
            "overall_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Simple evaluation logic (can be enhanced with LLM)
        if criteria:
            total_score = 0
            for criterion, description in criteria.items():
                # Placeholder scoring logic
                score = len(output) / 1000.0  # Simple heuristic
                score = min(score, 1.0)
                evaluation["criteria_scores"][criterion] = score
                total_score += score
            
            evaluation["overall_score"] = total_score / len(criteria)
        
        self.evaluation_history.append(evaluation)
        return evaluation
    
    def batch_evaluate(self, outputs: list[str], criteria: dict) -> dict:
        """Evaluate multiple outputs"""
        results = {
            "evaluations": [],
            "average_score": 0.0
        }
        
        for output in outputs:
            eval_result = self.evaluate_output(output, criteria)
            results["evaluations"].append(eval_result)
        
        if results["evaluations"]:
            scores = [e["overall_score"] for e in results["evaluations"]]
            results["average_score"] = sum(scores) / len(scores)
        
        return results
    
    def get_evaluation_report(self) -> str:
        """Generate an evaluation report"""
        if not self.evaluation_history:
            return "No evaluations performed yet."
        
        avg_score = sum(e["overall_score"] for e in self.evaluation_history) / len(self.evaluation_history)
        return f"Evaluations: {len(self.evaluation_history)}, Average Score: {avg_score:.2f}"


class SwarmGraph:
    """LangGraph-based workflow for SwarmForge"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.memory = MemoryManager()
        self.evaluator = EvaluationEngine(llm)
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph_builder = StateGraph(SwarmState)
        
        # Define nodes
        graph_builder.add_node("process_input", self._process_input)
        graph_builder.add_node("agent_execution", self._agent_execution)
        graph_builder.add_node("evaluation", self._evaluation)
        graph_builder.add_node("memory_update", self._memory_update)
        graph_builder.add_node("aggregate_results", self._aggregate_results)
        
        # Define edges
        graph_builder.add_edge("process_input", "agent_execution")
        graph_builder.add_edge("agent_execution", "evaluation")
        graph_builder.add_edge("evaluation", "memory_update")
        graph_builder.add_edge("memory_update", "aggregate_results")
        graph_builder.add_edge("aggregate_results", END)
        
        # Set entry point
        graph_builder.set_entry_point("process_input")
        
        self.graph = graph_builder.compile()
    
    def _process_input(self, state: SwarmState) -> SwarmState:
        """Process and validate input"""
        state["messages"].append(HumanMessage(content=state["task"]))
        state["status"] = "input_processed"
        
        # Store in short-term memory
        self.memory.store_short_term("current_task", state["task"])
        
        return state
    
    def _agent_execution(self, state: SwarmState) -> SwarmState:
        """Execute agents (placeholder for agent orchestration)"""
        state["status"] = "agents_executed"
        state["agent_results"] = {
            "primary_agent": f"Processing: {state['task'][:50]}...",
            "timestamp": datetime.now().isoformat()
        }
        return state
    
    def _evaluation(self, state: SwarmState) -> SwarmState:
        """Evaluate agent results"""
        criteria = {
            "relevance": "Is it relevant?",
            "completeness": "Is it complete?"
        }
        
        output = state["agent_results"].get("primary_agent", "")
        eval_result = self.evaluator.evaluate_output(output, criteria)
        
        state["evaluation_results"] = eval_result
        state["status"] = "evaluated"
        
        return state
    
    def _memory_update(self, state: SwarmState) -> SwarmState:
        """Update memory with results"""
        self.memory.store_long_term(
            key=f"task_{len(self.memory.long_term.get('tasks', {}))}",
            value={
                "task": state["task"],
                "results": state["agent_results"],
                "evaluation": state["evaluation_results"]
            },
            category="tasks"
        )
        
        state["short_term_memory"] = self.memory.short_term.copy()
        state["long_term_memory"] = self.memory.long_term.copy()
        state["status"] = "memory_updated"
        
        return state
    
    def _aggregate_results(self, state: SwarmState) -> SwarmState:
        """Aggregate and finalize results"""
        state["status"] = "completed"
        state["messages"].append(
            AIMessage(content=f"Task completed: {state['task'][:50]}...")
        )
        return state
    
    def run(self, task: str) -> dict:
        """Execute the swarm workflow"""
        initial_state: SwarmState = {
            "task": task,
            "messages": [],
            "agent_results": {},
            "evaluation_results": {},
            "short_term_memory": {},
            "long_term_memory": {},
            "status": "initialized"
        }
        
        result = self.graph.invoke(initial_state)
        return result
    
    def get_memory_stats(self) -> dict:
        """Get current memory statistics"""
        return self.memory.get_memory_stats()
    
    def get_evaluation_report(self) -> str:
        """Get evaluation report"""
        return self.evaluator.get_evaluation_report()
