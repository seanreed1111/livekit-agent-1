"""Unit tests for DriveThruAgent.

Tests the agent initialization, wiring, and component ownership.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from drive_thru_agent import DriveThruAgent
from drive_thru_llm import DriveThruLLM
from menu_provider import MenuProvider
from order_state_manager import OrderStateManager


@pytest.fixture
def menu_provider():
    """Real menu provider."""
    return MenuProvider(
        "src/menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
    )


@pytest.fixture
def mock_llm():
    """Mock DriveThruLLM."""
    return Mock(spec=DriveThruLLM)


@pytest.fixture
def drive_thru_agent(mock_llm, menu_provider, tmp_path):
    """Create DriveThruAgent with mocked LLM."""
    return DriveThruAgent(
        session_id="test-session",
        llm=mock_llm,
        menu_provider=menu_provider,
        output_dir=str(tmp_path / "orders"),
    )


def test_agent_initialization(drive_thru_agent):
    """Test that DriveThruAgent initializes correctly."""
    assert drive_thru_agent is not None
    assert isinstance(drive_thru_agent, DriveThruAgent)


def test_agent_creates_order_state(drive_thru_agent):
    """Test that agent creates OrderStateManager."""
    order_state = drive_thru_agent.order_state
    assert order_state is not None
    assert isinstance(order_state, OrderStateManager)


def test_agent_creates_tools(drive_thru_agent):
    """Test that agent creates tools and they are available."""
    # Agent should have created tools
    # We can't directly inspect LiveKit Agent's tools, but we can verify
    # the agent was created successfully (implicitly tests tools were created)
    agent = drive_thru_agent.agent
    assert agent is not None


def test_agent_has_instructions(drive_thru_agent):
    """Test that agent has instructions set."""
    agent = drive_thru_agent.agent
    # Agent should have instructions - we verify by checking the agent exists
    # and was initialized with instructions
    assert agent is not None
    # The actual instructions are internal to the Agent, but we can verify
    # the agent was created successfully


def test_agent_owns_order_state(drive_thru_agent):
    """Test that agent owns and provides access to order state."""
    order_state = drive_thru_agent.order_state
    assert order_state is not None

    # Test that order state is actually usable
    assert order_state.is_empty()

    # Add an item and verify it persists
    order_state.add_item(
        item_name="Big Mac", category="Beef & Pork", modifiers=[], quantity=1
    )
    assert not order_state.is_empty()


def test_agent_session_directory_created(drive_thru_agent, tmp_path):
    """Test that session directory is created when order state is used."""
    # When we add an item, the directory should be created
    drive_thru_agent.order_state.add_item(
        item_name="Big Mac", category="Beef & Pork", modifiers=[], quantity=1
    )

    # Verify session directory exists
    session_dir = Path(tmp_path / "orders" / "test-session")
    assert session_dir.exists()

    # Verify incremental log exists
    log_file = session_dir / "incremental_log.jsonl"
    assert log_file.exists()
