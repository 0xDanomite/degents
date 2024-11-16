from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from langchain_anthropic import ChatAnthropic
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
import asyncio
import os
from dotenv import load_dotenv

load_dotenv('../../.env.local')

class AgentActivity:
    def __init__(self, activity_type: str, message: str, details: Optional[Dict] = None):
        self.type = activity_type  # 'info', 'analysis', 'trade', 'warning', 'error'
        self.message = message
        self.details = details
        self.timestamp = datetime.now().isoformat()

class AgentService:
    def __init__(self):
        try:
            print("Initializing AgentService...")

            # Initialize CDP components with environment variables
            self.agentkit = CdpAgentkitWrapper(
                cdp_api_key_name=os.getenv('CDP_API_KEY_NAME'),
                cdp_api_key_private_key=os.getenv('CDP_API_KEY_PRIVATE_KEY'),
                network_id=os.getenv('NETWORK_ID', 'base-sepolia')
            )
            print("CDP AgentKit initialized")

            self.toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.agentkit)
            tools = self.toolkit.get_tools()
            print(f"CDP Toolkit initialized with {len(tools)} tools")
            print("Available tools:", [t.name for t in tools])

            # Initialize AI components
            self.llm = ChatAnthropic(
                anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
                model_name="claude-3-opus-20240229"
            )
            print("Claude AI initialized")

            # Agent state
            self.is_running = False
            self.auto_trading = False

            # Activity tracking
            self.activities = deque(maxlen=100)  # Keep last 100 activities
            self.websocket_connections = set()

            # Load wallet data if exists
            self.wallet_data_file = "wallet_data.txt"
            self._load_wallet_data()

            print("AgentService initialization complete")
            self.add_activity("info", "Agent service initialized successfully")

        except Exception as e:
            print(f"Error initializing AgentService: {str(e)}")
            raise

    def _load_wallet_data(self):
        """Load existing wallet data if available"""
        try:
            if os.path.exists(self.wallet_data_file):
                with open(self.wallet_data_file, 'r') as f:
                    wallet_data = f.read()
                    if wallet_data:
                        self.add_activity("info", "Loaded existing wallet data")
                        print("Wallet data loaded successfully")
        except Exception as e:
            print(f"Error loading wallet data: {str(e)}")
            self.add_activity("warning", "No existing wallet data found")

    def add_activity(self, activity_type: str, message: str, details: Optional[Dict] = None):
        """Add new activity and notify connected clients"""
        try:
            activity = AgentActivity(activity_type, message, details)
            self.activities.append(activity)
            if self.websocket_connections:  # Only create task if there are connections
                asyncio.create_task(self._notify_clients(activity))
        except Exception as e:
            print(f"Error adding activity: {str(e)}")

    async def _notify_clients(self, activity: AgentActivity):
        """Send activity updates to connected WebSocket clients"""
        message = {
            "type": "agent_activity",
            "data": {
                "type": activity.type,
                "message": activity.message,
                "details": activity.details,
                "timestamp": activity.timestamp
            }
        }
        dead_connections = set()
        for ws in self.websocket_connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"Error sending to websocket: {str(e)}")
                dead_connections.add(ws)

        # Remove dead connections
        self.websocket_connections = self.websocket_connections - dead_connections

    async def start(self):
        """Start the agent"""
        if not self.is_running:
            self.is_running = True
            self.add_activity("info", "Agent started")
            asyncio.create_task(self.monitor_trends())
            print("Agent started successfully")

    async def stop(self):
        """Stop the agent"""
        if self.is_running:
            self.is_running = False
            self.add_activity("info", "Agent stopped")
            print("Agent stopped successfully")

    def set_auto_trading(self, enabled: bool):
        """Enable/disable auto trading"""
        self.auto_trading = enabled
        self.add_activity("info", f"Auto trading {'enabled' if enabled else 'disabled'}")
        print(f"Auto trading {'enabled' if enabled else 'disabled'}")

    async def get_wallet_info(self) -> Dict:
        """Get wallet details and balance"""
        try:
            print("Getting wallet info...")
            tools = self.toolkit.get_tools()

            # Get wallet details using appropriate tool
            wallet_tool = next((t for t in tools if t.name == "get_wallet_details"), None)
            balance_tool = next((t for t in tools if t.name == "get_balance"), None)

            if not wallet_tool or not balance_tool:
                raise Exception("Required wallet tools not found")

            wallet_details = await wallet_tool.run("")
            print("Wallet details fetched:", wallet_details)

            balance = await balance_tool.run("")
            print("Balance fetched:", balance)

            return {
                "address": wallet_details.get("address", "No address found"),
                "balance": balance if balance else "0",
                "network": "base-sepolia",
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error getting wallet info: {str(e)}")
            self.add_activity("error", f"Error getting wallet info: {str(e)}")
            return {
                "address": "Error fetching address",
                "balance": "0",
                "network": "base-sepolia",
                "last_updated": datetime.now().isoformat()
            }

    async def get_token_holdings(self) -> List[Dict]:
        """Get list of tokens held by the wallet"""
        try:
            print("Getting token holdings...")
            tools = self.toolkit.get_tools()
            balance_tool = next((t for t in tools if t.name == "get_balance"), None)

            if not balance_tool:
                raise Exception("Balance tool not found")

            tokens = await balance_tool.run("list_tokens")
            print("Tokens fetched:", tokens)

            holdings = []
            for token in tokens:
                balance = await balance_tool.run(f"get_balance {token['address']}")
                holdings.append({
                    "symbol": token["symbol"],
                    "balance": balance,
                    "token_address": token["address"],
                    "last_updated": datetime.now().isoformat()
                })

            return holdings

        except Exception as e:
            print(f"Error getting token holdings: {str(e)}")
            self.add_activity("error", f"Error getting token holdings: {str(e)}")
            return []

    async def manage_funds(self, action: str, amount: float) -> Dict:
        """Handle deposit/withdrawal of funds"""
        try:
            if action == "deposit":
                self.add_activity("info", f"Initiating deposit of {amount} ETH...")
                result = await self.toolkit.get_tools()[0].run(f"request_faucet_funds {amount}")
                self.add_activity("success", f"Successfully deposited {amount} ETH",
                                {"tx_hash": result.get("tx_hash")})
                return result
            elif action == "withdraw":
                self.add_activity("info", f"Initiating withdrawal of {amount} ETH...")
                result = await self.toolkit.get_tools()[0].run(f"transfer {amount}")
                self.add_activity("success", f"Successfully withdrawn {amount} ETH",
                                {"tx_hash": result.get("tx_hash")})
                return result
            else:
                raise ValueError("Invalid action")
        except Exception as e:
            print(f"Error managing funds: {str(e)}")
            self.add_activity("error", f"Fund management error: {str(e)}")
            raise

    async def monitor_trends(self):
        """Main monitoring loop"""
        print("Starting trend monitoring...")
        while self.is_running:
            try:
                self.add_activity("info", "Scanning for trending tokens...")

                # Implement trend monitoring logic here
                await asyncio.sleep(30)  # Wait before next scan

            except Exception as e:
                print(f"Error in trend monitoring: {str(e)}")
                self.add_activity("error", f"Monitoring error: {str(e)}")
                await asyncio.sleep(5)

    def get_state(self) -> Dict:
        """Get current agent state"""
        return {
            "is_running": self.is_running,
            "auto_trading": self.auto_trading,
            "last_update": datetime.now().isoformat()
        }

# Create singleton instance
agent = AgentService()
