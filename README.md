# SwarmForge - Scalable Multi-Agent AI Framework

A production-ready framework for building scalable multi-agent AI systems with LLM coordination, parallel/sequential execution, tool integration, memory management, and output evaluation.

Web App Quick Start

- Run the embedded FastAPI web UI: `python webserver.py`
- Open the web UI in your browser at `http://127.0.0.1:8000`
- If your browser rejects `localhost:8000`, use `http://127.0.0.1:8000` (copy-paste the exact URL).

## 🚀 Features

- **Multi-Agent Orchestration**: Coordinate multiple specialized AI agents
- **Parallel & Sequential Execution**: Choose between execution modes for optimal performance
- **LangGraph Integration**: Built on LangChain's LangGraph for reliable workflows
- **Memory Management**: Dual-tier memory (short-term & long-term) with categorization
- **Tool Integration**: Web search, code execution, file operations, data analysis
- **Evaluation Engine**: Automatic output evaluation and quality scoring
- **Hierarchical Coordination**: Support for coordinator-worker patterns
- **Event Logging**: Comprehensive execution tracking and analytics

## 📋 Prerequisites

- Python 3.10+
- API Keys (at least one):
  - OpenAI API key (for GPT-4/3.5-turbo) OR
  - Groq API key (free tier available)
- Optional: Tavily API key for web search capabilities

## 🛠️ Installation

### 1. Clone and Setup
```bash
cd swarmforge
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY or GROQ_API_KEY
# Optional: TAVILY_API_KEY for web search
```

## 🏃 Quick Start

### Run the Interactive Demo
```bash
python main.py
```

This will launch an interactive menu where you can:
1. **Basic Workflow** - Test LangGraph with memory and evaluation
2. **Agent Pool** - See parallel/sequential agent execution
3. **Full Workflow** - End-to-end multi-agent orchestration
4. Exit

### Launch Web App from Desktop Shortcut (Windows)

**Option A: Create a shortcut manually**
1. Right-click on Desktop → New → Shortcut
2. Enter this location:
   ```
   powershell -Command "cd C:\Users\91900\OneDrive\Desktop\swarmforge; python webserver.py; pause"
   ```
   (Adjust the path if your folder is elsewhere)
3. Name it `SwarmForge Webapp`
4. Right-click the shortcut → Properties → Advanced → Check "Run as Administrator" (if needed)
5. Click the shortcut to launch the web server
6. Open Chrome and go to: `http://127.0.0.1:8000`

**Option B: Use the pre-built launcher**
```bash
# Windows PowerShell or Command Prompt
RUN_WEBAPP.bat
```
This runs the server in a dedicated terminal window.

**Option C: One-liner in PowerShell**
```powershell
cd "C:\Users\91900\OneDrive\Desktop\swarmforge"; python webserver.py
```

**Troubleshooting:**
- If you see "Please enter a valid URL" in Chrome, use `http://127.0.0.1:8000` instead of `localhost:8000`
- If port 8000 is already in use, kill the process: `Stop-Process -Name python -Force` then restart
- Check browser console (F12) if you get "link is not valid" at form submission — you likely need to add an API key to `.env`

### Example: Create Your Own Swarm

```python
from langchain_openai import ChatOpenAI
from agents import AgentConfig, AgentRole, ExecutionMode, SwarmOrchestrator
from graph import SwarmGraph

# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Create the swarm orchestrator
orchestrator = SwarmOrchestrator(llm)
pool = orchestrator.create_pool("my_team")

# Add agents
pool.add_agent(AgentConfig(
    name="researcher",
    role=AgentRole.RESEARCHER,
    tools=["web_search"]
))

pool.add_agent(AgentConfig(
    name="analyzer",
    role=AgentRole.ANALYZER,
    tools=["data_analysis"]
))

# Execute in parallel
pool.set_execution_mode(ExecutionMode.PARALLEL)
import asyncio
results = asyncio.run(pool.execute("Analyze AI trends"))
```

## 📁 Project Structure

