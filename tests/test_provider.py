"""Tests for AVPCredentialProvider."""

import pytest
from openclaw_avp import AVPCredentialProvider, Backend


class TestAVPCredentialProvider:
    """Test suite for AVPCredentialProvider."""

    def test_memory_backend(self):
        """Test with in-memory backend."""
        provider = AVPCredentialProvider(backend=Backend.MEMORY)

        # OpenClaw interface
        provider.set_credential("api_key", "test_value")
        assert provider.get_credential("api_key") == "test_value"
        assert provider.has_credential("api_key") is True

        # List
        creds = provider.list_credentials()
        assert "api_key" in creds

        # Delete
        assert provider.delete_credential("api_key") is True
        assert provider.has_credential("api_key") is False

        provider.close()

    def test_context_manager(self):
        """Test context manager usage."""
        with AVPCredentialProvider(backend=Backend.MEMORY) as provider:
            provider.set_credential("key", "value")
            assert provider.get_credential("key") == "value"

    def test_rotate_credential(self):
        """Test credential rotation."""
        provider = AVPCredentialProvider(backend=Backend.MEMORY)

        provider.set_credential("rotate_key", "v1")
        assert provider.get_credential("rotate_key") == "v1"

        provider.rotate_credential("rotate_key", "v2")
        assert provider.get_credential("rotate_key") == "v2"

        provider.close()
