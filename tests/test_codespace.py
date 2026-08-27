import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


configure = load_module(
    "configure_workspace",
    ROOT / ".devcontainer" / "scripts" / "configure_workspace.py",
)
verify = load_module(
    "verify_workspace_response",
    ROOT / ".devcontainer" / "scripts" / "verify_workspace_response.py",
)
resolve_tenant = load_module(
    "resolve_tenant",
    ROOT / ".devcontainer" / "scripts" / "resolve_tenant.py",
)


class DevcontainerConfigurationTests(unittest.TestCase):
    def test_github_cli_is_installed(self):
        devcontainer = json.loads(
            (ROOT / ".devcontainer" / "devcontainer.json").read_text()
        )
        self.assertIn(
            "ghcr.io/devcontainers/features/github-cli:1",
            devcontainer["features"],
        )

    def test_fabric_login_uses_cli_token_audience(self):
        script = (
            ROOT / ".devcontainer" / "scripts" / "fabric-login.sh"
        ).read_text()
        self.assertIn(
            "--resource https://analysis.windows.net/powerbi/api",
            script,
        )
        self.assertNotIn("--resource https://api.fabric.microsoft.com", script)

    def test_fabric_login_requires_devcontainer(self):
        script = (
            ROOT / ".devcontainer" / "scripts" / "fabric-login.sh"
        ).read_text()
        self.assertIn("must run inside the workshop devcontainer", script)
        self.assertIn("Fabric: Sign in again", script)

    def test_fabric_cli_encryption_fallback_is_configured(self):
        script = (
            ROOT / ".devcontainer" / "scripts" / "post-create.sh"
        ).read_text()
        self.assertIn(
            'fab" config set encryption_fallback_enabled true',
            script,
        )

    def test_tenant_domain_is_resolved_from_openid_metadata(self):
        self.assertEqual(
            resolve_tenant.tenant_id_from_metadata(
                {
                    "authorization_endpoint": (
                        "https://login.microsoftonline.com/"
                        "11111111-2222-3333-4444-555555555555/oauth2/authorize"
                    )
                }
            ),
            "11111111-2222-3333-4444-555555555555",
        )

    def test_work_email_is_normalized_to_domain(self):
        self.assertEqual(
            resolve_tenant.normalize_domain(" Participant@Contoso.com "),
            "contoso.com",
        )

    def test_invalid_tenant_domain_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "valid work email"):
            resolve_tenant.normalize_domain("not a domain")

    def test_noncommercial_tenant_authority_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "commercial"):
            resolve_tenant.tenant_id_from_metadata(
                {
                    "authorization_endpoint": (
                        "https://login.microsoftonline.us/"
                        "11111111-2222-3333-4444-555555555555/oauth2/authorize"
                    )
                }
            )


class WorkshopConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.generic = configure.load_config(
            ROOT / ".codespace" / "workshop.json"
        )
        self.multi_amc = configure.load_config(
            ROOT / ".codespace" / "multi-amc-workshop.json"
        )
        self.temp_dir = tempfile.TemporaryDirectory()
        self.context_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_configuration_is_ready_to_use(self):
        result = configure.configure_workspace(
            self.generic, self.context_dir, "Team Workspace"
        )
        self.assertEqual(result, "Team Workspace")
        status = configure.configure_workspace(
            self.generic, self.context_dir, ""
        )
        self.assertEqual(status, "UNCONFIGURED")
        context = (self.context_dir / "team-context.md").read_text()
        self.assertIn("Codespace: Configure team workspace", context)

    def test_multi_amc_profile_preserves_protected_workspaces(self):
        with self.assertRaisesRegex(ValueError, "is protected"):
            configure.configure_workspace(
                self.multi_amc, self.context_dir, "multi-amc hack"
            )

    def test_configured_workspace_generates_complete_context(self):
        result = configure.configure_workspace(
            self.multi_amc, self.context_dir, "Readmissions Team"
        )
        self.assertEqual(result, "Readmissions Team")
        self.assertEqual(
            (self.context_dir / "team-workspace-name").read_text(),
            "Readmissions Team\n",
        )
        context = (self.context_dir / "team-context.md").read_text()
        self.assertIn("Multi-AMC Hack Modeling", context)
        self.assertIn("PHI", context)
        self.assertIn("Readmissions Team", context)

    def test_workspace_name_pattern_is_enforced(self):
        config = copy.deepcopy(self.multi_amc)
        config["workspace"]["namePattern"] = r"^Team [0-9]+$"
        config["workspace"]["namePatternDescription"] = "Use Team followed by a number."
        with self.assertRaisesRegex(ValueError, "Use Team followed"):
            configure.configure_workspace(config, self.context_dir, "Readmissions")

    def test_generated_copilot_instructions_include_protected_workspaces(self):
        instructions = self.context_dir / "workshop.instructions.md"
        configure.write_copilot_instructions(self.multi_amc, instructions)
        content = instructions.read_text()
        self.assertIn('applyTo: "**"', content)
        self.assertIn("Multi-AMC Hack Modeling", content)
        self.assertIn("PHI", content)

    def test_invalid_configuration_is_rejected(self):
        path = self.context_dir / "invalid.json"
        path.write_text(json.dumps({"schemaVersion": 1}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "workshopName must be"):
            configure.load_config(path)

    def test_unexpected_configuration_field_is_rejected(self):
        path = self.context_dir / "invalid.json"
        invalid = copy.deepcopy(self.multi_amc)
        invalid["typo"] = True
        path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unexpected configuration"):
            configure.load_config(path)

    def test_markdown_code_span_handles_backticks(self):
        self.assertEqual(configure._code_span("Team `One`"), "`` Team `One` ``")


class WorkspaceResponseTests(unittest.TestCase):
    def test_exact_workspace_is_accepted(self):
        response = {
            "status": "Success",
            "result": {
                "data": {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "displayName": "Team 1",
                }
            },
        }
        self.assertEqual(
            verify.exact_workspace(response, "Team 1"),
            ("Team 1", "11111111-1111-1111-1111-111111111111"),
        )

    def test_substring_workspace_is_rejected(self):
        response = {
            "status": "Success",
            "result": {
                "data": {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "displayName": "Team 10",
                }
            },
        }
        with self.assertRaisesRegex(ValueError, "not 'Team 1'"):
            verify.exact_workspace(response, "Team 1")

    def test_failed_response_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "successful"):
            verify.exact_workspace({"status": "Failure"}, "Team 1")


if __name__ == "__main__":
    unittest.main()
