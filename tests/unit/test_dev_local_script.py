import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


class DevLocalScriptUnitTests(unittest.TestCase):
    def _make_workspace(self, include_env: bool = True) -> tuple[Path, Path]:
        temp_dir = Path(tempfile.mkdtemp())
        root = temp_dir / "workspace"
        script_dir = root / "scripts"
        script_dir.mkdir(parents=True)

        source_script = Path("scripts/dev_local.sh").read_text()
        script_path = script_dir / "dev_local.sh"
        script_path.write_text(source_script)
        script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR)

        if include_env:
            (root / ".env.local").write_text(
                textwrap.dedent(
                    """
                    MCP_ENVIRONMENT=dev
                    MCP_SESSION_BACKEND=memory
                    MCP_SESSION_STORE_URL=
                    MCP_SESSION_CONNECTIVITY_MODEL=local_process
                    MCP_SESSION_DURABILITY_REQUIRED=false
                    HOST=127.0.0.1
                    PORT=8080
                    PYTHONPATH=src
                    LOCAL_REDIS_PORT=6379
                    """
                ).strip()
                + "\n"
            )

        return temp_dir, script_path

    def _make_fake_python(self, temp_dir: Path) -> Path:
        bin_dir = temp_dir / "bin"
        bin_dir.mkdir()
        fake_python = bin_dir / "python3"
        fake_python.write_text(
            textwrap.dedent(
                """
                #!/usr/bin/env bash
                env | sort > "${CAPTURE_ENV_FILE}"
                printf '%s\n' "$*" > "${CAPTURE_ARGS_FILE}"
                exit 0
                """
            ).strip()
            + "\n"
        )
        fake_python.chmod(fake_python.stat().st_mode | stat.S_IXUSR)
        return fake_python

    def test_missing_env_local_exits_with_guidance(self):
        temp_dir, script_path = self._make_workspace(include_env=False)

        completed = subprocess.run(
            ["bash", str(script_path)],
            cwd=script_path.parent.parent,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(".env.local", completed.stderr)
        self.assertIn("local runtime defaults", completed.stderr)

    def test_minimal_mode_preserves_memory_session_defaults(self):
        temp_dir, script_path = self._make_workspace()
        self._make_fake_python(temp_dir)
        env_file = temp_dir / "captured.env"
        args_file = temp_dir / "captured.args"

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{temp_dir / 'bin'}:{env.get('PATH', '')}",
                "CAPTURE_ENV_FILE": str(env_file),
                "CAPTURE_ARGS_FILE": str(args_file),
            }
        )

        completed = subprocess.run(
            ["bash", str(script_path)],
            cwd=script_path.parent.parent,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        captured_env = env_file.read_text()
        captured_args = args_file.read_text()
        self.assertIn("MCP_SESSION_BACKEND=memory", captured_env)
        self.assertIn("MCP_SESSION_CONNECTIVITY_MODEL=local_process", captured_env)
        self.assertIn("-m uvicorn mcp_server.cloud_run_entrypoint:app", captured_args)

    def test_hosted_mode_applies_redis_overrides(self):
        temp_dir, script_path = self._make_workspace()
        self._make_fake_python(temp_dir)
        env_file = temp_dir / "captured.env"
        args_file = temp_dir / "captured.args"

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{temp_dir / 'bin'}:{env.get('PATH', '')}",
                "CAPTURE_ENV_FILE": str(env_file),
                "CAPTURE_ARGS_FILE": str(args_file),
                "LOCAL_SESSION_MODE": "hosted",
            }
        )

        completed = subprocess.run(
            ["bash", str(script_path)],
            cwd=script_path.parent.parent,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        captured_env = env_file.read_text()
        self.assertIn("MCP_SESSION_BACKEND=redis", captured_env)
        self.assertIn("MCP_SESSION_STORE_URL=redis://127.0.0.1:6379/0", captured_env)
        self.assertIn("MCP_SESSION_CONNECTIVITY_MODEL=local_docker_compose", captured_env)
        self.assertIn("MCP_SESSION_DURABILITY_REQUIRED=true", captured_env)


if __name__ == "__main__":
    unittest.main()
