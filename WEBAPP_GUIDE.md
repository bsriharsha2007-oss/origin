# 🐝 SwarmForge Web Application Guide

## Quick Start

### Option 1: Command Prompt (Windows)
```batch
start_webapp.cmd
```

### Option 2: PowerShell (Windows)
```powershell
.\start_webapp.ps1
```

### Option 3: Manual
```bash
python webserver.py
```

## Access the Web App

Once the server starts, open your browser to:

- **Main Web App**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/openapi.json

## Features

### 🎮 Control Panel
- **Initialize Swarm**: Set up the framework with your LLM (OpenAI or Groq)
- **Add Agents**: Create agents with specific roles:
  - Researcher: Gathers information
  - Analyzer: Analyzes data and findings
  - Synthesizer: Combines results
  - Executor: Takes action
  - Coordinator: Manages orchestration

### ⚡ Task Execution
- **Task Description**: Enter any task you want the swarm to handle
- **Agent Count**: Choose 1-10 agents for the task
- **Execution Mode**:
  - **Parallel**: All agents work simultaneously (fast, concurrent)
  - **Sequential**: Agents work one after another (safe, ordered)
  - **Hierarchical**: Coordinator directs execution (structured)
- **Memory Management**: Enable/disable persistent memory

### 👥 Agent Management
- View all active agents
- See agent roles and execution statistics
- Monitor agent states in real-time

### 📊 Results Dashboard
- **Current Result**: View the latest task execution result
- **Execution History**: See up to 10 previous tasks
- **Memory Tab**: Search stored memory from past executions
- **Evaluation Tab**: View AI-generated evaluation reports

## API Endpoints

### Initialization
```
POST /api/initialize
- Initialize the swarm framework
```

### Agent Management
```
POST /api/agents/add
- Add a new agent to the pool

GET /api/agents/list
- List all active agents

GET /api/agents/stats
- Get statistics about agents and pools
```

### Task Execution
```
POST /api/execute
- Execute a task using the swarm
- Body: {
    "task": "string",
    "agent_count": integer,
    "execution_mode": "parallel|sequential|hierarchical",
    "use_memory": boolean
  }

GET /api/execute/history?limit=10
- Get execution history
```

### Memory & Evaluation
```
GET /api/memory/stats
- Get memory statistics

GET /api/memory/search?query=string&category=general
- Search memory for specific information

GET /api/evaluation/report
- Get evaluation report of recent executions
```

### Health
```
GET /health
- Health check endpoint
```

## Environment Setup

The web app uses your existing `.env` file for configuration:

```env
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

If you don't have a `.env` file, copy from `.env.example`:
```bash
copy .env.example .env
```

Then add your API keys.

## Troubleshooting

### Port 8000 Already in Use
If port 8000 is busy, modify `webserver.py`:
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8001,  # Change this number
    log_level="info"
)
```

### Missing Dependencies
Reinstall requirements:
```bash
pip install -r requirements.txt --force-reinstall
```

### API Key Issues
- Ensure your `.env` file exists and has valid API keys
- The web app will work with Groq API (free tier available)
- OpenAI is optional for more powerful models

### Memory Issues with Large Tasks
- Reduce the task scope
- Decrease agent count
- Use sequential execution mode for better memory management

## Advanced Usage

### Custom Agent Configuration
Edit `webserver.py` line 170-180 to customize default agent creation:

```python
config = AgentConfig(
    name=request.name,
    role=AgentRole[request.role.upper()],
    tools=request.tools or [],
    max_iterations=3,  # Adjust iteration count
    timeout=30  # Timeout in seconds
)
```

### Adding New Tools
Modify `tools.py` and add your tools, then reference them in agent creation:

```python
tools=["web_search", "code_execution", "custom_tool"]
```

### Persistent Data
Memory is stored in-memory during execution. For persistence:
1. Implement database backend in `MemoryManager`
2. Add `/api/memory/save` endpoint
3. Load memory on app startup

## Performance Tips

1. **For Fast Execution**: Use Parallel mode with 3-5 agents
2. **For Accuracy**: Use Sequential mode with detailed agents
3. **For Complex Tasks**: Use Hierarchical mode with Coordinator
4. **Memory Search**: Search is fast but index large queries

## Browser Compatibility

- Chrome/Chromium: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Edge: ✅ Full support
- Mobile browsers: ⚠️ Responsive but optimized for desktop

## Security Notes

- The web app runs on localhost by default
- Change `host="0.0.0.0"` in `webserver.py` only if you trust your network
- API keys are stored in `.env` - keep this file private
- CORS is enabled for development - restrict in production

## Next Steps

1. Initialize the swarm with your preferred LLM
2. Add 3-5 agents with different roles
3. Try a simple task first (e.g., "List the planets")
4. Progress to complex multi-step tasks
5. Explore different execution modes and agent configurations

---

For more information, see README.md and PROJECT_SUMMARY.txt
