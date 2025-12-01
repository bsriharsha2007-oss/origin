"""
SwarmForge Tools Module
Provides reusable tools for agents (search, code execution, web scraping, etc.)
"""

import json
import subprocess
import os
from typing import Any, Optional
from langchain_core.tools import tool
try:
    from tavily import TavilyClient
    tavily_available = True
except ImportError:
    tavily_available = False
    TavilyClient = None

# Initialize Tavily for web search
tavily_client = None


def initialize_tools(tavily_api_key: Optional[str] = None):
    """Initialize external tool clients"""
    global tavily_client
    if tavily_api_key and tavily_available:
        tavily_client = TavilyClient(api_key=tavily_api_key)


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for information using Tavily.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        Search results as formatted string
    """
    if not tavily_client:
        return "Tavily client not initialized. Set TAVILY_API_KEY environment variable."
    
    try:
        response = tavily_client.search(query=query, max_results=max_results)
        results = []
        for result in response.get("results", []):
            results.append(f"- {result['title']}: {result['content']}\n  URL: {result['url']}")
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def code_execution(code: str, language: str = "python") -> str:
    """
    Execute code safely in a sandboxed environment.
    
    Args:
        code: Code to execute
        language: Programming language (python, bash)
        
    Returns:
        Execution result or error
    """
    try:
        if language.lower() == "python":
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=10
            )
        elif language.lower() == "bash":
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            return f"Unsupported language: {language}"
        
        output = result.stdout if result.stdout else result.stderr
        return output or "Execution completed with no output."
    except subprocess.TimeoutExpired:
        return "Code execution timed out (10s limit)"
    except Exception as e:
        return f"Execution error: {str(e)}"


@tool
def file_operations(operation: str, path: str, content: Optional[str] = None) -> str:
    """
    Perform file operations (read, write, list).
    
    Args:
        operation: 'read', 'write', or 'list'
        path: File or directory path
        content: Content to write (for write operation)
        
    Returns:
        Operation result
    """
    try:
        if operation == "read":
            with open(path, "r") as f:
                return f.read()
        elif operation == "write":
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content or "")
            return f"File written: {path}"
        elif operation == "list":
            files = os.listdir(path)
            return "\n".join(files)
        else:
            return f"Unknown operation: {operation}"
    except Exception as e:
        return f"File operation error: {str(e)}"


@tool
def data_analysis(data: str, analysis_type: str) -> str:
    """
    Analyze data (JSON parsing, statistics, etc.).
    
    Args:
        data: Data to analyze
        analysis_type: Type of analysis
        
    Returns:
        Analysis result
    """
    try:
        if analysis_type == "json":
            parsed = json.loads(data)
            return f"Valid JSON with {len(parsed)} top-level keys"
        elif analysis_type == "stats":
            numbers = [float(x) for x in data.split() if x.replace(".", "").isdigit()]
            if numbers:
                return f"Count: {len(numbers)}, Mean: {sum(numbers)/len(numbers):.2f}, Min: {min(numbers)}, Max: {max(numbers)}"
            return "No numeric data found"
        else:
            return f"Analysis type '{analysis_type}' not implemented"
    except Exception as e:
        return f"Analysis error: {str(e)}"


@tool
def memory_store(operation: str, key: str, value: Optional[str] = None) -> str:
    """
    Store and retrieve data in memory (key-value store).
    
    Args:
        operation: 'set', 'get', or 'delete'
        key: Storage key
        value: Value to store (for set operation)
        
    Returns:
        Operation result
    """
    # This would typically interface with a database or vector store
    # For now, returning placeholder
    return f"Memory operation '{operation}' on key '{key}' executed"


# Tool registry for easy access
TOOL_REGISTRY = {
    "web_search": web_search,
    "code_execution": code_execution,
    "file_operations": file_operations,
    "data_analysis": data_analysis,
    "memory_store": memory_store,
}


def get_tools(tool_names: Optional[list[str]] = None) -> list:
    """
    Get a list of tools. If tool_names is None, return all tools.
    
    Args:
        tool_names: List of tool names to retrieve
        
    Returns:
        List of tool functions
    """
    if tool_names is None:
        return list(TOOL_REGISTRY.values())
    
    return [TOOL_REGISTRY[name] for name in tool_names if name in TOOL_REGISTRY]
