"""GENIUS MCP Tools Registry"""

from .hear_sound import register_hear_sound
from .diagnose import register_diagnose
from .list_entities import register_list_entities
from .get_home_health import register_get_home_health
from .propose_action import register_propose_action
from .confirm_action import register_confirm_action
from .record_incident import register_record_incident
from .register_entity import register_register_entity
from .check_warranty import register_check_warranty
from .file_warranty_claim import register_file_warranty_claim
from .deliberate_repair import register_deliberate_repair


def register_all_tools(server):
    """Registers all GENIUS MCP tools onto the MCPServer instance."""
    # Core 7 Diagnostic & Safety Tools
    register_hear_sound(server)
    register_diagnose(server)
    register_list_entities(server)
    register_get_home_health(server)
    register_propose_action(server)
    register_confirm_action(server)
    register_record_incident(server)

    # Day 0 Onboarding & Warranties
    register_register_entity(server)
    register_check_warranty(server)
    register_file_warranty_claim(server)

    # AWS Builder Specialist Deliberation Panel
    register_deliberate_repair(server)
