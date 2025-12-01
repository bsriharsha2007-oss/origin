"""
SwarmForge Main Application
Example usage and entry point for the multi-agent framework
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from agents import AgentConfig, AgentRole, ExecutionMode, SwarmOrchestrator
from graph import SwarmGraph
from tools import initialize_tools, get_tools


def setup_environment():
    """Load and validate environment variables"""
    load_dotenv()
    
    # Check for required API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not (openai_key or groq_key):
        print("⚠️  Warning: No LLM API key found. Set OPENAI_API_KEY or GROQ_API_KEY")
    
    if not tavily_key:
        print("⚠️  Warning: No Tavily API key found. Web search disabled. Set TAVILY_API_KEY")
    else:
        initialize_tools(tavily_key)
    
    return {
        "openai_key": openai_key,
        "groq_key": groq_key,
        "tavily_key": tavily_key
    }


def get_llm():
    """Get the appropriate LLM based on available API keys"""
    if os.getenv("GROQ_API_KEY"):
        print("Using Groq LLM (faster, free tier available)")
        return ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0.7,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
    elif os.getenv("OPENAI_API_KEY"):
        print("Using OpenAI LLM (GPT-4/3.5-turbo)")
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    else:
        raise ValueError("No LLM API key configured. Please set OPENAI_API_KEY or GROQ_API_KEY")


def demo_basic_workflow():
    """Demonstrate basic SwarmForge workflow"""
    print("\n" + "="*60)
    print("🤖 SwarmForge - Basic Workflow Demo")
    print("="*60)
    
    # Setup
    env_vars = setup_environment()
    llm = get_llm()
    
    # Create the swarm graph
    print("\n1️⃣  Initializing SwarmGraph...")
    graph = SwarmGraph(llm)
    print(f"   ✓ Graph initialized with memory and evaluation engine")
    
    # Run a task
    task = "Analyze the impact of AI on software development"
    print(f"\n2️⃣  Running task: '{task}'")
    result = graph.run(task)
    print(f"   ✓ Task status: {result['status']}")
    print(f"   ✓ Result: {result['agent_results']}")
    
    # Check memory and evaluation
    print("\n3️⃣  Memory and Evaluation Stats:")
    memory_stats = graph.get_memory_stats()
    print(f"   - Short-term memory entries: {memory_stats['short_term_size']}")
    print(f"   - Long-term memory categories: {memory_stats['long_term_categories']}")
    print(f"   - Total long-term entries: {memory_stats['long_term_total']}")
    
    eval_report = graph.get_evaluation_report()
    print(f"   - Evaluation Report: {eval_report}")


def demo_agent_pool():
    """Demonstrate agent pool with parallel execution"""
    print("\n" + "="*60)
    print("🤖 SwarmForge - Agent Pool Demo")
    print("="*60)
    
    # Setup
    env_vars = setup_environment()
    llm = get_llm()
    
    # Create orchestrator
    print("\n1️⃣  Creating SwarmOrchestrator...")
    orchestrator = SwarmOrchestrator(llm)
    
    # Create a pool of specialized agents
    print("\n2️⃣  Creating agent pool with specialized roles...")
    pool = orchestrator.create_pool("research_team")
    
    # Add agents with different roles
    agents_config = [
        AgentConfig(
            name="researcher_001",
            role=AgentRole.RESEARCHER,
            tools=["web_search"],
            max_iterations=3
        ),
        AgentConfig(
            name="analyzer_001",
            role=AgentRole.ANALYZER,
            tools=["data_analysis"],
            max_iterations=3
        ),
        AgentConfig(
            name="synthesizer_001",
            role=AgentRole.SYNTHESIZER,
            tools=["code_execution"],
            max_iterations=3
        ),
    ]
    
    for config in agents_config:
        pool.add_agent(config)
        print(f"   ✓ Added {config.name} ({config.role.value})")
    
    # Test different execution modes
    task = "Analyze recent trends in machine learning"
    
    for mode in [ExecutionMode.SEQUENTIAL, ExecutionMode.PARALLEL]:
        print(f"\n3️⃣  Executing in {mode.value.upper()} mode...")
        pool.set_execution_mode(mode)
        
        import asyncio
        result = asyncio.run(pool.execute(task))
        
        print(f"   ✓ Execution completed")
        for agent_name, response in result.items():
            print(f"     - {agent_name}: {response['status']}")
    
    # Print pool statistics
    print("\n4️⃣  Pool Statistics:")
    stats = orchestrator.get_orchestration_stats()
    print(f"   - Total pools: {stats['total_pools']}")
    print(f"   - Total executions: {stats['total_executions']}")
    for pool_name, pool_stats in stats["pools"].items():
        print(f"   - Pool '{pool_name}': {pool_stats['total_agents']} agents")


def demo_full_workflow():
    """Demonstrate a complete end-to-end workflow"""
    print("\n" + "="*60)
    print("🤖 SwarmForge - Full Workflow Demo")
    print("="*60)
    
    # Setup
    env_vars = setup_environment()
    llm = get_llm()
    
    print("\n📋 Full Workflow Sequence:")
    print("   1. Initialize LangGraph with memory")
    print("   2. Create specialized agent pool")
    print("   3. Execute parallel research and analysis")
    print("   4. Evaluate results")
    print("   5. Store findings in long-term memory")
    
    # Initialize components
    graph = SwarmGraph(llm)
    orchestrator = SwarmOrchestrator(llm)
    
    # Create research team
    research_pool = orchestrator.create_pool("research_team")
    for role in [AgentRole.RESEARCHER, AgentRole.ANALYZER]:
        research_pool.add_agent(AgentConfig(
            name=f"{role.value}_agent",
            role=role,
            max_iterations=3
        ))
    
    research_pool.set_execution_mode(ExecutionMode.PARALLEL)
    
    # Execute a complex task
    complex_task = "Research and analyze the environmental impact of AI infrastructure"
    
    print(f"\n▶️  Executing task: {complex_task}")
    result = graph.run(complex_task)
    
    print(f"\n✅ Workflow completed!")
    print(f"   Status: {result['status']}")
    print(f"   Memory stats: {graph.get_memory_stats()}")


def main():
    """Main entry point"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║          Welcome to SwarmForge Framework Demo              ║")
    print("║   A Scalable Multi-Agent AI Framework with LLM Coord.      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\nSelect a demo to run:")
    print("1. Basic Workflow (LangGraph, Memory, Evaluation)")
    print("2. Agent Pool Demo (Parallel/Sequential Execution)")
    print("3. Full End-to-End Workflow")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            demo_basic_workflow()
        elif choice == "2":
            demo_agent_pool()
        elif choice == "3":
            demo_full_workflow()
        elif choice == "4":
            print("\n👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice. Please try again.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("   - Make sure you have an LLM API key set (OPENAI_API_KEY or GROQ_API_KEY)")
        print("   - Check that all dependencies are installed: pip install -r requirements.txt")
        print("   - Ensure your .env file is properly configured")


if __name__ == "__main__":
    main()
