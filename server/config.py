"""
GENIUS Server Configuration
Spec: Model Context Protocol (MCP) 2025-11-25
Transport: Streamable HTTP & SSE Push
"""

from dataclasses import dataclass
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class MCPConfig:
    server_name: str = "genius"
    server_title: str = "GENIUS — Home World Model"
    server_version: str = "1.0.0"
    mcp_spec_version: str = "2025-11-25"
    transport: str = "Streamable HTTP"
    streamable_path: str = "/mcp"
    sse_events_path: str = "/events"
    host: str = os.getenv("GENIUS_HOST", "127.0.0.1")
    port: int = int(os.getenv("GENIUS_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # AWS Integration Settings
    aws_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    polly_voice_id: str = "Joanna"  # Neural Amazon Polly voice

    def to_dict(self) -> Dict[str, Any]:
        return {
            "server": {
                "name": self.server_name,
                "title": self.server_title,
                "version": self.server_version,
                "mcp_spec": self.mcp_spec_version,
            },
            "transports": {
                "mcp_streamable_http": f"http://{self.host}:{self.port}{self.streamable_path}",
                "sse_proactive_push": f"http://{self.host}:{self.port}{self.sse_events_path}",
            },
            "capabilities": {
                "tools": {
                    "listChanged": True,
                },
                "prompts": {
                    "listChanged": False,
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True,
                }
            }
        }


# Singleton loaded config instance
CONFIG = MCPConfig()
