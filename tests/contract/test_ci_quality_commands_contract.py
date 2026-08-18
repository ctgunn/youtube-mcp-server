"""Contract coverage for the repository quality-command surface."""

from pathlib import Path
import unittest


class CiQualityCommandsContractTests(unittest.TestCase):
    """Verify the declared development toolchain and canonical Make commands."""

    def test_project_declares_quality_tooling_and_typecheck_scope(self):
        """Require reproducible dev tools and an explicit mypy source baseline.

        :return: ``None`` after validating the checked-in project configuration.
        :raises AssertionError: If required quality tools or configuration are absent.
        """
        content = Path("pyproject.toml").read_text()

        self.assertIn("dev", content)
        self.assertIn("pytest", content)
        self.assertIn("ruff", content)
        self.assertIn("mypy", content)
        self.assertIn("[tool.mypy]", content)
        self.assertIn("src/mcp_server", content)

    def test_makefile_exposes_all_canonical_quality_commands(self):
        """Require individual and combined quality targets.

        :return: ``None`` after validating Makefile command targets.
        :raises AssertionError: If a required target or command is absent.
        """
        content = Path("Makefile").read_text()

        for target, command in (
            ("lint:", "$(PYTHON) -m ruff check ."),
            ("typecheck:", "$(PYTHON) -m mypy src/mcp_server"),
            ("test:", "$(PYTHON) -m pytest"),
            ("quality:", "$(MAKE) lint"),
        ):
            self.assertIn(target, content)
            self.assertIn(command, content)


if __name__ == "__main__":
    unittest.main()
