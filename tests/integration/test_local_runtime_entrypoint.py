import unittest
from pathlib import Path


class LocalRuntimeEntrypointIntegrationTests(unittest.TestCase):
    def test_local_guide_promotes_script_as_canonical_local_entrypoint(self):
        """Require local guidance to name the repository-owned entry point.

        :return: ``None`` after checking the local runtime procedure.
        """
        content = Path("docs/local-development.md").read_text()
        self.assertIn("bash scripts/dev_local.sh", content)
        self.assertIn(".env.local", content)
        self.assertIn("local runtime defaults", content)
        self.assertIn("Local MCP verification", content)

    def test_local_guide_keeps_minimal_local_outside_cloud_prerequisites(self):
        """Require local guidance to keep cloud setup out of the fast path.

        :return: ``None`` after checking the minimal local boundary.
        """
        content = Path("docs/local-development.md").read_text()
        self.assertIn("Minimal local runtime path", content)
        self.assertIn("does not require cloud provisioning", content)
        self.assertIn("hosted deployment", content)

    def test_local_files_distinguish_baseline_defaults_from_hosted_like_overrides(self):
        """Use the tracked baseline template instead of private local config.

        :return: ``None`` after checking local and hosted-like example boundaries.
        """
        env_local = Path(".env.local.example").read_text()
        local_env_example = Path("infrastructure/local/.env.example").read_text()
        self.assertIn("Baseline local runtime defaults", env_local)
        self.assertIn("Hosted-like local overrides", env_local)
        self.assertIn("LOCAL_SESSION_MODE=hosted", local_env_example)
        self.assertIn("override values for hosted-like local verification only", local_env_example)


if __name__ == "__main__":
    unittest.main()
