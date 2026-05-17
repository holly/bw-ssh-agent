#!/usr/bin/env python3

import argparse
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys

VERSION = "1.0.0"
SSH_AGENT_ENVIRON_KEYS = ["SSH_AUTH_SOCK", "SSH_AGENT_PID"]

# Bitwarden item type for SSH keys
BITWARDEN_TYPE_SSH_KEY = 5

parser = argparse.ArgumentParser(description="Parse command line options.")
parser.add_argument(
    "shell_type",
    type=str,
    nargs="?",
    metavar="bash or zsh or fish",
    default="bash",
    choices=["bash", "fish", "zsh"],
    help="using shell type. default bash",
)
parser.add_argument(
    "--version",
    "-v",
    action="version",
    version=f"%(prog)s {VERSION}",
    help="show version",
)
args = None


def _execute_command(cmds: list[str], stdin: str = None) -> tuple[int, str, str]:
    p = subprocess.Popen(
        cmds,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = p.communicate(input=stdin)
    return p.returncode, stdout.strip(), stderr.strip()


def add_ssh_key_from_string(ssh_key_string: str) -> str:
    # Ensure trailing newline — ssh-add may reject keys without it
    if not ssh_key_string.endswith("\n"):
        ssh_key_string += "\n"

    returncode, stdout, stderr = _execute_command(
        ["ssh-add", "-"], stdin=ssh_key_string
    )
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, "ssh-add", stdout, stderr)

    return stdout


def get_bw_ssh_keys() -> list[str]:
    returncode, stdout, stderr = _execute_command(["bw", "list", "items"])
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
    _, stdout, _ = _execute_command(
        ["pgrep", "-u", str(os.getuid()), "-x", "ssh-agent"]
    )
    if stdout:
        return int(stdout)
    return None


def guess_agent_socket(pid: int) -> str:
    candidates = glob.glob(f"/tmp/ssh-*/agent.{pid - 1}")
    if len(candidates) != 1:
        raise Exception(
            f"Could not guess SSH_AUTH_SOCK for running ssh-agent (pid {pid}). "
            f"Found {len(candidates)} candidate socket(s) for agent.{pid - 1}. "
            "Start a fresh shell or set SSH_AUTH_SOCK and SSH_AGENT_PID manually."
        )
    return candidates[0]


def kill_ssh_agent(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass


def start_ssh_agent() -> int:
    returncode, stdout, stderr = _execute_command(["ssh-agent", "-s"])

    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, "ssh-agent", stdout, stderr)

    # Parse ssh-agent output. Format (may vary by OS — depends on ssh-agent implementation):
    # SSH_AUTH_SOCK=/tmp/ssh-XXXXXXQ0VReG/agent.1234; export SSH_AUTH_SOCK;
    # SSH_AGENT_PID=1235; export SSH_AGENT_PID;
    # echo Agent pid 1235;
    for line in stdout.splitlines():
        kv = line.split(";")[0].strip()
        m = re.search(r"^(SSH_AUTH_SOCK|SSH_AGENT_PID)=(.*)$", kv)
        if not m:
            continue
        k = m.group(1)
        v = m.group(2)
        os.environ[k] = v

    return int(os.environ["SSH_AGENT_PID"])


def print_env_exports(agent_pid: int, shell_type: str) -> None:
    for k in SSH_AGENT_ENVIRON_KEYS:
        if shell_type in ("bash", "zsh"):
            print(f"export {k}={os.environ.get(k)}")
        elif shell_type == "fish":
            print(f"set -x {k} {os.environ.get(k)}")
    print(f"Agent pid {agent_pid}", file=sys.stderr)


def main() -> None:
    global args
    args = parser.parse_args()
    agent_pid: int | None = None
    agent_started = False

    try:
        if not shutil.which("bw"):
            raise Exception("bw (Bitwarden CLI) is not installed.")

        if not os.environ.get("BW_SESSION"):
            raise Exception(
                "Bitwarden vault is locked. Run: export BW_SESSION=$(bw unlock --raw)"
            )

        existing_pid = get_agent_pid()

        if existing_pid is not None:
            # Re-use running agent if possible
            if all(k in os.environ for k in SSH_AGENT_ENVIRON_KEYS):
                agent_pid = existing_pid
            else:
                # Try to guess the socket from /tmp and set env vars
                guessed_sock = guess_agent_socket(existing_pid)
                os.environ["SSH_AUTH_SOCK"] = guessed_sock
                os.environ["SSH_AGENT_PID"] = str(existing_pid)
                agent_pid = existing_pid
        else:
            for k in SSH_AGENT_ENVIRON_KEYS:
                if k in os.environ:
                    raise Exception(
                        f"ssh-agent environment variable already set: {k}={os.environ.get(k)}"
                    )

            agent_pid = start_ssh_agent()
            agent_started = True

        for ssh_key_string in get_bw_ssh_keys():
            add_ssh_key_from_string(ssh_key_string)

    except Exception as e:
        # Clean up the agent only if we started it before the error occurred
        if agent_started and agent_pid is not None:
            kill_ssh_agent(agent_pid)
        print(e, file=sys.stderr)
        sys.exit(1)

    print_env_exports(agent_pid, args.shell_type)


if __name__ == "__main__":
    main()
