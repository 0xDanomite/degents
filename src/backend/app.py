from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, List
from services.agent_service import AgentService
from services.token_trend_service import TokenTrendService
from pydantic import BaseModel
import os

app = FastAPI()

# Create agent instance
agent = AgentService()
# token_service = TokenTrendService()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug endpoints
@app.get("/")
async def root():
    return {"status": "running", "service": "Trend Token Agent API"}

@app.get("/api/debug/tools")
async def get_available_tools():
    """Debug endpoint to list available CDP tools"""
    try:
        tools = agent.toolkit.get_tools()
        tool_list = [
            {
                "name": t.name,
                "description": t.description
            }
            for t in tools
        ]
        print("Available tools:", tool_list)  # Debug log
        return {
            "available_tools": tool_list
        }
    except Exception as e:
        print(f"Error getting tools: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket connection
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    agent.websocket_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except:
        agent.websocket_connections.remove(websocket)

# Agent control endpoints
@app.post("/api/agent/{action}")
async def control_agent(action: str):
    try:
        if action == "start":
            await agent.start()
        elif action == "stop":
            await agent.stop()
        elif action == "auto-trading":
            enabled = True  # Get from request body in real implementation
            agent.set_auto_trading(enabled)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        return {"success": True, "state": agent.get_state()}
    except Exception as e:
        print(f"Error in agent control: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

# Wallet and holdings endpoints
@app.get("/api/wallet")
async def get_wallet_info():
    try:
        # Get wallet details
        wallet_tool = next((t for t in agent.toolkit.get_tools()
                          if t.name == "get_wallet_details"), None)
        wallet_details = await wallet_tool.arun({}) if wallet_tool else ""

        # Extract address from wallet details
        address = "No address found"
        if isinstance(wallet_details, str) and "default address:" in wallet_details:
            address = wallet_details.split("default address:")[-1].strip()

        # Get ETH balance
        eth_info = await agent.get_eth_balance()

        return {
            "address": address,
            "balance": eth_info["eth_balance"],
            "network": os.getenv('NETWORK_ID', 'base-sepolia'),
            "last_updated": eth_info["last_updated"]
        }
    except Exception as e:
        print(f"Error getting wallet info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/holdings")
async def get_holdings():
    try:
        holdings = await agent.get_token_holdings()
        return {"holdings": holdings}
    except Exception as e:
        print(f"Error getting holdings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fund management
@app.post("/api/wallet/manage-funds")
async def manage_funds(action: str, amount: float):
    try:
        result = await agent.manage_funds(action, amount)
        return result
    except Exception as e:
        print(f"Error managing funds: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

# Token trends endpoints
@app.get("/api/token-trends")
async def get_token_trends():
    try:
        trends = await agent.trend_service.detect_token_trends()
        return {
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting token trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-token")
async def analyze_token(token_data: dict):
    try:
        print(f"Analyzing token: {token_data}")  # Debug log
        result = await agent.analyze_trading_opportunity(token_data, {"exists": True})
        print(f"Analysis result: {result}")  # Debug log
        return result
    except Exception as e:
        print(f"Error analyzing token: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meme-combinations")
async def get_meme_combinations():
    try:
        result = await agent.get_meme_combinations()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-meme-token")
async def create_meme_token(token_params: Dict):
    try:
        result = await agent.create_meme_token(token_params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/generated-tokens")
async def get_generated_tokens():
    try:
        tokens = await agent.get_generated_tokens()
        return {"tokens": tokens}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TokenCreationRequest(BaseModel):
    name: str
    symbol: str
    description: str
    initial_supply: int
    max_supply: int
    tagline: str = ""
    meme_potential: str = ""

@app.post("/api/create-meme-token")
async def create_meme_token(token_data: TokenCreationRequest):
    """Create a new meme token on WOW.xyz"""
    try:
        # Convert Pydantic model to dict
        token_params = token_data.dict()

        # Call agent service to create token
        result = await agent.create_meme_token(token_params)

        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully created token {token_data.symbol}",
                "result": result["result"]
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create token")
            )

    except Exception as e:
        print(f"Error creating meme token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
