"""DriveThruAgent - Orchestrator for McDonald's drive-thru ordering.

This module provides the DriveThruAgent class that brings together all components
to create a complete drive-thru order taking agent. It defines the agent's persona,
registers tools, and coordinates the conversation flow.

Key Principles:
- Orchestration: Wires components together, doesn't implement logic
- Owns State: Owns OrderStateManager instance (composition)
- Receives Dependencies: Gets MenuProvider, DriveThruLLM via DI
- Defines Persona: Sets instructions and conversation style
"""

import logging

from livekit.agents import Agent

from drive_thru_llm import DriveThruLLM
from menu_provider import MenuProvider
from order_state_manager import OrderStateManager
from tools.order_tools import create_order_tools

logger = logging.getLogger(__name__)


class DriveThruAgent(Agent):
    """McDonald's drive-thru order taking agent.

    Orchestrates:
    - OrderStateManager (owns instance per session)
    - Tools (created with dependencies)
    - DriveThruLLM (wrapped LLM with context injection)
    - Instructions/persona

    This agent extends LiveKit's Agent class and provides all necessary
    components for a complete drive-thru ordering experience.
    """

    def __init__(
        self,
        session_id: str,
        llm: DriveThruLLM,
        menu_provider: MenuProvider,
        output_dir: str = "orders",
    ) -> None:
        """Initialize drive-thru agent.

        Args:
            session_id: Unique session ID
            llm: DriveThruLLM (wrapped LLM)
            menu_provider: MenuProvider for menu access
            output_dir: Directory for order files
        """
        # Store dependencies first
        self._llm = llm
        self._menu_provider = menu_provider
        self._session_id = session_id

        # Create OrderStateManager for this session (agent owns it)
        self._order_state = OrderStateManager(
            session_id=session_id, output_dir=output_dir
        )

        # Create tools with dependencies injected BEFORE calling super().__init__()
        self._tools = create_order_tools(
            order_state=self._order_state, menu_provider=self._menu_provider
        )

        # Log tool creation for diagnostics
        logger.info(f"Created {len(self._tools)} tools for drive-thru agent")

        # Initialize Agent with instructions AND tools
        super().__init__(instructions=self._get_instructions(), tools=self._tools)

    def _get_instructions(self) -> str:
        """Get agent instructions/persona.

        Returns:
            Complete agent instructions including persona, responsibilities,
            and guidelines.
        """
        return """You are a friendly and efficient McDonald's drive-thru order taker.

Your responsibilities:
1. Greet customers warmly when they arrive
2. Listen carefully to their order
3. Use the add_item_to_order function to record each item
4. Confirm each item after adding it
5. When customer is done, use complete_order function
6. Read back the complete order
7. Thank the customer

Guidelines:
- Be concise and natural - avoid overly formal language
- If unsure about an item, ask for clarification
- Always confirm items before adding to order
- Use exact menu item names when confirming
- If customer mentions an item not on the menu, politely inform them
- Be helpful with suggestions if they seem uncertain

Menu Categories:
- Breakfast: Morning items like Egg McMuffin, Hash Browns
- Beef & Pork: Big Mac, Quarter Pounder, burgers
- Chicken & Fish: McNuggets, Filet-O-Fish
- Snacks & Sides: Fries, Apple Slices
- Beverages: Soft drinks
- Coffee & Tea: Hot and iced coffee
- Desserts: Apple Pie, McFlurry
- Smoothies & Shakes

Remember: You have access to the complete menu via your tools. Use them!
"""

    @property
    def agent(self) -> Agent:
        """Get the LiveKit Agent instance.

        Returns:
            The Agent instance (self, since this class extends Agent)
        """
        return self

    @property
    def order_state(self) -> OrderStateManager:
        """Get the order state manager.

        Returns:
            The OrderStateManager instance for this session
        """
        return self._order_state

    @property
    def llm(self) -> DriveThruLLM:
        """Get the DriveThruLLM instance.

        Returns:
            The wrapped LLM with menu context injection
        """
        return self._llm

    @property
    def tools(self) -> list:
        """Get the order management tools.

        Returns:
            List of LiveKit FunctionTool instances
        """
        return self._tools

    async def close(self) -> None:
        """Clean up resources.

        This method can be extended to add cleanup logic if needed in the future.
        """
        pass
