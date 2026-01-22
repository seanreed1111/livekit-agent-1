"""Order state management and persistence.

This module provides the single source of truth for order state in the drive-thru agent.
All order mutations (add, remove, update) flow through OrderStateManager.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class OrderItem:
    """A single item in an order.

    Represents one line item with all its details.
    Immutable after creation (use update methods on OrderStateManager).
    """

    item_name: str
    category: str
    modifiers: list[str] = field(default_factory=list)
    quantity: int = 1
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "category": self.category,
            "modifiers": self.modifiers,
            "quantity": self.quantity,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItem":
        """Create OrderItem from dictionary."""
        return cls(
            item_id=data["item_id"],
            item_name=data["item_name"],
            category=data["category"],
            modifiers=data.get("modifiers", []),
            quantity=data.get("quantity", 1),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class OrderStateManager:
    """Single source of truth for order state and persistence.

    Manages:
    - In-memory order state (list of OrderItem)
    - Incremental logging (append after each mutation)
    - Final JSON output (on order completion)
    - Session lifecycle

    Thread-safety: NOT thread-safe. Each agent session gets its own instance.
    """

    def __init__(self, session_id: str, output_dir: str = "orders") -> None:
        """Initialize order state for a session.

        Args:
            session_id: Unique session identifier (UUID)
            output_dir: Directory to save order files

        Creates:
            - {output_dir}/{session_id}/ directory
            - incremental_log.jsonl file (empty initially)
        """
        self._session_id = session_id
        self._output_dir = Path(output_dir)
        self._session_dir = self._output_dir / session_id

        # In-memory state
        self._items: list[OrderItem] = []
        self._start_time = datetime.now()
        self._status = "in_progress"  # or "completed", "cancelled"

        # File paths
        self._incremental_log_path = self._session_dir / "incremental_log.jsonl"
        self._final_order_path = self._session_dir / "final_order.json"

        # Create session directory and empty log file
        self._ensure_session_directory()

    # Command Methods (mutations)

    def add_item(
        self,
        item_name: str,
        category: str,
        modifiers: list[str] | None = None,
        quantity: int = 1,
    ) -> OrderItem:
        """Add item to order.

        Args:
            item_name: Name of the menu item
            category: Menu category
            modifiers: List of modifier names (default: empty list)
            quantity: Number of items (default: 1)

        Returns:
            The created OrderItem

        Side effects:
            - Appends item to in-memory order
            - Appends to incremental log file
        """
        # Create OrderItem
        item = OrderItem(
            item_name=item_name,
            category=category,
            modifiers=modifiers or [],
            quantity=quantity,
        )

        # Add to in-memory state
        self._items.append(item)

        # Log event
        self._append_to_log(
            {
                "event": "add_item",
                "timestamp": datetime.now().isoformat(),
                "item": item.to_dict(),
            }
        )

        return item

    def remove_item(self, item_id: str) -> bool:
        """Remove item by ID.

        Args:
            item_id: The UUID of the item to remove

        Returns:
            True if found and removed, False otherwise

        Side effects:
            - Removes item from in-memory order
            - Appends removal event to incremental log
        """
        # Find item
        item_to_remove = None
        for item in self._items:
            if item.item_id == item_id:
                item_to_remove = item
                break

        if item_to_remove is None:
            return False

        # Remove from in-memory state
        self._items.remove(item_to_remove)

        # Log event
        self._append_to_log(
            {
                "event": "remove_item",
                "timestamp": datetime.now().isoformat(),
                "item_id": item_id,
                "item_name": item_to_remove.item_name,
            }
        )

        return True

    def update_item_quantity(self, item_id: str, new_quantity: int) -> bool:
        """Update quantity for an item.

        Args:
            item_id: The UUID of the item
            new_quantity: New quantity (must be > 0)

        Returns:
            True if found and updated, False otherwise

        Side effects:
            - Updates item quantity in-memory
            - Appends update event to incremental log
        """
        if new_quantity <= 0:
            return False

        # Find item
        item_to_update = None
        for item in self._items:
            if item.item_id == item_id:
                item_to_update = item
                break

        if item_to_update is None:
            return False

        # Update quantity
        old_quantity = item_to_update.quantity
        item_to_update.quantity = new_quantity

        # Log event
        self._append_to_log(
            {
                "event": "update_quantity",
                "timestamp": datetime.now().isoformat(),
                "item_id": item_id,
                "item_name": item_to_update.item_name,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
            }
        )

        return True

    def complete_order(self) -> dict:
        """Mark order complete and generate final JSON.

        Returns:
            Final order dictionary

        Side effects:
            - Writes final_order.json file
            - Appends completion event to incremental log
        """
        self._status = "completed"

        # Build final order dict
        final_order = {
            "session_id": self._session_id,
            "start_time": self._start_time.isoformat(),
            "completion_time": datetime.now().isoformat(),
            "status": self._status,
            "items": [item.to_dict() for item in self._items],
            "total_items": self.get_total_count(),
            "order_summary": self.get_order_summary(),
        }

        # Write final JSON
        with open(self._final_order_path, "w") as f:
            json.dump(final_order, f, indent=2)

        # Log completion event
        self._append_to_log(
            {
                "event": "complete_order",
                "timestamp": datetime.now().isoformat(),
                "total_items": self.get_total_count(),
            }
        )

        return final_order

    def clear_order(self) -> None:
        """Clear all items (for cancellation/restart).

        Side effects:
            - Clears in-memory order
            - Appends clear event to incremental log
        """
        self._items.clear()
        self._status = "cancelled"

        # Log clear event
        self._append_to_log(
            {"event": "clear_order", "timestamp": datetime.now().isoformat()}
        )

    # Query Methods (read-only)

    def get_items(self) -> list[OrderItem]:
        """Get all items in current order (read-only copy).

        Returns:
            List of OrderItem (copies, not references)
        """
        # Return copy to prevent external mutations
        return [
            OrderItem(
                item_id=item.item_id,
                item_name=item.item_name,
                category=item.category,
                modifiers=item.modifiers.copy(),  # Copy modifiers list
                quantity=item.quantity,
                timestamp=item.timestamp,
            )
            for item in self._items
        ]

    def get_item_by_id(self, item_id: str) -> OrderItem | None:
        """Get a specific item by its ID.

        Args:
            item_id: The UUID of the item

        Returns:
            OrderItem copy if found, None otherwise
        """
        for item in self._items:
            if item.item_id == item_id:
                return OrderItem(
                    item_id=item.item_id,
                    item_name=item.item_name,
                    category=item.category,
                    modifiers=item.modifiers.copy(),
                    quantity=item.quantity,
                    timestamp=item.timestamp,
                )
        return None

    def get_total_count(self) -> int:
        """Get total number of items (accounting for quantities).

        Example: If order has 2x Big Mac (quantity=2) and 1x Fries (quantity=1),
        returns 3.

        Returns:
            Total count of all items
        """
        return sum(item.quantity for item in self._items)

    def get_order_summary(self) -> str:
        """Get human-readable order summary.

        Returns:
            String like "2 Big Mac, 1 Medium Fries, 1 Coke"
        """
        if not self._items:
            return "No items"

        # Group items for display
        summary_parts = []
        for item in self._items:
            if item.quantity > 1:
                summary_parts.append(f"{item.quantity} {item.item_name}")
            else:
                summary_parts.append(f"1 {item.item_name}")

        return ", ".join(summary_parts)

    def is_empty(self) -> bool:
        """Check if order has no items.

        Returns:
            True if order is empty, False otherwise
        """
        return len(self._items) == 0

    # Private Methods (implementation details)

    def _append_to_log(self, event: dict) -> None:
        """Append event to incremental log file (JSONL format).

        Args:
            event: Event dictionary to log
        """
        with open(self._incremental_log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def _ensure_session_directory(self) -> None:
        """Create session directory if it doesn't exist."""
        self._session_dir.mkdir(parents=True, exist_ok=True)

        # Create empty log file if it doesn't exist
        if not self._incremental_log_path.exists():
            self._incremental_log_path.touch()
