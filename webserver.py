"""
SwarmForge Web Server
FastAPI backend for the SwarmForge framework
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from agents import (
    Agent, AgentPool, SwarmOrchestrator, 
    AgentConfig, AgentRole, ExecutionMode
)
from graph import SwarmGraph
from tools import initialize_tools

# Load environment
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="SwarmForge",
    description="Scalable Multi-Agent AI Framework",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tools
initialize_tools(os.getenv("TAVILY_API_KEY"))

# Global state
class AppState:
    orchestrator: Optional[SwarmOrchestrator] = None
    graph: Optional[SwarmGraph] = None
    llm = None
    execution_history: List[Dict] = []
    current_task: Optional[str] = None
    task_status: str = "idle"

state = AppState()


# ============================================================================
# Models
# ============================================================================

class TaskRequest(BaseModel):
    """Request to execute a task"""
    task: str
    agent_count: int = 3
    execution_mode: str = "parallel"
    use_memory: bool = True


class AgentRequest(BaseModel):
    """Request to add an agent"""
    name: str
    role: str  # "researcher", "analyzer", "synthesizer", "executor", "coordinator"
    tools: Optional[List[str]] = None


class ExecutionResponse(BaseModel):
    """Response from task execution"""
    status: str
    task: str
    result: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str
    duration: float


class PoolStatsResponse(BaseModel):
    """Pool statistics"""
    total_agents: int
    execution_mode: str
    agents: Dict[str, Any]


# ============================================================================
# Favicon Handler
# ============================================================================

@app.get("/favicon.ico")
async def favicon():
    """Return a simple favicon (prevents 404 errors)"""
    return FileResponse(
        path="favicon.ico",
        media_type="image/x-icon",
        status_code=200
    ) if os.path.exists("favicon.ico") else {"status": "no favicon"}


# ============================================================================
# Initialization Endpoints
# ============================================================================

@app.post("/api/initialize")
async def initialize_swarm(config: Dict[str, Any]):
    """Initialize the swarm framework"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_groq import ChatGroq
        
        # Select LLM
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        if groq_key:
            try:
                llm = ChatGroq(
                    model="mixtral-8x7b-32768",
                    temperature=0.7,
                    groq_api_key=groq_key
                )
                llm_type = "Groq"
            except Exception as e:
                print(f"Groq initialization failed: {e}, trying OpenAI...")
                if openai_key:
                    llm = ChatOpenAI(
                        model="gpt-3.5-turbo",
                        temperature=0.7,
                        openai_api_key=openai_key
                    )
                    llm_type = "OpenAI"
                else:
                    raise ValueError("Groq failed and no OpenAI key available")
        elif openai_key:
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=openai_key
            )
            llm_type = "OpenAI"
        else:
            raise ValueError(
                "No LLM API key configured. Add GROQ_API_KEY or OPENAI_API_KEY to .env file"
            )
        
        state.llm = llm
        state.orchestrator = SwarmOrchestrator(llm)
        state.graph = SwarmGraph(llm)
        
        return {
            "status": "initialized",
            "llm": llm_type,
            "message": f"SwarmForge initialized successfully with {llm_type}"
        }
    except Exception as e:
        error_detail = str(e)
        print(f"Initialization error: {error_detail}")
        raise HTTPException(status_code=400, detail=error_detail)


@app.get("/api/status")
async def get_status():
    """Get current status"""
    return {
        "initialized": state.llm is not None,
        "current_task": state.current_task,
        "task_status": state.task_status,
        "execution_history_count": len(state.execution_history)
    }


# ============================================================================
# Agent Management Endpoints
# ============================================================================

