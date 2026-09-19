"""GENIUS MCP Tools Registry"""

from .hear_sound import register_hear_sound
from .diagnose import register_diagnose
from .list_entities import register_list_entities
from .get_home_health import register_get_home_health
from .propose_action import register_propose_action
from .confirm_action import register_confirm_action
from .record_incident import register_record_incident


def register_all_tools(server):
    """Registers the seven GENIUS MCP tools onto the MCPServer instance."""
    register_hear_sound(server)
    register_diagnose(server)
    register_list_entities(server)
    register_get_home_health(server)
    register_propose_action(server)
    register_confirm_action(server)
    register_record_incident(server)
