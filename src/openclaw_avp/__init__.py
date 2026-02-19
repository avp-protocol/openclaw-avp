"""OpenClaw credential provider using Agent Vault Protocol."""

from openclaw_avp.provider import AVPCredentialProvider
from openclaw_avp.backend import Backend

__all__ = [
    "AVPCredentialProvider",
    "Backend",
]

__version__ = "0.1.0"
