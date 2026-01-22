"""LiveKit Tools for order management in the drive-thru agent.

This module provides the coordination layer between the LLM and the order management
system. Tools validate inputs using menu_validation, then delegate to OrderStateManager
for state mutations.

Key Principles:
- Thin coordination layer: orchestrate, don't implement logic
- Validate before mutate: always validate using menu_validation
- Return helpful string responses for the LLM to relay to users
"""

from livekit.agents import llm
from livekit.agents.llm import function_tool

from src.menu_provider import MenuProvider
from src.menu_validation import validate_order_item
from src.order_state_manager import OrderStateManager


def create_order_tools(
    order_state: OrderStateManager,
    menu_provider: MenuProvider,
) -> list[llm.Tool]:
    """
    Create LiveKit Tool instances with dependencies injected.

    This factory function uses closures to inject the OrderStateManager and
    MenuProvider dependencies into the tool functions. This allows each session
    to have its own OrderStateManager while sharing a single MenuProvider.

    Args:
        order_state: OrderStateManager instance for this session
        menu_provider: MenuProvider instance (shared singleton)

    Returns:
        List of FunctionTool objects that can be registered with an Agent

    Example:
        >>> menu_provider = MenuProvider("menu.json")
        >>> order_state = OrderStateManager(session_id="abc-123")
        >>> tools = create_order_tools(order_state, menu_provider)
        >>> agent = Agent(tools=tools, ...)
    """

    @function_tool(
        name="add_item_to_order",
        description=(
            "Add a menu item to the customer's order. Always validate the item "
            "exists on the menu before adding. Use this when the customer requests "
            "a menu item."
        ),
        raw_schema={
            "name": "add_item_to_order",
            "description": (
                "Add a menu item to the customer's order. Always validate the item "
                "exists on the menu before adding. Use this when the customer requests "
                "a menu item."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The menu category (e.g., 'Beef & Pork', 'Breakfast', 'Beverages')",
                        "enum": [
                            "Breakfast",
                            "Beef & Pork",
                            "Chicken & Fish",
                            "Salads",
                            "Snacks & Sides",
                            "Desserts",
                            "Beverages",
                            "Coffee & Tea",
                            "Smoothies & Shakes",
                        ],
                    },
                    "item_name": {
                        "type": "string",
                        "description": "The exact name of the menu item (e.g., 'Big Mac', 'Egg McMuffin')",
                    },
                    "modifiers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of modifiers or customizations (e.g., ['No Pickles', 'Extra Sauce'])",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of this item to add",
                        "default": 1,
                        "minimum": 1,
                    },
                },
                "required": ["category", "item_name"],
            },
        },
    )
    async def add_item_to_order(
        category: str,
        item_name: str,
        modifiers: list[str] | None = None,
        quantity: int = 1,
    ) -> str:
        """
        Add a menu item to the customer's order.

        This tool validates the item against the menu before adding it to the order.
        If validation fails, it returns an error message without mutating state.

        Args:
            category: Menu category (e.g., 'Beef & Pork', 'Breakfast')
            item_name: Name of the menu item (e.g., 'Big Mac')
            modifiers: Optional list of modifiers (e.g., ['No Pickles', 'Extra Sauce'])
            quantity: Number of items to add (default: 1)

        Returns:
            Confirmation message if successful, error message if validation fails
        """
        # Normalize inputs
        modifiers = modifiers or []

        # Validate item exists and modifiers are valid
        validation_result = validate_order_item(
            item_name=item_name,
            category=category,
            modifiers=modifiers,
            menu=menu_provider.get_menu(),
            fuzzy_threshold=85,
        )

        # If invalid, return error message without mutating state
        if not validation_result.is_valid:
            return f"Sorry, I couldn't add that item: {validation_result.error_message}"

        # Use matched item (might be fuzzy matched to correct spelling)
        matched_item = validation_result.matched_item
        order_state.add_item(
            item_name=matched_item.item_name,  # Use exact match from menu
            category=category,
            modifiers=modifiers,
            quantity=quantity,
        )

        # Build confirmation message
        modifier_text = ""
        if modifiers:
            modifier_text = f" with {', '.join(modifiers)}"

        if quantity > 1:
            return f"Added {quantity} {matched_item.item_name}{modifier_text} to your order."
        else:
            return f"Added one {matched_item.item_name}{modifier_text} to your order."

    @function_tool(
        name="complete_order",
        description=(
            "Complete the order and generate the final order summary. "
            "Call this when the customer says they're done ordering."
        ),
        raw_schema={
            "name": "complete_order",
            "description": (
                "Complete the order and generate the final order summary. "
                "Call this when the customer says they're done ordering."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    )
    async def complete_order() -> str:
        """
        Complete the order and generate the final order summary.

        This tool should be called when the customer indicates they're done ordering.
        It finalizes the order and writes the final JSON file.

        Returns:
            Order summary if successful, prompt to add items if order is empty
        """
        # Check if order is empty
        if order_state.is_empty():
            return "Your order is empty. Would you like to add something?"

        # Complete order (writes final JSON)
        final_order = order_state.complete_order()

        # Build summary
        summary = final_order["order_summary"]
        total_items = final_order["total_items"]

        return f"Order complete! You ordered: {summary}. Total items: {total_items}. Thank you!"

    @function_tool(
        name="remove_item_from_order",
        description=(
            "Remove an item from the order. Useful when customer wants to "
            "cancel an item. If multiple items with the same name exist, "
            "removes the most recently added one."
        ),
        raw_schema={
            "name": "remove_item_from_order",
            "description": (
                "Remove an item from the order. Useful when customer wants to "
                "cancel an item. If multiple items with the same name exist, "
                "removes the most recently added one."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Name of the item to remove (e.g., 'Big Mac')",
                    },
                },
                "required": ["item_name"],
            },
        },
    )
    async def remove_item_from_order(item_name: str) -> str:
        """
        Remove an item from the order.

        Useful when a customer wants to cancel or remove an item. If multiple items
        with the same name exist, this removes the most recently added one.

        Args:
            item_name: Name of the item to remove (e.g., 'Big Mac')

        Returns:
            Confirmation message if successful, error message if item not found
        """
        # Find item by name (use latest item with that name)
        items = order_state.get_items()
        item_to_remove = None

        # Search from end (most recent items first)
        for item in reversed(items):
            if item.item_name.lower() == item_name.lower():
                item_to_remove = item
                break

        if item_to_remove is None:
            return f"I don't see '{item_name}' in your order."

        # Remove item
        success = order_state.remove_item(item_to_remove.item_id)

        if success:
            return f"Removed {item_name} from your order."
        else:
            return f"Couldn't remove {item_name}. Please try again."

    # Return decorated functions (they are now FunctionTool instances)
    return [add_item_to_order, complete_order, remove_item_from_order]
