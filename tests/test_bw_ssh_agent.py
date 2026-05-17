"""Tests for bw-ssh-agent.py"""

import importlib.util
import os
import signal
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Dynamically load the hyphenated module name
_module_path = Path(__file__).parent.parent / "bw-ssh-agent.py"
_spec = importlib.util.spec_from_file_location("bw_ssh_agent", str(_module_path))
bws = importlib.util.module_from_spec(_spec)
sys.modules["bw_ssh_agent"] = bws
_spec.loader.exec_module(bws)


class TestExecuteCommand:
    """Tests for _execute_command function."""

    def test_success(self, mocker):
        mock_popen = mocker.patch("subprocess.Popen")
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("stdout", "stderr")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        rc, out, err = bws._execute_command(["echo", "hello"])
        assert rc == 0
        assert out == "stdout"
        assert err == "stderr"

    def test_with_stdin(self, mocker):
        mock_popen = mocker.patch("subprocess.Popen")
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("out", "err")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        rc, out, err = bws._execute_command(["cat"], stdin="input")
        mock_proc.communicate.assert_called_once_with(input="input")


class TestAddSshKeyFromString:
    """Tests for add_ssh_key_from_string function."""

    def test_adds_newline(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (0, "Identity added", "")

        bws.add_ssh_key_from_string("key_without_newline")
        _, kwargs = mock_exec.call_args
        assert kwargs["stdin"] == "key_without_newline\n"

    def test_preserves_existing_newline(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (0, "Identity added", "")

        bws.add_ssh_key_from_string("key_with_newline\n")
        _, kwargs = mock_exec.call_args
        assert kwargs["stdin"] == "key_with_newline\n"

    def test_failure(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (1, "", "Error")

        with pytest.raises(subprocess.CalledProcessError):
            bws.add_ssh_key_from_string("key")


class TestGetBwSshKeys:
    """Tests for get_bw_ssh_keys function."""

    def test_returns_only_ssh_keys(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (
            0,
            '[{"type": 5, "sshKey": {"privateKey": "ssh-key-1"}},'
            ' {"type": 1, "sshKey": {"privateKey": "not-ssh"}}]',
            "",
        )

        keys = bws.get_bw_ssh_keys()
        assert keys == ["ssh-key-1"]

    def test_empty_output(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (0, "", "")

        with pytest.raises(Exception, match="empty output"):
            bws.get_bw_ssh_keys()

    def test_command_failure(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (1, "", "Error")

        with pytest.raises(subprocess.CalledProcessError):
            bws.get_bw_ssh_keys()


class TestGetAgentPid:
    """Tests for get_agent_pid function."""

    def test_returns_pid(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (0, "12345", "")

        pid = bws.get_agent_pid()
        assert pid == 12345

    def test_returns_none(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (0, "", "")

        pid = bws.get_agent_pid()
        assert pid is None


class TestGuessAgentSocket:
    """Tests for guess_agent_socket function."""

    def test_single_candidate(self, mocker):
        mock_glob = mocker.patch("glob.glob")
        mock_glob.return_value = ["/tmp/ssh-xxx/agent.42"]

        sock = bws.guess_agent_socket(43)
        assert sock == "/tmp/ssh-xxx/agent.42"

    def test_no_candidate(self, mocker):
        mock_glob = mocker.patch("glob.glob")
        mock_glob.return_value = []

        with pytest.raises(Exception, match="Could not guess"):
            bws.guess_agent_socket(43)

    def test_multiple_candidates(self, mocker):
        mock_glob = mocker.patch("glob.glob")
        mock_glob.return_value = ["/tmp/ssh-a/agent.42", "/tmp/ssh-b/agent.42"]

        with pytest.raises(Exception, match="Could not guess"):
            bws.guess_agent_socket(43)


class TestKillSshAgent:
    """Tests for kill_ssh_agent function."""

    def test_sends_sigterm(self, mocker):
        mock_kill = mocker.patch("os.kill")
        bws.kill_ssh_agent(12345)
        mock_kill.assert_called_once_with(12345, signal.SIGTERM)

    def test_handles_process_lookup_error(self, mocker):
        mock_kill = mocker.patch("os.kill", side_effect=ProcessLookupError)
        bws.kill_ssh_agent(12345)


class TestStartSshAgent:
    """Tests for start_ssh_agent function."""

    def test_parses_and_sets_env(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (
            0,
            "SSH_AUTH_SOCK=/tmp/ssh-xxx/agent.1234; export SSH_AUTH_SOCK;\n"
            "SSH_AGENT_PID=1234; export SSH_AGENT_PID;\n"
            "echo Agent pid 1234;",
            "",
        )

        mocker.patch.dict(os.environ, {}, clear=False)

        pid = bws.start_ssh_agent()
        assert pid == 1234
        assert os.environ["SSH_AUTH_SOCK"] == "/tmp/ssh-xxx/agent.1234"
        assert os.environ["SSH_AGENT_PID"] == "1234"

    def test_failure(self, mocker):
        mock_exec = mocker.patch.object(bws, "_execute_command")
        mock_exec.return_value = (1, "", "Error")

        with pytest.raises(subprocess.CalledProcessError):
            bws.start_ssh_agent()


class TestPrintEnvExports:
    """Tests for print_env_exports function."""

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/ssh-xxx/agent.1234")
        monkeypatch.setenv("SSH_AGENT_PID", "1234")

    def test_bash_output(self, capsys):
        bws.print_env_exports(1234, "bash")
        captured = capsys.readouterr()
        assert "export SSH_AUTH_SOCK=/tmp/ssh-xxx/agent.1234" in captured.out
        assert "export SSH_AGENT_PID=1234" in captured.out
        assert "Agent pid 1234" in captured.err

    def test_zsh_output(self, capsys):
        bws.print_env_exports(1234, "zsh")
        captured = capsys.readouterr()
        assert "export SSH_AUTH_SOCK=/tmp/ssh-xxx/agent.1234" in captured.out

    def test_fish_output(self, capsys):
        bws.print_env_exports(1234, "fish")
        captured = capsys.readouterr()
        assert "set -x SSH_AUTH_SOCK /tmp/ssh-xxx/agent.1234" in captured.out
        assert "set -x SSH_AGENT_PID 1234" in captured.out


class TestMain:
    """Integration-style tests for main function with mocked dependencies."""

    def test_bw_not_installed(self, mocker, monkeypatch):
        mocker.patch("shutil.which", return_value=None)
        monkeypatch.setattr(sys, "argv", ["bw-ssh-agent.py"])
        with pytest.raises(SystemExit) as exc_info:
            bws.main()
        assert exc_info.value.code == 1

    def test_bw_session_missing(self, mocker, monkeypatch):
        mocker.patch("shutil.which", return_value="/usr/bin/bw")
        monkeypatch.delenv("BW_SESSION", raising=False)
        monkeypatch.setattr(sys, "argv", ["bw-ssh-agent.py"])
        with pytest.raises(SystemExit) as exc_info:
            bws.main()
        assert exc_info.value.code == 1

    def test_agent_already_running_with_env(self, mocker, monkeypatch):
        mocker.patch("shutil.which", return_value="/usr/bin/bw")
        monkeypatch.setenv("BW_SESSION", "test")
        mocker.patch.object(bws, "get_agent_pid", return_value=1234)
        monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/ssh-xxx/agent.1234")
        monkeypatch.setenv("SSH_AGENT_PID", "1234")
        mocker.patch.object(bws, "get_bw_ssh_keys", return_value=[])
        mock_print = mocker.patch.object(bws, "print_env_exports")
        monkeypatch.setattr(sys, "argv", ["bw-ssh-agent.py"])

        bws.main()
        mock_print.assert_called_once_with(1234, "bash")

    def test_agent_already_running_guess_socket(self, mocker, monkeypatch):
        mocker.patch("shutil.which", return_value="/usr/bin/bw")
        monkeypatch.setenv("BW_SESSION", "test")
        mocker.patch.object(bws, "get_agent_pid", return_value=1234)
        monkeypatch.delenv("SSH_AUTH_SOCK", raising=False)
        monkeypatch.delenv("SSH_AGENT_PID", raising=False)
        mocker.patch.object(
            bws, "guess_agent_socket", return_value="/tmp/ssh-xxx/agent.1233"
        )
        mocker.patch.object(bws, "get_bw_ssh_keys", return_value=[])
        mock_print = mocker.patch.object(bws, "print_env_exports")
        monkeypatch.setattr(sys, "argv", ["bw-ssh-agent.py"])

        bws.main()
        assert os.environ["SSH_AUTH_SOCK"] == "/tmp/ssh-xxx/agent.1233"
        assert os.environ["SSH_AGENT_PID"] == "1234"
        mock_print.assert_called_once_with(1234, "bash")