```
swarmforge/
├── main.py              # Entry point and demos
├── agents.py            # Agent orchestration (sequential/parallel/hierarchical)
├── graph.py             # LangGraph workflows with memory & evaluation
├── tools.py             # Tool definitions (search, code exec, analysis)
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

## 🔧 Core Components

### Agents Module
- **Agent**: Individual AI agent with memory and execution logging
- **AgentPool**: Manages multiple agents with different execution modes
- **SwarmOrchestrator**: High-level orchestration across multiple pools

### Graph Module
- **SwarmGraph**: LangGraph-based workflow engine
- **MemoryManager**: Dual-tier memory with categorization
- **EvaluationEngine**: Output evaluation and scoring

### Tools Module
- **web_search**: Search the internet (requires Tavily API)
- **code_execution**: Execute Python/bash code safely
- **file_operations**: Read, write, and list files
- **data_analysis**: JSON parsing and statistics
- **memory_store**: Key-value memory operations

## 🎯 Use Cases

1. **Research Automation**: Parallel research from multiple agents + synthesis
2. **Content Analysis**: Multi-perspective analysis with evaluation
3. **Code Review**: Specialized agents analyzing different code aspects
4. **Data Processing**: Distributed data analysis and aggregation
5. **Customer Support**: Coordinated agents handling different support tiers

## 📊 Monitoring & Analytics

Get execution statistics:

```python
# Agent statistics
agent_stats = agent.get_execution_stats()
# Returns: executions, success rate, timing

# Pool statistics
pool_stats = pool.get_pool_stats()
# Returns: agent count, execution mode, per-agent stats

# Orchestration statistics
orchestration_stats = orchestrator.get_orchestration_stats()
# Returns: pool count, total executions, per-pool details
```

## 🚀 Advanced Features

### Execution Modes

- **SEQUENTIAL**: Agents execute one after another (safer, deterministic)
- **PARALLEL**: Agents execute simultaneously (faster, for independent tasks)
- **HIERARCHICAL**: Coordinator agent directs worker agents (complex workflows)

### Memory Tiers

- **Short-term**: Session-specific, auto-cleared, with TTL support
- **Long-term**: Persistent, categorized, searchable

### Evaluation Criteria

Define custom evaluation criteria:

```python
criteria = {
    "relevance": "Is it relevant to the task?",
    "completeness": "Does it cover all aspects?",
    "accuracy": "Is the information correct?"
}
evaluation = evaluator.evaluate_output(output, criteria)
```

## 🔌 Integration Patterns

### With LangChain
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Use SwarmForge agents within LangChain chains
chain = LLMChain(llm=llm, prompt=template)
```

### With External APIs
```python
# Tools can call any external API
@tool
def custom_api_call(query: str):
    response = requests.get(f"https://api.example.com/search?q={query}")
    return response.json()
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No LLM API key configured" | Set `OPENAI_API_KEY` or `GROQ_API_KEY` in `.env` |
| "Module not found" | Run `pip install -r requirements.txt` |
| Web search not working | Set `TAVILY_API_KEY` in `.env` |
| Rate limit errors | Add delay between requests, use Groq (free tier) |
| Memory issues | Clear short-term memory with `memory.clear_short_term()` |

## 📚 Learning Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Groq Console](https://console.groq.com/)

## 🤝 Contributing

Feel free to extend SwarmForge with:
- Additional tools and integrations
- Custom execution strategies
- Advanced memory backends (Redis, Pinecone, etc.)
- Web UI dashboard
- Distributed execution support

## 📄 License

MIT License - Free to use and modify

## 🎓 Next Steps

1. ✅ **Run the demo**: `python main.py`
2. 📚 **Read the code**: Review agents.py, graph.py, tools.py
3. 🔨 **Build your swarm**: Create custom agents and tools
4. 🚀 **Deploy**: Use Azure/AWS/GCP with Docker
5. 📖 **Document**: Add your use cases and patterns

---

**Made with ❤️ by the SwarmForge team. Happy swarming! 🐝**
