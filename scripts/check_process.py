"""Validate process artifacts; application behavior is outside this check's scope."""

from pathlib import Path
import re
import sys

import yaml


class ValidationError(ValueError):
    """An artifact cannot safely be interpreted by its consumer."""


class ProcessLoader(yaml.SafeLoader):
    """Keep GitHub's `on` key a string and reject ambiguous duplicate keys."""


ProcessLoader.yaml_implicit_resolvers = {
    key: [(tag, pattern) for tag, pattern in values if tag != "tag:yaml.org,2002:bool"]
    for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
ProcessLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false|True|False|TRUE|FALSE)$"), list("tTfF")
)


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as error:
            raise ValidationError("YAML mapping keys must be scalar") from error
        if duplicate:
            raise ValidationError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


ProcessLoader.add_constructor("tag:yaml.org,2002:map", unique_mapping)


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def mapping(value, description):
    require(isinstance(value, dict), f"{description} must be a mapping")
    return value


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def read_yaml(text):
    try:
        return yaml.load(text, Loader=ProcessLoader)
    except yaml.YAMLError as error:
        raise ValidationError(f"invalid YAML: {error}") from error


def validate_skill(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    require(match is not None, "SKILL.md needs YAML frontmatter")
    data = mapping(read_yaml(match.group(1)), "skill frontmatter")
    name = data.get("name")
    require(nonempty(name) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), "invalid skill name")
    require(len(name) <= 64 and name == path.parent.name, "skill name must match its folder (max 64 chars)")
    require(nonempty(data.get("description")), "skill description is required")
    require(bool(text[match.end():].strip()), "skill instructions are empty")
    ui_path = path.parent / "agents" / "openai.yaml"
    ui = mapping(read_yaml(ui_path.read_text(encoding="utf-8")), "skill UI metadata")
    interface = mapping(ui.get("interface"), "interface")
    require(nonempty(interface.get("display_name")), "display_name is required")
    short = interface.get("short_description")
    require(nonempty(short) and 25 <= len(short) <= 64, "short_description must have 25–64 characters")
    prompt = interface.get("default_prompt")
    require(nonempty(prompt) and re.search(r"\$" + re.escape(name) + r"(?![a-z0-9-])", prompt),
            "default_prompt must invoke this skill")
    if "policy" in ui:
        policy = mapping(ui["policy"], "policy")
        if "allow_implicit_invocation" in policy:
            require(isinstance(policy["allow_implicit_invocation"], bool), "invocation policy must be boolean")


def validate_issue_form(data):
    data = mapping(data, "issue form")
    require(nonempty(data.get("name")) and nonempty(data.get("description")), "form name and description are required")
    body = data.get("body")
    require(isinstance(body, list) and body, "form body must be a nonempty list")
    ids = set()
    for field in body:
        field = mapping(field, "form field")
        kind = field.get("type")
        require(kind in {"markdown", "textarea", "input", "dropdown", "checkboxes"}, "unknown form field type")
        attrs = mapping(field.get("attributes"), "field attributes")
        if kind == "markdown":
            require(nonempty(attrs.get("value")), "markdown value is required")
            continue
        field_id = field.get("id")
        require(nonempty(field_id) and re.fullmatch(r"[A-Za-z0-9_-]+", field_id), "valid field id is required")
        require(field_id not in ids, f"duplicate form id: {field_id}")
        ids.add(field_id)
        require(nonempty(attrs.get("label")), "field label is required")
        if kind in {"dropdown", "checkboxes"}:
            options = attrs.get("options")
            require(isinstance(options, list) and options, "selection options are required")
            for option in options:
                require(nonempty(option) if kind == "dropdown" else
                        isinstance(option, dict) and nonempty(option.get("label")), "invalid selection option")
        if "validations" in field:
            validations = mapping(field["validations"], "validations")
            if "required" in validations:
                require(isinstance(validations["required"], bool), "required must be boolean")
    require(bool(ids), "form needs at least one input field")


def pinned_action(value):
    return isinstance(value, str) and re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", value) is not None


def validate_workflow(data):
    data = mapping(data, "workflow")
    require(nonempty(data.get("name")), "workflow name is required")
    events = mapping(data.get("on"), "workflow events")
    require(set(events) == {"pull_request", "push"}, "process workflow must run on PR and push only")
    for event in events.values():
        require(mapping(event, "event").get("branches") == ["main"], "process events must target main")
    require(data.get("permissions") == {"contents": "read"}, "workflow permissions must be contents: read")
    jobs = mapping(data.get("jobs"), "jobs")
    require(bool(jobs), "workflow has no jobs")
    for job in jobs.values():
        job = mapping(job, "job")
        if "permissions" in job:
            require(job["permissions"] == {"contents": "read"}, "job must not elevate permissions")
        steps = job.get("steps")
        require(isinstance(steps, list) and steps, "job must have steps")
        for step in steps:
            step = mapping(step, "step")
            require(("uses" in step) != ("run" in step), "step needs exactly one of uses or run")
            if "uses" in step:
                require(pinned_action(step["uses"]), "actions must be pinned to full commit SHAs")
            else:
                require(nonempty(step["run"]), "run command is empty")


def check_repository(root):
    errors = []
    checks = [(path, validate_skill) for path in sorted((root / ".agents/skills").glob("*/SKILL.md"))]
    for path in sorted((root / ".github/ISSUE_TEMPLATE").glob("*.yml")):
        checks.append((path, lambda p: validate_issue_form(read_yaml(p.read_text(encoding="utf-8")))))
    checks.append((root / ".github/workflows/process-checks.yml",
                   lambda p: validate_workflow(read_yaml(p.read_text(encoding="utf-8")))))
    for path, validator in checks:
        try:
            validator(path)
        except (OSError, ValidationError) as error:
            errors.append(f"{path.relative_to(root)}: {error}")
    return errors, len(checks)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    errors, count = check_repository(root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    print(f"Validated {count} process artifacts (structure only).")
