"""AVP Credential Provider for OpenClaw."""

from typing import Optional, Dict, List, Any
from pathlib import Path
import getpass

from avp import AVPClient
from avp.backends import FileBackend, MemoryBackend

from openclaw_avp.backend import Backend


class AVPCredentialProvider:
    """
    OpenClaw credential provider that uses AVP for secure storage.

    Drop-in replacement for OpenClaw's default keys.json storage.
    Provides encrypted credential storage with hardware security support.

    Example:
        >>> from openclaw import Agent
        >>> from openclaw_avp import AVPCredentialProvider
        >>>
        >>> credentials = AVPCredentialProvider("avp.toml")
        >>> agent = Agent(credential_provider=credentials)
        >>> agent.run()
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        backend: Backend = Backend.FILE,
        vault_path: Optional[str] = None,
        password: Optional[str] = None,
        device: Optional[str] = None,
        url: Optional[str] = None,
        workspace: str = "openclaw",
    ):
        """
        Initialize the AVP credential provider.

        Args:
            config_path: Path to AVP config file (avp.toml).
            backend: Backend type (FILE, KEYCHAIN, HARDWARE, REMOTE).
            vault_path: Path to vault file (for FILE backend).
            password: Vault password (will prompt if not provided).
            device: Device path (for HARDWARE backend).
            url: Remote URL (for REMOTE backend).
            workspace: AVP workspace name.
        """
        self._workspace = workspace
        self._client: Optional[AVPClient] = None
        self._session_id: Optional[str] = None

        # Initialize backend
        if backend == Backend.MEMORY:
            self._backend = MemoryBackend()
        elif backend == Backend.FILE:
            vault = vault_path or str(Path.home() / ".openclaw" / "avp_vault.enc")
            if password is None:
                password = getpass.getpass(f"Enter AVP vault password: ")
            Path(vault).parent.mkdir(parents=True, exist_ok=True)
            self._backend = FileBackend(vault, password)
        elif backend == Backend.KEYCHAIN:
            raise NotImplementedError("Keychain backend coming soon")
        elif backend == Backend.HARDWARE:
            raise NotImplementedError("Hardware backend coming soon")
        elif backend == Backend.REMOTE:
            raise NotImplementedError("Remote backend coming soon")
        else:
            raise ValueError(f"Unknown backend: {backend}")

        self._connect()

    def _connect(self):
        """Connect to AVP vault."""
        self._client = AVPClient(self._backend)
        session = self._client.authenticate(workspace=self._workspace)
        self._session_id = session.session_id

    def get_credential(self, key: str) -> Optional[str]:
        """
        Get a credential by key.

        OpenClaw credential provider interface.

        Args:
            key: Credential key name.

        Returns:
            Credential value or None.
        """
        try:
            result = self._client.retrieve(self._session_id, key)
            return result.value.decode()
        except Exception:
            return None

    def set_credential(self, key: str, value: str) -> None:
        """
        Store a credential.

        OpenClaw credential provider interface.

        Args:
            key: Credential key name.
            value: Credential value.
        """
        self._client.store(self._session_id, key, value.encode())

    def delete_credential(self, key: str) -> bool:
        """
        Delete a credential.

        OpenClaw credential provider interface.

        Args:
            key: Credential key name.

        Returns:
            True if deleted.
        """
        result = self._client.delete(self._session_id, key)
        return result.deleted

    def list_credentials(self) -> List[str]:
        """
        List all credential keys.

        OpenClaw credential provider interface.

        Returns:
            List of credential key names.
        """
        result = self._client.list_secrets(self._session_id)
        return [s.name for s in result.secrets]

    def has_credential(self, key: str) -> bool:
        """
        Check if a credential exists.

        Args:
            key: Credential key name.

        Returns:
            True if exists.
        """
        return key in self.list_credentials()

    def rotate_credential(self, key: str, new_value: str) -> None:
        """
        Rotate a credential with version tracking.

        Args:
            key: Credential key name.
            new_value: New credential value.
        """
        self._client.rotate(self._session_id, key, new_value.encode())

    def close(self):
        """Close the vault connection."""
        if self._client:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def migrate_from_keys_json(
    keys_json_path: str,
    provider: AVPCredentialProvider,
    delete_source: bool = False,
) -> int:
    """
    Migrate credentials from OpenClaw keys.json to AVP.

    Args:
        keys_json_path: Path to keys.json file.
        provider: AVPCredentialProvider instance.
        delete_source: Whether to delete keys.json after migration.

    Returns:
        Number of credentials migrated.
    """
    import json

    path = Path(keys_json_path)
    if not path.exists():
        return 0

    with open(path) as f:
        keys = json.load(f)

    count = 0
    for key, value in keys.items():
        if isinstance(value, str):
            provider.set_credential(key, value)
            count += 1

    if delete_source:
        # Secure delete: overwrite then remove
        with open(path, "wb") as f:
            f.write(b"\x00" * path.stat().st_size)
        path.unlink()

    return count
