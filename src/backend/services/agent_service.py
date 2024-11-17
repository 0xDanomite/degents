from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from langchain_anthropic import ChatAnthropic
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
import asyncio
import json
import os
from dotenv import load_dotenv
from .token_trend_service import TokenTrendService


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

            self.wallet_data_file = "wallet_data.txt"
            self.wallet_address = None
            self.generated_tokens = []
            # Initialize CDP components with environment variables
            network = os.getenv('NETWORK_ID', 'base-sepolia')
            print(f"Using network: {network}")

            self.agentkit = CdpAgentkitWrapper(
                cdp_api_key_name=os.getenv('CDP_API_KEY_NAME'),
                cdp_api_key_private_key=os.getenv('CDP_API_KEY_PRIVATE_KEY'),
                network_id=network
            )
            print("CDP AgentKit initialized")

            # Export wallet data immediately after initialization
            wallet_data = self.agentkit.export_wallet()
            print("Wallet data exported:", wallet_data[:50] + "..." if wallet_data else "No wallet data")

            # Save wallet data
            with open(self.wallet_data_file, 'w') as f:
                f.write(wallet_data)
            print("Wallet data saved to file")

            # Initialize toolkit
            self.toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.agentkit)
            tools = self.toolkit.get_tools()
            print(f"CDP Toolkit initialized with {len(tools)} tools")
            print("Available tools:", [t.name for t in tools])

            # Get initial wallet details to verify setup
            asyncio.create_task(self._verify_wallet_setup())

            # Initialize AI components
            self.llm = ChatAnthropic(
                anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
                model_name="claude-3-opus-20240229"
            )
            print("Claude AI initialized")

            self.trend_service = TokenTrendService()
            print("Token trend service initialized")

            # Agent state
            self.is_running = False
            self.auto_trading = False

            # Activity tracking
            self.activities = deque(maxlen=100)  # Keep last 100 activities
            self.websocket_connections = set()

            # Load wallet data if exists
            # self.wallet_data_file = "wallet_data.txt"
            self._load_wallet_data()

            print("AgentService initialization complete")
            self.add_activity("info", "Agent service initialized successfully")

        except Exception as e:
            print(f"Error initializing AgentService: {str(e)}")
            raise

    async def _verify_wallet_setup(self):
        """Verify wallet is properly set up"""
        try:
            # First, request faucet funds if on testnet
            if os.getenv('NETWORK_ID', 'base-sepolia') == 'base-sepolia':
                print("Requesting faucet funds for testnet...")
                tools = self.toolkit.get_tools()
                faucet_tool = None

                for tool in tools:
                    if tool.name == "request_faucet_funds":
                        faucet_tool = tool
                        break

                if faucet_tool:
                    try:
                        result = await faucet_tool.arun({
                            "amount": 0.1
                        })
                        print("Faucet request result:", result)
                    except Exception as e:
                        print(f"Error requesting faucet funds: {str(e)}")

            # Get wallet details
            wallet_tool = None
            for tool in tools:
                if tool.name == "get_wallet_details":
                    wallet_tool = tool
                    break

            if wallet_tool:
                try:
                    wallet_info = await wallet_tool.arun({})
                    print("Initial wallet details:", wallet_info)

                    # Extract address from the wallet info string
                    if isinstance(wallet_info, str) and "default address:" in wallet_info:
                        address = wallet_info.split("default address:")[-1].strip()
                        self.add_activity("info", f"Wallet initialized with address: {address}")

                        # Store the address for later use
                        self.wallet_address = address
                        print(f"Wallet address stored: {address}")
                    else:
                        print("Unexpected wallet info format:", wallet_info)
                except Exception as e:
                    print(f"Error getting wallet details: {str(e)}")
            else:
                print("Warning: get_wallet_details tool not found")

        except Exception as e:
            print(f"Error verifying wallet setup: {str(e)}")

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

            # Get balance using the correct input format
            balance_tool = next((t for t in tools if t.name == "get_balance"), None)
            if balance_tool:
                try:
                    balance = await balance_tool.arun({
                        "asset_id": "eth"
                    })
                    print("Raw balance response:", balance)
                except Exception as e:
                    print(f"Error getting balance: {str(e)}")
                    balance = "0"
            else:
                balance = "0"

            # Use the stored wallet address
            return {
                "address": getattr(self, 'wallet_address', 'No address found'),
                "balance": balance if balance else "0",
                "network": os.getenv('NETWORK_ID', 'base-sepolia'),
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error getting wallet info: {str(e)}")
            self.add_activity("error", f"Error getting wallet info: {str(e)}")
            return {
                "address": "Error fetching address",
                "balance": "0",
                "network": os.getenv('NETWORK_ID', 'base-sepolia'),
                "last_updated": datetime.now().isoformat()
            }

    async def get_eth_balance(self) -> Dict:
        """Get ETH/WETH balance for the wallet"""
        try:
            print("Getting ETH balance...")
            tools = self.toolkit.get_tools()
            balance_tool = next((t for t in tools if t.name == "get_balance"), None)

            if not balance_tool:
                raise Exception("Balance tool not found")

            # Get ETH balance
            eth_result = await balance_tool.arun({
                "asset_id": "eth"
            })

            # Parse the balance from the result string
            # Example format: "Balances for wallet abc123:\n  default: 0.5"
            eth_amount = "0"
            if isinstance(eth_result, str):
                try:
                    # Extract the balance amount
                    balance_line = eth_result.split('\n')[1]  # Get the second line
                    eth_amount = balance_line.split(': ')[1].strip()  # Get amount after colon
                except:
                    print("Could not parse ETH balance from:", eth_result)

            return {
                "eth_balance": eth_amount,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error getting ETH balance: {str(e)}")
            return {
                "eth_balance": "0",
                "last_updated": datetime.now().isoformat()
            }

    async def get_token_holdings(self) -> List[Dict]:
        """Get list of all token holdings excluding ETH"""
        try:
            print("Getting token holdings...")
            tools = self.toolkit.get_tools()
            balance_tool = next((t for t in tools if t.name == "get_balance"), None)

            if not balance_tool:
                raise Exception("Balance tool not found")

            holdings = []

            # First get ETH balance
            try:
                eth_result = await balance_tool.arun({
                    "asset_id": "eth"  # Properly formatted input
                })

                if isinstance(eth_result, str):
                    try:
                        balance_line = eth_result.split('\n')[1]
                        balance = balance_line.split(': ')[1].strip()
                    except:
                        balance = "0"

                    holdings.append({
                        "symbol": "ETH",
                        "balance": balance,
                        "token_address": "native",
                        "last_updated": datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error getting ETH balance: {str(e)}")

            # Initialize generated tokens list if it doesn't exist
            if not hasattr(self, 'generated_tokens'):
                self.generated_tokens = []

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
        """Main monitoring loop with trend-based token creation"""
        print("Starting trend monitoring...")

        while self.is_running:
            try:
                self.add_activity("info", "Analyzing token trends...")

                # Get token recommendations
                analysis = await self.get_meme_combinations()

                if analysis["success"] and self.auto_trading:
                    recommendations = analysis.get("recommendations", [])

                    for token in recommendations:
                        try:
                            # Use the create_meme_token method
                            result = await self.create_meme_token(token)

                            if result["success"]:
                                print(f"Successfully created token: {token['symbol']}")
                            else:
                                print(f"Failed to create token: {result.get('error')}")

                            # Wait between token creations
                            await asyncio.sleep(30)

                        except Exception as e:
                            print(f"Error creating token in monitor_trends: {str(e)}")
                            self.add_activity(
                                "error",
                                f"Failed to create token {token['symbol']}: {str(e)}"
                            )

                # Wait before next trend check
                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                print(f"Error in trend monitoring: {str(e)}")
                self.add_activity("error", f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying # Wait a minute before retrying

    def get_state(self) -> Dict:
        """Get current agent state"""
        return {
            "is_running": self.is_running,
            "auto_trading": self.auto_trading,
            "last_update": datetime.now().isoformat()
        }

    async def generate_meme_token(self, trend1: Dict, trend2: Dict) -> Dict:
        """Generate a new meme token combining two trends using AI"""
        try:
            prompt = f"""You are a creative meme token generator. You'll combine two trending tokens into a new, hilarious meme token.

    Trend 1: {trend1['name']} ({trend1['symbol']})
    Trend 2: {trend2['name']} ({trend2['symbol']})

    Create a new meme token that combines these two trends in a funny and viral way.
    Return ONLY valid JSON with this structure:
    {{
        "name": "Full Token Name",
        "symbol": "TOKEN_SYMBOL",
        "description": "Funny description with emojis",
        "tagline": "Short catchy tagline",
        "meme_potential": "Brief explanation of why this combination is memeable"
    }}

    Make it absurd, funny, and viral - think like a meme lord! Include relevant emojis.
    Remember to return ONLY the JSON object, no additional text or formatting."""

            # Get response from Claude
            response = await self.llm.ainvoke(
                [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract and parse JSON from response
            try:
                # Get just the content string from the response
                response_text = response.content
                print("Raw AI response content:", response_text)  # Debug print

                # Parse the JSON directly from the content
                result = json.loads(response_text)
                print("Parsed AI generated token:", result)  # Debug print

                # Calculate initial and max supply based on trend scores
                combined_score = (trend1["score"] + trend2["score"]) / 2
                initial_supply = int(1_000_000 * (1 + combined_score * 10))

                token_params = {
                    "name": result["name"],
                    "symbol": result["symbol"][:10].upper(),
                    "description": result["description"],
                    "initial_supply": initial_supply,
                    "max_supply": initial_supply * 10,
                    "source_trends": [
                        {"symbol": trend1["symbol"], "score": trend1["score"]},
                        {"symbol": trend2["symbol"], "score": trend2["score"]}
                    ],
                    "tagline": result["tagline"],
                    "meme_potential": result["meme_potential"],
                    "created": False,
                    "transaction_hash": None,
                    "network": os.getenv('NETWORK_ID', 'base-sepolia'),
                    "timestamp": datetime.now().isoformat()  # Add timestamp for sorting
                }

                # Store the generated token
                if not hasattr(self, 'generated_tokens'):
                    self.generated_tokens = []
                self.generated_tokens.append(token_params)

                self.add_activity(
                    "info",
                    f"Generated new meme token: {token_params['symbol']}",
                    token_params
                )

                return {
                    "success": True,
                    "token": token_params
                }

            except json.JSONDecodeError as je:
                print(f"JSON parsing error: {str(je)}")
                print("Problematic response:", response_text)
                raise Exception(f"Failed to parse AI response as JSON: {str(je)}")
            except Exception as parse_error:
                print(f"Error processing AI response: {str(parse_error)}")
                raise parse_error

        except Exception as e:
            print(f"Error generating meme token: {str(e)}")
            self.add_activity("error", f"Failed to generate meme token: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_meme_token(self, token_params: Dict) -> Dict:
        """Create a new meme token using WOW.xyz"""
        try:
            # Get the wow_create_token tool
            tools = self.toolkit.get_tools()
            wow_tool = next((t for t in tools if t.name == "wow_create_token"), None)

            if not wow_tool:
                raise Exception("WOW token creation tool not found")

            self.add_activity(
                "info",
                f"Creating meme token {token_params['symbol']}..."
            )

            # Create the token using the tool directly
            try:
                # Convert supplies to strings
                creation_params = {
                    "name": token_params["name"],
                    "symbol": token_params["symbol"],
                    "description": token_params["description"],
                    "initial_supply": str(token_params["initial_supply"]),
                    "max_supply": str(token_params["max_supply"])
                }

                print("Creating token with params:", creation_params)  # Debug print

                # Use the tool synchronously
                result = wow_tool(creation_params)
                print("Creation result:", result)  # Debug print

                # Parse the result if it's a string
                if isinstance(result, str):
                    try:
                        result = json.loads(result)
                    except json.JSONDecodeError:
                        result = {"transaction_hash": None, "message": result}

            except Exception as tool_error:
                print(f"Tool execution error: {str(tool_error)}")  # Debug print
                raise tool_error

            # Get network details
            network = os.getenv('NETWORK_ID', 'base-sepolia')
            base_scan_url = "https://sepolia.basescan.org" if network == "base-sepolia" else "https://basescan.org"

            # Extract transaction hash from result
            tx_hash = result.get("transaction_hash")

            # Update token params with creation details
            token_params.update({
                "created": True,
                "transaction_hash": tx_hash,
                "network": network,
                "timestamp": datetime.now().isoformat(),
                "base_scan_url": f"{base_scan_url}/tx/{tx_hash}" if tx_hash else None
            })

            # Store the created token
            if not hasattr(self, 'generated_tokens'):
                self.generated_tokens = []
            self.generated_tokens.append(token_params)

            self.add_activity(
                "success",
                f"Created meme token {token_params['symbol']}",
                {
                    "token_params": token_params,
                    "creation_result": result,
                    "base_scan_url": token_params["base_scan_url"]
                }
            )

            return {
                "success": True,
                "result": token_params
            }

        except Exception as e:
            print(f"Error in create_meme_token: {str(e)}")  # Debug print
            self.add_activity(
                "error",
                f"Failed to create token {token_params['symbol']}: {str(e)}"
            )
            return {
                "success": False,
                "error": str(e)
            }

    async def get_meme_combinations(self) -> Dict:
        """Get trending tokens and generate meme combinations"""
        try:
            # Get top trending tokens
            trends = self.trend_service.get_top_trends(2)

            if len(trends) < 2:
                return {
                    "success": False,
                    "message": "Not enough trending tokens available"
                }

            # Generate meme combination
            result = await self.generate_meme_token(trends[0], trends[1])

            if result["success"]:
                return {
                    "success": True,
                    "recommendations": [result["token"]]  # Changed from combinations to recommendations
                }
            else:
                return {
                    "success": False,
                    "message": result["error"]
                }

        except Exception as e:
            print(f"Error getting meme combinations: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    async def get_generated_tokens(self) -> List[Dict]:
        """Get list of all generated tokens"""
        try:
            if not hasattr(self, 'generated_tokens'):
                self.generated_tokens = []
            return self.generated_tokens
        except Exception as e:
            print(f"Error getting generated tokens: {str(e)}")
            return []

# Create singleton instance
agent = AgentService()
