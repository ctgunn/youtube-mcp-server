import unittest
from pathlib import Path


class LocalRuntimeEntrypointIntegrationTests(unittest.TestCase):
    def test_readme_promotes_script_as_canonical_local_entrypoint(self):
        content = Path("README.md").read_text()
        self.assertIn("bash scripts/dev_local.sh", content)
        self.assertIn(".env.local", content)
        self.assertIn("local runtime defaults", content)
        self.assertIn("Local runtime verification", content)

    def test_readme_keeps_minimal_local_outside_cloud_prerequisites(self):
        content = Path("README.md").read_text()
        self.assertIn("Minimal local runtime path", content)
        self.assertIn("does not require cloud provisioning", content)
        self.assertIn("Hosted deployment-only inputs", content)

    def test_local_files_distinguish_baseline_defaults_from_hosted_like_overrides(self):
        env_local = Path(".env.local").read_text()
        local_env_example = Path("infrastructure/local/.env.example").read_text()
        self.assertIn("Baseline local runtime defaults", env_local)
        self.assertIn("Hosted-like local overrides", env_local)
        self.assertIn("LOCAL_SESSION_MODE=hosted", local_env_example)
        self.assertIn("override values for hosted-like local verification only", local_env_example)


if __name__ == "__main__":
    unittest.main()
