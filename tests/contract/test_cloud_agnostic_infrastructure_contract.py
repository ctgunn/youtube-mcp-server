import unittest
from pathlib import Path


class CloudAgnosticInfrastructureContractTests(unittest.TestCase):
    def test_shared_contract_defines_required_capabilities_and_outputs(self):
        content = Path(
            "specs/020-cloud-agnostic-iac/contracts/shared-platform-contract.md"
        ).read_text()
        for expected in (
            "Hosted runtime",
            "Network ingress",
            "Runtime identity",
            "Secret-backed runtime configuration",
            "Observability integration",
            "Durable shared session support",
            "application deployment model",
            "provider adapters must preserve one consistent application deployment model",
        ):
            self.assertIn(expected, content)

    def test_execution_mode_contract_preserves_local_first_boundaries(self):
        content = Path(
            "specs/020-cloud-agnostic-iac/contracts/execution-mode-contract.md"
        ).read_text()
        for expected in (
            "Minimal Local Runtime",
            "Hosted-Like Local Verification",
            "Hosted Deployment",
            "must not require provider provisioning",
            "provider adapter",
        ):
            self.assertIn(expected, content)

    def test_aws_adapter_contract_defines_mapping_outputs_and_limitations(self):
        content = Path(
            "specs/020-cloud-agnostic-iac/contracts/aws-provider-adapter-contract.md"
        ).read_text()
        for expected in (
            "planning-grade",
            "AWS App Runner",
            "AWS Secrets Manager",
            "Amazon ElastiCache for Redis",
            "partial or unsupported",
            "application deployment model",
        ):
            self.assertIn(expected, content)

    def test_data_model_tracks_capabilities_adapters_and_execution_modes(self):
        content = Path("specs/020-cloud-agnostic-iac/data-model.md").read_text()
        for expected in (
            "Shared Platform Contract",
            "Platform Capability",
            "Provider Adapter Module",
            "Capability Mapping",
            "Execution Mode",
            "minimal_local",
            "hosted_like_local",
            "hosted",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