@app.post("/api/agents/add")
async def add_agent(request: AgentRequest):
    """Add an agent to the pool"""
    try:
        if not state.orchestrator:
            raise ValueError("Swarm not initialized. Call /api/initialize first")
        
        # Get or create pool
        if not state.orchestrator.agent_pools:
            pool = state.orchestrator.create_pool("main")
        else:
            pool = list(state.orchestrator.agent_pools.values())[0]
        
        # Create agent config
        config = AgentConfig(
            name=request.name,
            role=AgentRole[request.role.upper()],
            tools=request.tools or []
        )
        
        pool.add_agent(config)
        
        return {
            "status": "added",
            "agent": request.name,
            "role": request.role
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/agents/list")
async def list_agents():
    """List all agents"""
    try:
        if not state.orchestrator or not state.orchestrator.agent_pools:
            return {"agents": []}
        
        pool = list(state.orchestrator.agent_pools.values())[0]
        agents = [
            {
                "name": agent.config.name,
                "role": agent.config.role.value,
                "tools": agent.config.tools or [],
                "state": agent.state,
                "executions": len(agent.execution_log)
            }
            for agent in pool.agents.values()
        ]
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/agents/stats")
async def get_agent_stats():
    """Get statistics for all agents"""
    try:
        if not state.orchestrator:
            return {"stats": {}}
        
        stats = state.orchestrator.get_orchestration_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Task Execution Endpoints
# ============================================================================

@app.post("/api/execute")
async def execute_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Execute a task using the swarm"""
    try:
        if not state.llm:
            raise ValueError("Swarm not initialized. Please click 'Initialize' first.")
        
        if not state.orchestrator:
            raise ValueError("Orchestrator not initialized. Please click 'Initialize' first.")
        
        state.current_task = request.task
        state.task_status = "running"
        start_time = datetime.now()
        
        # Create pool if needed
        try:
            if not state.orchestrator.agent_pools:
                pool = state.orchestrator.create_pool("main")
                
                # Add default agents if none exist
                for i in range(min(request.agent_count, 3)):
                    roles = [AgentRole.RESEARCHER, AgentRole.ANALYZER, AgentRole.SYNTHESIZER]
                    role = roles[i % len(roles)]
                    config = AgentConfig(
                        name=f"agent_{i}",
                        role=role,
                        max_iterations=3
                    )
                    pool.add_agent(config)
            else:
                pool = list(state.orchestrator.agent_pools.values())[0]
        except Exception as e:
            raise ValueError(f"Failed to create/get pool: {str(e)}")
        
        # Set execution mode
        try:
            mode = ExecutionMode[request.execution_mode.upper()]
            pool.set_execution_mode(mode)
        except KeyError:
            raise ValueError(f"Invalid execution mode: {request.execution_mode}")
        
        # Execute task
        try:
            result = await pool.execute(request.task)
        except Exception as e:
            raise ValueError(f"Task execution failed: {str(e)}")
        
        if request.use_memory:
            try:
                state.graph.run(request.task)
            except Exception as e:
                print(f"Memory save failed (non-critical): {e}")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Store in history
        execution_record = {
            "task": request.task,
            "status": "completed",
            "result": result,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "agent_count": request.agent_count,
            "execution_mode": request.execution_mode
        }
        state.execution_history.append(execution_record)
        
        state.task_status = "completed"
        
        return ExecutionResponse(
            status="success",
            task=request.task,
            result=result,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )
    
    except Exception as e:
        state.task_status = "error"
        error_msg = str(e)
        print(f"Execute error: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)


@app.get("/api/execute/history")
async def get_execution_history(limit: int = 10):
    """Get execution history"""
    return {
        "history": state.execution_history[-limit:],
        "total": len(state.execution_history)
    }


# ============================================================================
# Memory and Evaluation Endpoints
# ============================================================================

@app.get("/api/memory/stats")
async def get_memory_stats():
    """Get memory statistics"""
    try:
        if not state.graph:
            return {"memory": {}}
        
        stats = state.graph.get_memory_stats()
        return {"memory": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/memory/search")
async def search_memory(query: str, category: str = "general"):
    """Search memory"""
    try:
        if not state.graph:
            return {"results": []}
        
        results = state.graph.memory.search_memory(query, category)
        return {
            "query": query,
            "results": [{"key": k, "value": v} for k, v in results]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/evaluation/report")
async def get_evaluation_report():
    """Get evaluation report"""
    try:
        if not state.graph:
            return {"report": ""}
        
        report = state.graph.get_evaluation_report()
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Web UI Endpoints
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the web UI"""
    return get_html()


@app.get("/app", response_class=HTMLResponse)
async def get_app():
    """Serve the web app"""
    return get_html()


def get_html():
    """Get the HTML for the web UI"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SwarmForge - Multi-Agent AI Framework</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        h1 {
            font-size: 32px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            color: #666;
            font-size: 14px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 1200px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
        
        .panel {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .panel h2 {
            font-size: 20px;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #555;
            font-size: 14px;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: inherit;
            font-size: 14px;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        button {
            flex: 1;
            padding: 12px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-size: 14px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .button-secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .button-secondary:hover {
            background: #e0e0e0;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .status {
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            margin: 10px 0;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .status.warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .agent-item {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 12px;
            margin: 8px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .agent-info {
            flex: 1;
        }
        
        .agent-name {
            font-weight: 500;
            color: #333;
        }
        
        .agent-role {
            font-size: 12px;
            color: #666;
            margin-top: 3px;
        }
        
        .agent-state {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            background: #667eea;
            color: white;
        }
        
        .output {
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-top: 10px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            vertical-align: middle;
            margin-right: 8px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        
        .stat-item {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            font-weight: 500;
        }
        
        .stat-value {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-top: 3px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            border-bottom: 1px solid #ddd;
        }
        
        .tab-button {
            padding: 10px 15px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-weight: 500;
            color: #666;
            transition: all 0.3s;
            flex: none;
        }
        
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐝 SwarmForge</h1>
            <p class="subtitle">Scalable Multi-Agent AI Framework with LLM Coordination</p>
        </header>
        
        <div class="grid">
            <!-- Control Panel -->
            <div class="panel">
                <h2>🎮 Control Panel</h2>
                
                <div class="form-group">
                    <label>Initialize Swarm</label>
                    <button onclick="initializeSwarm()">Initialize</button>
                    <div id="initStatus"></div>
                </div>
                
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
                
                <div class="form-group">
                    <label for="agentName">Agent Name</label>
                    <input type="text" id="agentName" placeholder="e.g., researcher_1">
                </div>
                
                <div class="form-group">
                    <label for="agentRole">Agent Role</label>
                    <select id="agentRole">
                        <option value="researcher">Researcher</option>
                        <option value="analyzer">Analyzer</option>
                        <option value="synthesizer">Synthesizer</option>
                        <option value="executor">Executor</option>
                        <option value="coordinator">Coordinator</option>
                    </select>
                </div>
                
                <div class="button-group">
                    <button onclick="addAgent()">Add Agent</button>
                    <button class="button-secondary" onclick="listAgents()">List Agents</button>
                </div>
                <div id="agentStatus"></div>
            </div>
            
            <!-- Task Execution -->
            <div class="panel">
                <h2>⚡ Task Execution</h2>
                
                <div class="form-group">
                    <label for="task">Task Description</label>
                    <textarea id="task" placeholder="Enter your task here..."></textarea>
                </div>
                
                <div class="form-group">
                    <label for="agentCount">Number of Agents</label>
                    <input type="number" id="agentCount" value="3" min="1" max="10">
                </div>
                
                <div class="form-group">
                    <label for="execMode">Execution Mode</label>
                    <select id="execMode">
                        <option value="parallel">Parallel (Fast)</option>
                        <option value="sequential">Sequential (Safe)</option>
                        <option value="hierarchical">Hierarchical (Coordinated)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="useMemory" checked> Use Memory Management
                    </label>
                </div>
                
                <button onclick="executeTask()">Execute Task</button>
                <div id="taskStatus"></div>
            </div>
        </div>
        
        <!-- Agents Panel -->
        <div class="panel">
            <h2>👥 Agents</h2>
            <div id="agentsList">
                <p style="color: #999;">No agents added yet. Add one above to get started.</p>
            </div>
            <div id="agentsStats"></div>
        </div>
        
        <!-- Results Panel -->
        <div class="panel">
            <h2>📊 Results & History</h2>
            
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab('results')">Current Result</button>
                <button class="tab-button" onclick="switchTab('history')">Execution History</button>
                <button class="tab-button" onclick="switchTab('memory')">Memory</button>
                <button class="tab-button" onclick="switchTab('evaluation')">Evaluation</button>
            </div>
            
            <div id="results" class="tab-content active">
                <div id="resultOutput">Waiting for execution...</div>
            </div>
            
            <div id="history" class="tab-content">
                <div id="historyOutput"></div>
            </div>
            
            <div id="memory" class="tab-content">
                <input type="text" id="memoryQuery" placeholder="Search memory..." style="margin-bottom: 10px;">
                <button onclick="searchMemory()">Search</button>
                <div id="memoryOutput" style="margin-top: 10px;"></div>
            </div>
            
            <div id="evaluation" class="tab-content">
                <button onclick="getEvaluationReport()">Get Evaluation Report</button>
                <div id="evaluationOutput" style="margin-top: 10px;"></div>
            </div>
        </div>
    </div>
    
    <script>
        const API_URL = '/api';
        
        async function initializeSwarm() {
            try {
                const response = await fetch(`${API_URL}/initialize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                
                let data;
                try {
                    data = await response.json();
                } catch (parseError) {
                    throw new Error(`Invalid response from server: ${response.status}`);
                }
                
                if (!response.ok) {
                    const errorMsg = data.detail || data.message || 'Unknown error';
                    showStatus('initStatus', `✗ Error: ${errorMsg}`, 'error');
                    console.error('API Error:', data);
                    return;
                }
                
                showStatus('initStatus', `✓ Initialized with ${data.llm}`, 'success');
                loadAgents();
            } catch (e) {
                console.error('Init error:', e);
                showStatus('initStatus', `✗ Error: ${e.message}`, 'error');
            }
        }
        
        async function addAgent() {
            const name = document.getElementById('agentName').value;
            const role = document.getElementById('agentRole').value;
            
            if (!name) {
                showStatus('agentStatus', 'Please enter agent name', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_URL}/agents/add`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, role, tools: [] })
                });
                const data = await response.json();
                showStatus('agentStatus', `✓ Agent "${name}" added as ${role}`, 'success');
                document.getElementById('agentName').value = '';
                loadAgents();
            } catch (e) {
                showStatus('agentStatus', `✗ Error: ${e.message}`, 'error');
            }
        }
        
        async function listAgents() {
            loadAgents();
        }
        
        async function loadAgents() {
            try {
                const response = await fetch(`${API_URL}/agents/list`);
                const data = await response.json();
                
                const agentsList = document.getElementById('agentsList');
                if (data.agents.length === 0) {
                    agentsList.innerHTML = '<p style="color: #999;">No agents added yet.</p>';
                } else {
                    agentsList.innerHTML = data.agents.map(agent => `
                        <div class="agent-item">
                            <div class="agent-info">
                                <div class="agent-name">${agent.name}</div>
                                <div class="agent-role">Role: ${agent.role} | Executions: ${agent.executions}</div>
                            </div>
                            <div class="agent-state">${agent.state}</div>
                        </div>
                    `).join('');
                }
                
                const statsResponse = await fetch(`${API_URL}/agents/stats`);
                const statsData = await statsResponse.json();
                
                if (statsData.total_pools > 0) {
                    const pool = Object.values(statsData.pools)[0];
                    document.getElementById('agentsStats').innerHTML = `
                        <div class="stats">
                            <div class="stat-item">
                                <div class="stat-label">Total Agents</div>
                                <div class="stat-value">${pool.total_agents}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Execution Mode</div>
                                <div class="stat-value">${pool.execution_mode}</div>
                            </div>
                        </div>
                    `;
                }
            } catch (e) {
                console.error('Error loading agents:', e);
            }
        }
        
        async function executeTask() {
            const task = document.getElementById('task').value;
            const agentCount = parseInt(document.getElementById('agentCount').value);
            const execMode = document.getElementById('execMode').value;
            const useMemory = document.getElementById('useMemory').checked;
            
            if (!task) {
                showStatus('taskStatus', 'Please enter a task', 'error');
                return;
            }
            
            const taskStatus = document.getElementById('taskStatus');
            taskStatus.innerHTML = '<div class="status info"><span class="loading"></span>Executing task...</div>';
            
            try {
                const response = await fetch(`${API_URL}/execute`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        task,
                        agent_count: agentCount,
                        execution_mode: execMode,
                        use_memory: useMemory
                    })
                });
                
                let data;
                try {
                    data = await response.json();
                } catch (parseError) {
                    throw new Error(`Invalid response from server: ${response.status}`);
                }
                
                if (!response.ok) {
                    const errorMsg = data.detail || data.message || 'Unknown error';
                    showStatus('taskStatus', `✗ Error: ${errorMsg}`, 'error');
                    console.error('API Error:', data);
                    return;
                }
                
                showStatus('taskStatus', `✓ Task completed in ${data.duration.toFixed(2)}s`, 'success');
                
                const result = document.getElementById('resultOutput');
                result.innerHTML = `
                    <div>
                        <strong>Status:</strong> ${data.status}<br>
                        <strong>Duration:</strong> ${data.duration.toFixed(2)}s<br>
                        <strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}<br>
                        <strong>Result:</strong><br>
                        <div class="output">${JSON.stringify(data.result, null, 2)}</div>
                    </div>
                `;
                
                loadHistory();
                loadAgents();
            } catch (e) {
                console.error('Execute error:', e);
                showStatus('taskStatus', `✗ Error: ${e.message}`, 'error');
            }
        }
        }
        
        async function loadHistory() {
            try {
                const response = await fetch(`${API_URL}/execute/history?limit=5`);
                const data = await response.json();
                
                const history = document.getElementById('historyOutput');
                if (data.history.length === 0) {
                    history.innerHTML = '<p style="color: #999;">No execution history yet.</p>';
                } else {
                    history.innerHTML = data.history.map(item => `
                        <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; margin: 8px 0;">
                            <strong>${item.task.substring(0, 50)}...</strong><br>
                            <small>Mode: ${item.execution_mode} | Agents: ${item.agent_count} | Duration: ${item.duration.toFixed(2)}s</small><br>
                            <small style="color: #999;">${new Date(item.timestamp).toLocaleString()}</small>
                        </div>
                    `).join('');
                }
            } catch (e) {
                console.error('Error loading history:', e);
            }
        }
        
        async function searchMemory() {
            const query = document.getElementById('memoryQuery').value;
            if (!query) {
                showStatus('memoryOutput', 'Enter a search query', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_URL}/memory/search?query=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                const output = document.getElementById('memoryOutput');
                if (data.results.length === 0) {
                    output.innerHTML = '<div class="status info">No results found</div>';
                } else {
                    output.innerHTML = data.results.map(r => `
                        <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; margin: 8px 0;">
                            <strong>${r.key}</strong><br>
                            <div class="output">${JSON.stringify(r.value, null, 2)}</div>
                        </div>
                    `).join('');
                }
            } catch (e) {
                showStatus('memoryOutput', `Error: ${e.message}`, 'error');
            }
        }
        
        async function getEvaluationReport() {
            try {
                const response = await fetch(`${API_URL}/evaluation/report`);
                const data = await response.json();
                
                document.getElementById('evaluationOutput').innerHTML = `
                    <div class="output">${data.report}</div>
                `;
            } catch (e) {
                showStatus('evaluationOutput', `Error: ${e.message}`, 'error');
            }
        }
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function showStatus(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
        
        // Load initial data
        window.addEventListener('load', () => {
            loadAgents();
            loadHistory();
        });
    </script>
</body>
</html>
"""


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import sys
    
    print("""
    ================================================
             SwarmForge Web Server Started            
    ================================================
    
    Open your browser and go to:
       http://localhost:8000
    
    API Documentation:
       http://localhost:8000/docs
    
    Press Ctrl+C to stop the server
    """)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
