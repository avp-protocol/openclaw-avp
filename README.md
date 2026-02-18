<p align="center">
  <img src="https://raw.githubusercontent.com/avp-protocol/spec/main/assets/avp-shield.svg" alt="AVP Shield" width="80" />
</p>

<h1 align="center">openclaw-avp</h1>

<p align="center">
  <strong>OpenClaw credential provider integration for AVP</strong><br>
  Drop-in replacement · Same API · Hardware security
</p>

<p align="center">
  <a href="https://pypi.org/project/openclaw-avp/"><img src="https://img.shields.io/pypi/v/openclaw-avp?style=flat-square&color=00D4AA" alt="PyPI" /></a>
  <a href="https://github.com/avp-protocol/openclaw-avp/actions"><img src="https://img.shields.io/github/actions/workflow/status/avp-protocol/openclaw-avp/ci.yml?style=flat-square" alt="CI" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-blue?style=flat-square" alt="License" /></a>
</p>

---

## Overview

`openclaw-avp` implements OpenClaw's credential provider interface using the Agent Vault Protocol. Replace OpenClaw's default `keys.json` with AVP — get hardware-grade security without changing your agent code.

## Installation

```bash
pip install openclaw-avp
```

## Quick Start

```python
from openclaw import Agent
from openclaw_avp import AVPCredentialProvider

# Create AVP-backed credential provider
credentials = AVPCredentialProvider("avp.toml")

# Use with OpenClaw agent
agent = Agent(credential_provider=credentials)

# Secrets are now stored in AVP vault instead of ~/.openclaw/keys.json
agent.run()
```

## Migration from Default Provider

```bash
# Export existing credentials
openclaw credentials export > credentials.json

# Import into AVP
avp import credentials.json --backend keychain

# Update openclaw config
openclaw config set credential_provider avp
openclaw config set avp.config avp.toml

# Clean up
rm credentials.json
rm ~/.openclaw/keys.json  # Remove old plaintext secrets
```

## Configuration

### openclaw.toml

```toml
[credentials]
provider = "avp"
config = "avp.toml"
```

### avp.toml

```toml
[backend]
type = "keychain"  # or "file", "hardware", "remote"

[workspace]
name = "openclaw-default"
```

## Backend Selection

```python
from openclaw_avp import AVPCredentialProvider, Backend

# OS Keychain (recommended)
credentials = AVPCredentialProvider(backend=Backend.KEYCHAIN)

# Hardware secure element (maximum security)
credentials = AVPCredentialProvider(backend=Backend.HARDWARE, device="/dev/ttyUSB0")

# Remote vault (team environments)
credentials = AVPCredentialProvider(
    backend=Backend.REMOTE,
    url="https://vault.company.com"
)
```

## API Compatibility

`AVPCredentialProvider` implements the full OpenClaw credential interface:

| Method | AVP Operation |
|--------|---------------|
| `get_credential(key)` | RETRIEVE |
| `set_credential(key, value)` | STORE |
| `delete_credential(key)` | DELETE |
| `list_credentials()` | LIST |

## Security Comparison

| Provider | Infostealer | Host Compromise | Memory Dump |
|----------|:-----------:|:---------------:|:-----------:|
| OpenClaw default (keys.json) | ✗ | ✗ | ✗ |
| AVP File | ✗ | ✗ | ✗ |
| AVP Keychain | ✓ | ✗ | ✗ |
| AVP Hardware | ✓ | ✓ | ✓ |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

<p align="center">
  <a href="https://github.com/avp-protocol/spec">AVP Specification</a> ·
  <a href="https://github.com/openclaw/openclaw">OpenClaw</a>
</p>
