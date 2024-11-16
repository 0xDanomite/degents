from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from services.agent_service import AgentService

app = FastAPI()

# Create agent instance
agent = AgentService()

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
        print("Fetching wallet info...")  # Debug log
        wallet_info = await agent.get_wallet_info()
        print("Wallet info response:", wallet_info)  # Debug log
        return wallet_info
    except Exception as e:
        print(f"Error getting wallet info: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/holdings")
async def get_holdings():
    try:
        print("Fetching holdings...")  # Debug log
        holdings = await agent.get_token_holdings()
        print("Holdings response:", holdings)  # Debug log
        return {"holdings": holdings}
    except Exception as e:
        print(f"Error getting holdings: {str(e)}")  # Debug log
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
        # Mock data until we implement token_service
        mock_trends = [
            {
                "symbol": "PEPE",
                "mentions": 25,
                "unique_users": 15,
                "engagement": 150,
                "score": 0.85,
                "token_verified": True,
                "first_seen": datetime.now().isoformat(),
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "WOJAK",
                "mentions": 18,
                "unique_users": 12,
                "engagement": 120,
                "score": 0.75,
                "token_verified": False,
                "first_seen": datetime.now().isoformat(),
                "timestamp": datetime.now().isoformat()
            }
        ]

        return {
            "trends": mock_trends,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting token trends: {str(e)}")  # Debug log
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
