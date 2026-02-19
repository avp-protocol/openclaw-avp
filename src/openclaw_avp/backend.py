"""Backend enum for OpenClaw-AVP."""

from enum import Enum


class Backend(Enum):
    """AVP backend types for OpenClaw."""

    FILE = "file"
    KEYCHAIN = "keychain"
    HARDWARE = "hardware"
    REMOTE = "remote"
    MEMORY = "memory"
