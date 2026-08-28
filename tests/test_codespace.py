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
    "configure_context",
    ROOT / ".devcontainer" / "scripts" / "configure_context.py",
)
resolve_tenant = load_module(
    "resolve_tenant",
    ROOT / ".devcontainer" / "scripts" / "resolve_tenant.py",
)
configure_copilot = load_module(
    "configure_copilot",
    ROOT / ".devcontainer" / "scripts" / "configure_copilot.py",
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
            ROOT / ".devcontainer" / "scripts" / "install-tools.sh"
        ).read_text()
        self.assertIn(
            'fab" config set encryption_fallback_enabled true',
            script,
        )

    def test_shared_tools_are_installed_during_prebuild(self):
        devcontainer = json.loads(
            (ROOT / ".devcontainer" / "devcontainer.json").read_text()
        )
        self.assertEqual(
            devcontainer["onCreateCommand"],
            "bash .devcontainer/scripts/install-tools.sh",
        )
        post_create = (
            ROOT / ".devcontainer" / "scripts" / "post-create.sh"
        ).read_text()
        self.assertNotIn("pip install", post_create)
        self.assertNotIn("npm install", post_create)

    def test_fabric_mcp_is_registered_for_copilot_cli(self):
        devcontainer = json.loads(
            (ROOT / ".devcontainer" / "devcontainer.json").read_text()
        )
        self.assertNotIn("FABRIC_MCP_VERSION", devcontainer["containerEnv"])

        install_tools = (
            ROOT / ".devcontainer" / "scripts" / "install-tools.sh"
        ).read_text()
        self.assertIn("@microsoft/fabric-mcp@latest", install_tools)

        mcp_config = json.loads(
            (ROOT / ".github" / "mcp.json").read_text()
        )
        fabric = mcp_config["mcpServers"]["fabric"]
        self.assertEqual(fabric["type"], "stdio")
        self.assertEqual(fabric["command"], "fabmcp")
        self.assertEqual(
            fabric["args"],
            ["server", "start", "--mode", "all"],
        )
        self.assertEqual(fabric["tools"], ["*"])

    def test_every_installed_extension_has_documented_rationale(self):
        devcontainer = json.loads(
            (ROOT / ".devcontainer" / "devcontainer.json").read_text()
        )
        rationale = (ROOT / "guidance" / "organizer-setup.md").read_text()
        for extension in devcontainer["customizations"]["vscode"]["extensions"]:
            with self.subTest(extension=extension):
                self.assertIn(f"`{extension}`", rationale)

    def test_copilot_cli_profile_opens_in_terminal_editor(self):
        devcontainer = json.loads(
            (ROOT / ".devcontainer" / "devcontainer.json").read_text()
        )
        settings = devcontainer["customizations"]["vscode"]["settings"]
        self.assertEqual(
            settings["terminal.integrated.defaultLocation"],
            "editor",
        )
        copilot_profile = settings["terminal.integrated.profiles.linux"][
            "Copilot CLI"
        ]
        self.assertEqual(copilot_profile["path"], "/bin/bash")
        self.assertEqual(copilot_profile["args"], ["-lc", "exec copilot"])

    def test_bash_terminals_load_shared_fabric_authentication(self):
        devcontainer = json.loads(
            (ROOT / ".devcontainer" / "devcontainer.json").read_text()
        )
        self.assertEqual(
            devcontainer["containerEnv"]["BASH_ENV"],
            "${containerWorkspaceFolder}/.devcontainer/scripts/fabric-shell-env.sh",
        )
        post_create = (
            ROOT / ".devcontainer" / "scripts" / "post-create.sh"
        ).read_text()
        self.assertIn("configure-shell.sh", post_create)

    def test_shell_authentication_refreshes_without_storing_tokens(self):
        shell_env = (
            ROOT / ".devcontainer" / "scripts" / "fabric-shell-env.sh"
        ).read_text()
        self.assertIn("az account get-access-token", shell_env)
        self.assertIn('export FAB_TOKEN="${fabric_token}"', shell_env)
        login = (
            ROOT / ".devcontainer" / "scripts" / "fabric-login.sh"
        ).read_text()
        self.assertIn('auth_config_dir}/tenant-id"', login)

    def test_copilot_trust_preserves_existing_configuration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / ".copilot" / "config.json"
            config_path.parent.mkdir()
            config_path.write_text(
                json.dumps(
                    {
                        "theme": "dark",
                        "trustedFolders": ["/workspaces/existing"],
                    }
                ),
                encoding="utf-8",
            )

            self.assertTrue(
                configure_copilot.add_trusted_folder(config_path, root)
            )
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["theme"], "dark")
            self.assertEqual(
                config["trustedFolders"],
                ["/workspaces/existing", str(root.resolve())],
            )
            self.assertFalse(
                configure_copilot.add_trusted_folder(config_path, root)
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

    def test_workshop_context_uses_rbac_and_live_confirmation(self):
        context_file = self.context_dir / "workshop-context.md"
        configure.write_context(self.multi_amc, context_file)
        context = context_file.read_text()
        self.assertIn("Multi-AMC Hack Modeling", context)
        self.assertIn("PHI", context)
        self.assertIn("Fabric RBAC", context)
        self.assertIn("Wait for explicit participant confirmation", context)

    def test_generated_copilot_instructions_include_protected_workspaces(self):
        instructions = self.context_dir / "workshop.instructions.md"
        configure.write_copilot_instructions(self.multi_amc, instructions)
        content = instructions.read_text()
        self.assertIn('applyTo: "**"', content)
        self.assertIn("Multi-AMC Hack Modeling", content)
        self.assertIn("PHI", content)
        self.assertIn("live Fabric context", content)

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


if __name__ == "__main__":
    unittest.main()
