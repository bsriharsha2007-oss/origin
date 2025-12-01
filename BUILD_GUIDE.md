"""
SwarmForge Build Guide
Complete step-by-step instructions to build and run locally
"""

# ============================================================
# HOW TO BUILD SWARMFORGE: STEP-BY-STEP GUIDE
# ============================================================

"""
⏱️  Estimated Time: 30-60 minutes

This guide walks you through building SwarmForge locally on your machine.
You'll have a working multi-agent AI framework ready to extend.

PART 1: PREREQUISITES & SETUP (5 minutes)
========================================================

1. Python Installation
   - Ensure you have Python 3.10+ installed
   - Check: python --version
   - Download from python.org if needed

2. Get API Keys (Choose at least one)
   
   Option A: OpenAI (GPT-4 / GPT-3.5-turbo)
   - Go to: https://platform.openai.com/api-keys
   - Create new secret key
   - Copy to safe location
   
   Option B: Groq (Free tier, fast inference)
   - Go to: https://console.groq.com/keys
   - Create API key
   - Much faster, no cost (beta)
   - Recommended for testing!
   
   Option C (Optional): Tavily API for web search
   - Go to: https://tavily.com
   - Sign up for API key
   - Enables web search tool

3. Clone/Navigate to SwarmForge folder
   - Already done! You have: agents.py, graph.py, tools.py, requirements.txt


PART 2: ENVIRONMENT SETUP (10 minutes)
========================================================

Step 1: Create Virtual Environment
   
   On Windows (cmd):
   ───────────────────
   python -m venv venv
   venv\Scripts\activate
   
   On macOS/Linux (bash):
   ────────────────────
   python3 -m venv venv
   source venv/bin/activate
   
   ✓ You should see (venv) in your terminal prompt

Step 2: Install Dependencies
   
   pip install -r requirements.txt
   
   This installs:
   - langgraph: LangChain graph orchestration
   - langchain: LLM framework
   - langchain-openai: OpenAI integration
   - langchain-groq: Groq integration
   - tavily-python: Web search API
   - chromadb: Vector memory database
   - Other utilities

Step 3: Configure Environment Variables
   
   1. Copy the template:
      cp .env.example .env
      
   2. Edit .env file with your favorite editor:
      - Set OPENAI_API_KEY or GROQ_API_KEY
      - Optionally set TAVILY_API_KEY
      
      Example .env:
      ──────────────────────────────────
      OPENAI_API_KEY=sk-... (your key)
      TAVILY_API_KEY=tvly-... (optional)
      DEBUG=false
      ──────────────────────────────────

Step 4: Verify Installation
   
   python -c "from langchain_openai import ChatOpenAI; print('✓ Setup OK')"
   
   Should print: ✓ Setup OK


PART 3: UNDERSTANDING THE ARCHITECTURE (10 minutes)
========================================================

SwarmForge has 3 core modules:

1. AGENTS.PY - Multi-Agent Orchestration
   ───────────────────────────────────────
   Key Classes:
   - Agent: Individual AI agent with memory and logging
   - AgentPool: Manages multiple agents
   - SwarmOrchestrator: High-level coordination
   
   Execution Modes:
   - SEQUENTIAL: One agent after another (safe)
   - PARALLEL: All agents at same time (fast)
   - HIERARCHICAL: Coordinator + workers (structured)
   
   Example:
   ────────
   pool = AgentPool(llm)
   pool.add_agent(AgentConfig(name="researcher", role=AgentRole.RESEARCHER))
   pool.set_execution_mode(ExecutionMode.PARALLEL)
   results = await pool.execute("search for AI trends")

2. GRAPH.PY - LangGraph Workflow Engine
   ──────────────────────────────────────
   Key Classes:
   - SwarmGraph: LangGraph-based workflow
   - MemoryManager: Short-term + long-term memory
   - EvaluationEngine: Output quality scoring
   
   Workflow Nodes:
   1. process_input: Validate and store task
   2. agent_execution: Run agents
   3. evaluation: Score results
   4. memory_update: Store in memory
   5. aggregate_results: Finalize output
   
   Example:
   ────────
   graph = SwarmGraph(llm)
   result = graph.run("Analyze AI trends")
   # Returns: messages, results, evaluation, memory

3. TOOLS.PY - Tool Definitions
   ────────────────────────────
   Available Tools:
   - web_search(query): Search the internet
   - code_execution(code): Run Python/bash code
   - file_operations(op, path): Read/write files
   - data_analysis(data, type): JSON/stats analysis
   - memory_store(op, key, value): Key-value storage
   
   Example:
   ────────
   results = web_search("latest AI breakthroughs")
   output = code_execution("print(2**10)")


PART 4: RUN THE INTERACTIVE DEMO (10 minutes)
========================================================

Step 1: Start the Demo
   
   python main.py
   
   You'll see a menu:
   ───────────────────
   1. Basic Workflow (LangGraph, Memory, Evaluation)
   2. Agent Pool Demo (Parallel/Sequential Execution)
   3. Full End-to-End Workflow
   4. Exit

Step 2: Run Each Demo
   
   Try option 1 first:
   - This tests LangGraph with memory management
   - Shows evaluation scoring
   - Takes ~10 seconds
   
   Then option 2:
   - Creates 3 specialized agents
   - Runs them in parallel and sequential
   - Shows execution statistics
   - Takes ~15 seconds
   
   Finally option 3:
   - Full multi-agent research workflow
   - Demonstrates orchestration
   - Memory and evaluation in action


PART 5: BUILD YOUR OWN SWARM (20 minutes)
========================================================

Example 1: Content Analysis Team
──────────────────────────────────

from langchain_openai import ChatOpenAI
from agents import AgentConfig, AgentRole, ExecutionMode, SwarmOrchestrator
import asyncio

# Setup
llm = ChatOpenAI(model="gpt-3.5-turbo")
orchestrator = SwarmOrchestrator(llm)

# Create team
team = orchestrator.create_pool("analysis_team")
team.add_agent(AgentConfig(
    name="summarizer",
    role=AgentRole.ANALYZER,
    tools=["data_analysis"]
))
team.add_agent(AgentConfig(
    name="critic",
    role=AgentRole.ANALYZER,
    tools=["code_execution"]
))

# Execute
team.set_execution_mode(ExecutionMode.PARALLEL)
results = asyncio.run(team.execute("Analyze the article about quantum computing"))

# Get stats
stats = orchestrator.get_orchestration_stats()
print(stats)


Example 2: Research Workflow with Memory
─────────────────────────────────────────

from graph import SwarmGraph

graph = SwarmGraph(llm)

# Run task
result = graph.run("Research AI safety concerns")

# Check memory
memory_stats = graph.get_memory_stats()
print(f"Stored {memory_stats['long_term_total']} findings in long-term memory")

# Retrieve findings
findings = graph.memory.retrieve_long_term("task_0", category="tasks")
print(findings)


PART 6: TESTING YOUR BUILD (5 minutes)
========================================================

Run the test suite:

pytest tests.py -v

Expected output:
────────────────
test_short_term_storage PASSED
test_long_term_storage PASSED
test_evaluate_output PASSED
test_sequential_execution PASSED
test_parallel_execution PASSED
... more tests ...

All tests should pass ✓


PART 7: COMMON ERRORS & SOLUTIONS
========================================================

Error 1: "ModuleNotFoundError: No module named 'langchain'"
──────────────────────────────────────────────────────────
Cause: Dependencies not installed
Fix:
   pip install -r requirements.txt

Error 2: "No LLM API key configured"
───────────────────────────────────
Cause: Missing OPENAI_API_KEY or GROQ_API_KEY
Fix:
   1. Set environment variable:
      - Windows: set OPENAI_API_KEY=sk-...
      - Or edit .env file
   2. Restart Python/terminal

Error 3: "Web search not working"
────────────────────────────────
Cause: TAVILY_API_KEY not set (optional feature)
Fix:
   - This is optional. Set TAVILY_API_KEY to enable
   - Framework works without it

Error 4: "Rate limit exceeded"
──────────────────────────────
Cause: Too many API calls
Fix:
   - Use Groq (free tier, rate limits are generous)
   - Add delays between requests
   - Or upgrade OpenAI plan


PART 8: NEXT STEPS - EXTEND & DEPLOY
========================================================

Now that you have a working SwarmForge, here's what to do:

1. ✅ Extend Tools
   - Add custom tools in tools.py
   - Example: database queries, slack messages, etc.
   
2. ✅ Create Specialized Agents
   - Define custom agent roles
   - Implement domain-specific logic
   
3. ✅ Custom Workflows
   - Design LangGraph workflows for your use case
   - Add conditional logic and branching
   
4. ✅ Add Persistence
   - Store results in database
   - Use ChromaDB for vector memory
   - Implement backup/recovery
   
5. ✅ Build API/UI
   - Create FastAPI endpoint for your swarm
   - Build simple web dashboard
   - Add real-time monitoring
   
6. ✅ Deploy to Cloud
   - Azure App Service or Container Apps
   - AWS Lambda or ECS
   - Google Cloud Run
   - Follow deployment guide in docs/


DEPLOYMENT CHECKLIST
═════════════════════════════════════════════════════════

Local Running: ✅ COMPLETE
- [x] Environment setup
- [x] Dependencies installed
- [x] Demo runs successfully
- [x] Tests pass

Ready for Production?
- [ ] Add database for persistence
- [ ] Implement error handling/retries
- [ ] Add authentication
- [ ] Set up monitoring/logging
- [ ] Create Docker image
- [ ] Configure CI/CD pipeline
- [ ] Deploy to cloud


QUICK REFERENCE COMMANDS
═════════════════════════════════════════════════════════

# Setup
python -m venv venv
venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python main.py

# Test
pytest tests.py -v

# Check syntax
python -m py_compile agents.py graph.py tools.py

# Run specific demo
python -c "from main import demo_basic_workflow; demo_basic_workflow()"


SUMMARY
═════════════════════════════════════════════════════════

🎉 You now have a fully functional SwarmForge!

What you've built:
✓ Multi-agent orchestration framework
✓ LangGraph-based workflow engine
✓ Memory management (short & long-term)
✓ Output evaluation system
✓ Tool integration
✓ Parallel/sequential/hierarchical execution

What you can do:
✓ Build research teams
✓ Coordinate specialized agents
✓ Chain complex workflows
✓ Evaluate and store results
✓ Monitor and analyze performance

What's next:
→ Customize agents for your domain
→ Add domain-specific tools
→ Build API endpoints
→ Deploy to cloud
→ Build UI dashboard


Questions? Check:
- README.md - Framework overview
- main.py - Example usage
- agents.py - Agent orchestration
- graph.py - Workflow engine
- tools.py - Available tools


Made with ❤️ by the SwarmForge team
Happy swarming! 🐝

═════════════════════════════════════════════════════════
"""

# To view this guide in a text editor:
# Open this file (BUILD_GUIDE.md) in your editor
# Or run: python -c "print(__doc__)"

if __name__ == "__main__":
    print(__doc__)
