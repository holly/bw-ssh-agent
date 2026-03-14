# bw-ssh-agent

A script that automatically loads SSH keys stored in Bitwarden into `ssh-agent`.

## Overview

This script retrieves SSH private keys from your Bitwarden vault and registers them into a newly started `ssh-agent`. Designed to be used with `eval` so the agent's environment variables are applied to your current shell session.

## Requirements

- Python 3.10+
- [Bitwarden CLI (`bw`)](https://bitwarden.com/help/cli/)
- `ssh-agent` (included in OpenSSH)

## Setup

### 1. Install Bitwarden CLI

```bash
# macOS
brew install bitwarden-cli

# or via npm
npm install -g @bitwarden/cli
```

### 2. Login and unlock Bitwarden

```bash
bw login
export BW_SESSION=$(bw unlock --raw)
```

### 3. Store SSH keys in Bitwarden

Make sure your SSH keys are saved as **SSH Key** type items in your Bitwarden vault.

## Usage

```bash
eval $(python3 bw-ssh-agent.py)
```

This will:

1. Check that `bw` is installed and that no `ssh-agent` is already running
2. Start a new `ssh-agent`
3. Fetch all SSH keys (type: 5) from your Bitwarden vault
4. Register each key into the agent via `ssh-add`
5. Export `SSH_AUTH_SOCK` and `SSH_AGENT_PID` to your shell

## Notes

- If `ssh-agent` is already running, the script exits with an error to prevent duplicate agents.
- The Bitwarden vault must be unlocked (`BW_SESSION` set) before running.
- To automate on login, add the `eval` line to your `.bashrc` / `.zshrc`.

## License

MIT
