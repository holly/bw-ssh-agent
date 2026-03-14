#!/usr/bin/env python3

import json
import os
import re
import shutil
import signal
import subprocess
import sys

SSH_AGENT_ENVIRON_KEYS = ["SSH_AUTH_SOCK", "SSH_AGENT_PID"]

# Bitwarden item type for SSH keys
BITWARDEN_TYPE_SSH_KEY = 5


def _execute_command(cmds: list[str], stdin: str = None) -> tuple[int, str, str]:

    p = subprocess.Popen(
        cmds,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = p.communicate(input=stdin)
    return p.returncode, stdout.strip(), stderr.strip()


def add_ssh_key_from_string(ssh_key_string: str) -> str:

    # Ensure trailing newline — ssh-add may reject keys without it
    if not ssh_key_string.endswith("\n"):
        ssh_key_string += "\n"

    returncode, stdout, stderr = _execute_command(["ssh-add", "-"], stdin=ssh_key_string)
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, "ssh-add", stdout, stderr)

    return stdout


def get_bw_ssh_keys() -> list[str]:

    returncode, stdout, stderr = _execute_command(['bw', 'list', 'items'])
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, "bw", stdout, stderr)

    if not stdout:
        raise Exception(f"bw list items returned empty output. {stderr}".strip())

    items = json.loads(stdout)
    keys = []
    for item in items:
        if item["type"] != BITWARDEN_TYPE_SSH_KEY:
            continue
        keys.append(item["sshKey"]["privateKey"])

    return keys


def get_agent_pid() -> int | None:

    # Scope to current user to avoid detecting other users' agents
    _, stdout, _ = _execute_command(['pgrep', '-u', str(os.getuid()), '-x', 'ssh-agent'])
    if stdout:
        return int(stdout)
    return None


def kill_ssh_agent(pid: int) -> None:

    os.kill(pid, signal.SIGTERM)


def start_ssh_agent() -> int:

    returncode, stdout, stderr = _execute_command(['ssh-agent', '-s'])

    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, "ssh-agent", stdout, stderr)

    # Parse ssh-agent output. Format (may vary by OS — depends on ssh-agent implementation):
    # SSH_AUTH_SOCK=/tmp/ssh-XXXXXXQ0VReG/agent.1234; export SSH_AUTH_SOCK;
    # SSH_AGENT_PID=1235; export SSH_AGENT_PID;
    # echo Agent pid 1235;
    for line in stdout.splitlines():
        kv = line.split(";")[0].strip()
        m = re.search(r'^(SSH_AUTH_SOCK|SSH_AGENT_PID)=(.*)$', kv)
        if not m:
            continue
        k = m.group(1)
        v = m.group(2)
        os.environ[k] = v

    return int(os.environ["SSH_AGENT_PID"])


def main() -> None:

    agent_pid: int | None = None

    try:
        if not shutil.which("bw"):
            raise Exception("bw (Bitwarden CLI) is not installed.")

        if not os.environ.get("BW_SESSION"):
            raise Exception(
                "Bitwarden vault is locked. Run: export BW_SESSION=$(bw unlock --raw)"
            )

        pid = get_agent_pid()
        if pid is not None:
            raise Exception(f"ssh-agent is already running. pid: {pid}")

        for k in SSH_AGENT_ENVIRON_KEYS:
            if k in os.environ:
                raise Exception(
                    f"ssh-agent environment variable already set: {k}={os.environ.get(k)}"
                )

        agent_pid = start_ssh_agent()

        for ssh_key_string in get_bw_ssh_keys():
            add_ssh_key_from_string(ssh_key_string)

    except Exception as e:
        # Clean up the agent if it was started before the error occurred
        if agent_pid is not None:
            kill_ssh_agent(agent_pid)
        print(e, file=sys.stderr)
        sys.exit(1)

    for k in SSH_AGENT_ENVIRON_KEYS:
        print(f"export {k}={os.environ.get(k)}")
    print(f"Agent pid {os.environ['SSH_AGENT_PID']}", file=sys.stderr)


if __name__ == "__main__":
    main()
