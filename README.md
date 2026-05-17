# bw-ssh-agent

[![Tests](https://github.com/holly/bw-ssh-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/holly/bw-ssh-agent/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A script that automatically loads SSH keys stored in Bitwarden into `ssh-agent`.

## Overview

This script retrieves SSH private keys from your Bitwarden vault and registers them into a newly started `ssh-agent`. Designed to be used with `eval` so the agent's environment variables are applied to your current shell session.

## Requirements

- Python 3.15+
- [Bitwarden CLI (`bw`)](https://bitwarden.com/help/cli/)
- `ssh-agent` (included in OpenSSH)
- `uv` (Python package manager)

## Setup

### 1. Install dependencies

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Bitwarden CLI
brew install bitwarden-cli
# or: npm install -g @bitwarden/cli
```

### 2. Login and unlock Bitwarden

```bash
bw login
export BW_SESSION=$(bw unlock --raw)
```

### 3. Store SSH keys in Bitwarden

Make sure your SSH keys are saved as **SSH Key** type items in your Bitwarden vault.

## Command Line Options

```bash
uv run python bw-ssh-agent.py [shell_type] [--version|-v]
```

### Arguments

| Argument | Required | Default | Choices | Description |
|----------|----------|---------|---------|-------------|
| `shell_type` | Optional | `bash` | `bash`, `zsh`, `fish` | Output shell format |

### Options

| Option | Description |
|--------|-------------|
| `--version`, `-v` | Show version information and exit |

### Examples

```bash
# bash (default)
uv run python bw-ssh-agent.py

# zsh
uv run python bw-ssh-agent.py zsh

# fish
uv run python bw-ssh-agent.py fish

# Version check
uv run python bw-ssh-agent.py --version
```

## Behavior and Processing Flow

### Startup Checks

1. **Check Bitwarden CLI (`bw`)**
   - Exits with error if not installed

2. **Check Bitwarden session**
   - Verifies `BW_SESSION` environment variable
   - Exits with error if not set (prompts to run `bw unlock --raw`)

3. **Check existing `ssh-agent`**

   | Condition | Behavior |
   |-----------|----------|
   | No process, no env vars | Starts new `ssh-agent` |
   | Process exists, env vars set | Reuses existing agent |
   | Process exists, no env vars | Guesses `/tmp/ssh-*/agent.{pid-1}` |
   | Process exists, guess failed | Exits with error |

### Key Registration

- Fetches **type = 5 (SSH Key)** items from Bitwarden vault
- Registers each private key via `ssh-add -`
- Automatically appends trailing newline if missing

### Output

Exports environment variables in the specified shell format:

```bash
# bash / zsh
export SSH_AUTH_SOCK=/tmp/ssh-XXXXXX/agent.1234
export SSH_AGENT_PID=1234

# fish
set -x SSH_AUTH_SOCK /tmp/ssh-XXXXXX/agent.1234
set -x SSH_AGENT_PID 1234
```

**Note**: Wrap with `eval` to apply to current shell:

```bash
eval $(uv run python bw-ssh-agent.py)
```

## Troubleshooting

### ssh-agent is already running
- **Cause**: Existing `ssh-agent` detected but env vars missing and socket guess failed
- **Solution**: Kill existing process with `ssh-agent -k` or set env vars manually

### Could not guess SSH_AUTH_SOCK
- **Cause**: Failed to guess `/tmp/ssh-*/agent.{pid-1}` (0 or multiple candidates)
- **Solution**: Start a fresh shell or set `SSH_AUTH_SOCK` and `SSH_AGENT_PID` manually

### Bitwarden vault is locked
- **Cause**: `BW_SESSION` environment variable not set
- **Solution**: Run `export BW_SESSION=$(bw unlock --raw)`

## Development

### Running Tests

```bash
uv run pytest -v
```

### Version Management

`pyproject.toml` and `bw-ssh-agent.py` VERSION must match.
`/git-publish` command automatically checks consistency and tags releases.

## License

MIT
