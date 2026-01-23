"""McDonald's menu models and data.

This module provides Pydantic v2 models for representing McDonald's menu items,
modifiers, and complete menu structure.
"""

from menus.mcdonalds.models import Item, Menu, Modifier

__all__ = ["Item", "Menu", "Modifier"]
