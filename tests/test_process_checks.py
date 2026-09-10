"""Positive and negative consumer-contract tests using synthetic artifacts."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_process import (
    ValidationError, check_repository, read_yaml, validate_issue_form,
    validate_ruleset, validate_skill, validate_workflow,
)


FORM = {
    "name": "Synthetic task", "description": "A synthetic form",
    "body": [{"type": "textarea", "id": "goal", "attributes": {"label": "Goal"},
              "validations": {"required": True}}],
}
WORKFLOW = {
    "name": "Process checks",
    "on": {"pull_request": {"branches": ["main"]}, "push": {"branches": ["main"]}},
    "permissions": {"contents": "read"},
    "jobs": {"process": {"steps": [{"uses": "example/action@" + "a" * 40}, {"run": "check"}]}},
}


class YamlTests(unittest.TestCase):
    def test_preserves_on_key_and_parses_explicit_booleans(self):
        self.assertEqual(read_yaml("on: push\nrequired: true\n"), {"on": "push", "required": True})

    def test_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(ValidationError, "duplicate YAML key"):
            read_yaml("name: one\nname: two\n")

    def test_rejects_malformed_yaml(self):
        with self.assertRaises(ValidationError):
            read_yaml("name: [\n")

    def test_rejects_unsafe_constructor(self):
        with self.assertRaises(ValidationError):
            read_yaml("!!python/object/apply:os.system ['echo forbidden']")


class FormTests(unittest.TestCase):
    def test_valid_form(self):
        validate_issue_form(copy.deepcopy(FORM))

    def test_duplicate_field_ids(self):
        form = copy.deepcopy(FORM)
        form["body"] *= 2
        with self.assertRaisesRegex(ValidationError, "duplicate form id"):
            validate_issue_form(form)

    def test_missing_label(self):
        form = copy.deepcopy(FORM)
        del form["body"][0]["attributes"]["label"]
        with self.assertRaises(ValidationError):
            validate_issue_form(form)

    def test_quoted_required_is_not_boolean(self):
        form = copy.deepcopy(FORM)
        form["body"][0]["validations"]["required"] = "true"
        with self.assertRaisesRegex(ValidationError, "boolean"):
            validate_issue_form(form)

    def test_empty_body(self):
        form = copy.deepcopy(FORM)
        form["body"] = []
        with self.assertRaises(ValidationError):
            validate_issue_form(form)

    def test_dropdown_without_choices(self):
        form = copy.deepcopy(FORM)
        form["body"][0]["type"] = "dropdown"
        with self.assertRaisesRegex(ValidationError, "options"):
            validate_issue_form(form)


class WorkflowTests(unittest.TestCase):
    def test_valid_workflow(self):
        validate_workflow(copy.deepcopy(WORKFLOW))

    def test_mutable_action_reference(self):
        workflow = copy.deepcopy(WORKFLOW)
        workflow["jobs"]["process"]["steps"][0]["uses"] = "example/action@main"
        with self.assertRaisesRegex(ValidationError, "pinned"):
            validate_workflow(workflow)

    def test_write_permissions(self):
        workflow = copy.deepcopy(WORKFLOW)
        workflow["permissions"]["contents"] = "write"
        with self.assertRaisesRegex(ValidationError, "permissions"):
            validate_workflow(workflow)

    def test_job_permission_escalation(self):
        workflow = copy.deepcopy(WORKFLOW)
        workflow["jobs"]["process"]["permissions"] = {"contents": "write"}
        with self.assertRaisesRegex(ValidationError, "elevate"):
            validate_workflow(workflow)

    def test_privileged_pr_event(self):
        workflow = copy.deepcopy(WORKFLOW)
        workflow["on"]["pull_request_target"] = workflow["on"].pop("pull_request")
        with self.assertRaises(ValidationError):
            validate_workflow(workflow)

    def test_ambiguous_step(self):
        workflow = copy.deepcopy(WORKFLOW)
        workflow["jobs"]["process"]["steps"][0]["run"] = "unexpected"
        with self.assertRaises(ValidationError):
            validate_workflow(workflow)


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / "synthetic-skill"
        (self.folder / "agents").mkdir(parents=True)
        self.path = self.folder / "SKILL.md"
        self.path.write_text("---\nname: synthetic-skill\ndescription: A synthetic workflow\n---\nRead the task.\n")
        self.ui = self.folder / "agents/openai.yaml"
        self.ui.write_text('interface:\n  display_name: "Synthetic Skill"\n'
                           '  short_description: "Validate a synthetic workflow"\n'
                           '  default_prompt: "Use $synthetic-skill for this task."\n')

    def test_valid_skill(self):
        validate_skill(self.path)

    def test_missing_frontmatter(self):
        self.path.write_text("Instructions without metadata")
        with self.assertRaises(ValidationError):
            validate_skill(self.path)

    def test_mismatched_identity(self):
        self.path.write_text(self.path.read_text().replace("synthetic-skill", "different-skill"))
        with self.assertRaisesRegex(ValidationError, "folder"):
            validate_skill(self.path)

    def test_missing_instructions(self):
        self.path.write_text(self.path.read_text().replace("Read the task.\n", ""))
        with self.assertRaisesRegex(ValidationError, "empty"):
            validate_skill(self.path)

    def test_prompt_invokes_wrong_skill(self):
        self.ui.write_text(self.ui.read_text().replace("$synthetic-skill", "$synthetic-skill-other"))
        with self.assertRaisesRegex(ValidationError, "invoke"):
            validate_skill(self.path)

    def test_missing_ui_file(self):
        self.ui.unlink()
        with self.assertRaises(OSError):
            validate_skill(self.path)


class RepositoryTests(unittest.TestCase):
    def test_missing_workflow_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            errors, count = check_repository(Path(directory))
        self.assertEqual(count, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("process-checks.yml", errors[0])

    def test_skill_directory_without_entrypoint_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".agents/skills/incomplete-skill/agents").mkdir(parents=True)
            errors, count = check_repository(root)
        self.assertEqual(count, 2)
        self.assertTrue(any("incomplete-skill/SKILL.md" in error for error in errors))

    def test_yaml_extension_form_is_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / ".github/ISSUE_TEMPLATE/broken.yaml"
            template.parent.mkdir(parents=True)
            template.write_text("name: missing-body\ndescription: broken form\n")
            errors, count = check_repository(root)
        self.assertEqual(count, 2)
        self.assertTrue(any("broken.yaml" in error for error in errors))


class RulesetTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.ruleset = json.loads((root / ".github/rulesets/main.json").read_text())
        self.workflow = read_yaml((root / ".github/workflows/process-checks.yml").read_text())

    def test_valid_proposal(self):
        validate_ruleset(self.ruleset, self.workflow)

    def test_accidental_activation(self):
        self.ruleset["enforcement"] = "active"
        with self.assertRaisesRegex(ValidationError, "disabled"):
            validate_ruleset(self.ruleset, self.workflow)

    def test_unrelated_branch(self):
        self.ruleset["conditions"]["ref_name"]["include"] = ["~ALL"]
        with self.assertRaisesRegex(ValidationError, "only main"):
            validate_ruleset(self.ruleset, self.workflow)

    def test_missing_required_check(self):
        self.ruleset["rules"][3]["parameters"]["required_status_checks"][0]["context"] = "Unknown job"
        with self.assertRaisesRegex(ValidationError, "exist in the workflow"):
            validate_ruleset(self.ruleset, self.workflow)

    def test_arbitrary_check_source(self):
        self.ruleset["rules"][3]["parameters"]["required_status_checks"][0].pop("integration_id")
        with self.assertRaisesRegex(ValidationError, "GitHub Actions"):
            validate_ruleset(self.ruleset, self.workflow)

    def test_bypass_grant(self):
        self.ruleset["bypass_actors"] = [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}]
        with self.assertRaisesRegex(ValidationError, "bypass"):
            validate_ruleset(self.ruleset, self.workflow)


if __name__ == "__main__":
    unittest.main()
