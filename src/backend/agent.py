# src/backend/agent.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from datetime import datetime
from typing import Optional, Dict
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

# Load environment variables
load_dotenv('../../.env.local')

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AutoTradingRequest(BaseModel):
    enabled: bool

class TrendAgent:
    def __init__(self):
        self.wallet_data_file = "wallet_data.txt"
        self.agent_executor = None
        self.config = None
        self.is_running = False
        self.auto_trading = False
        self.initialize_agent()

    def initialize_agent(self):
        """Initialize the agent with CDP Agentkit"""
        try:
            # Initialize LLM
            llm = ChatOpenAI(model="gpt-4")

            # Load existing wallet data if available
            wallet_data = None
            if os.path.exists(self.wallet_data_file):
                with open(self.wallet_data_file) as f:
                    wallet_data = f.read()

            # Configure CDP Agentkit
            values = {}
            if wallet_data:
                values = {"cdp_wallet_data": wallet_data}

            # Initialize CDP wrapper
            agentkit = CdpAgentkitWrapper(**values)

            # Save wallet data
            wallet_data = agentkit.export_wallet()
            with open(self.wallet_data_file, "w") as f:
                f.write(wallet_data)

            # Initialize toolkit and get tools
            cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
            tools = cdp_toolkit.get_tools()

            # Configure memory
            memory = MemorySaver()

            # Custom prompt for trend trading agent
            system_prompt = """You are an AI agent specialized in monitoring and trading meme tokens based on social media trends.

            Available tools include:
            1. Wallet management (get_wallet_details, get_balance)
            2. Token operations (deploy_token, wow_create_token, wow_buy_token, wow_sell_token)
            3. Trading operations (trade, transfer)
            4. Faucet interaction (request_faucet_funds)

            When creating or trading tokens:
            1. Always check wallet balance first
            2. Request faucet funds if needed on testnet
            3. Verify transaction success
            4. Monitor token performance
            5. Consider trend strength and momentum

            Be cautious and thorough in your operations while maintaining efficiency."""

            # Create agent
            self.agent_executor, self.config = create_react_agent(
                llm,
                tools=tools,
                checkpointer=memory,
                state_modifier=system_prompt,
            )

            print("Agent initialized successfully!")
            return True

        except Exception as e:
            print(f"Error initializing agent: {e}")
            return False

    async def process_trend(self, trend_data: Dict):
        """Process a trend and make trading decisions"""
        if not self.is_running or not self.auto_trading:
            return

        prompt = f"""
        Analyze this trend and determine appropriate action:
        Trend: {trend_data['name']}
        Score: {trend_data['score']}
        Volume: {trend_data['volume']}

        1. Check if related tokens exist
        2. If no tokens exist, consider creating one using wow_create_token
        3. If tokens exist, analyze and consider trading
        4. Ensure proper risk management
        """

        try:
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=prompt)]},
                self.config
            ):
                if "agent" in chunk:
                    print("Agent thought:", chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print("Tool usage:", chunk["tools"]["messages"][0].content)

        except Exception as e:
            print(f"Error processing trend: {e}")

    def get_state(self):
        """Get current agent state"""
        return {
            "is_running": self.is_running,
            "auto_trading": self.auto_trading,
            "last_update": datetime.now().isoformat(),
        }

# Create singleton agent instance
trend_agent = TrendAgent()

@app.post("/api/agent/start")
async def start_agent():
    try:
        trend_agent.is_running = True
        return {
            "success": True,
            "message": "Agent started successfully",
            "state": trend_agent.get_state()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.post("/api/agent/stop")
async def stop_agent():
    try:
        trend_agent.is_running = False
        return {
            "success": True,
            "message": "Agent stopped successfully",
            "state": trend_agent.get_state()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.post("/api/agent/auto-trading")
async def set_auto_trading(request: AutoTradingRequest):
    try:
        trend_agent.auto_trading = request.enabled
        return {
            "success": True,
            "message": f"Auto-trading {'enabled' if request.enabled else 'disabled'}",
            "state": trend_agent.get_state()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.get("/api/agent/state")
async def get_agent_state():
    return {
        "success": True,
        "state": trend_agent.get_state()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.post("/api/agent/process-trend")
async def process_trend(trend: Dict):
    try:
        await trend_agent.process_trend(trend)
        return {"success": True, "message": "Trend processing started"}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    try:
        while True:
            data = await websocket.receive_text()  # You can process data from the client if needed
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
