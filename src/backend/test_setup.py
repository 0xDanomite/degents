# src/backend/test_setup.py
from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env.local')

def test_setup():
    print("Testing CDP Agent Setup...")

    try:
        # 1. Test CDP AgentKit initialization
        print("\n1. Testing CDP AgentKit initialization...")
        agentkit = CdpAgentkitWrapper()
        print("✓ CDP AgentKit initialized successfully")

        # 2. Test toolkit creation
        print("\n2. Testing CDP Toolkit creation...")
        toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = toolkit.get_tools()
        print(f"✓ CDP Toolkit created successfully with {len(tools)} tools")
        print("Available tools:")
        for tool in tools:
            print(f"  - {tool.name}")

        # 3. Test Claude/Anthropic integration
        print("\n3. Testing Anthropic integration...")
        llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        response = llm.invoke([HumanMessage(content="Hello! Please respond with a simple 'Hello from Claude'")])
        print(f"✓ Anthropic response: {response.content}")

        # 4. Test wallet functionality
        print("\n4. Testing wallet functionality...")
        wallet_data = agentkit.export_wallet()
        print("✓ Wallet data exported successfully")

        print("\nAll components initialized successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error during setup test: {str(e)}")
        return False

if __name__ == "__main__":
    test_setup()
