# Feature plan template

Use this template to capture the details Copilot needs to implement a feature safely and completely. Keep it concise and specific. Do not include task checklists here—track execution steps in the Implementation Plan or GitHub Issue.

## Problem

Describe the user problem and why it matters.

## Goals (acceptance criteria)

- Criterion 1
- Criterion 2

## Non-goals

- Out of scope items

## Design

- High-level design and data flow
- Public API or CLI changes
- Data structures and types
- UX/CLI examples
- Alignment with existing conventions (logging via logging.getLogger(__name__), CLI key=value patches, Director runlog persistence)

## Impacted code

List files and symbols that will change. Use backticks for paths and symbol names.

- `path/to/file.py`: function `foo()` change: ...
- Note any CLI or runlog integrations (e.g., `subcommands/run_cmd.py`, `shared.write_log_file`)

## Edge cases and risks

- Case 1
- Case 2

## Test plan

- Unit tests to add/update
- Integration/CLI tests
- Define any test case placeholders (e.g., `{audio_file}`) and how they resolve from pipeline configuration

## Migration/compat

- Backwards compatibility notes
- Deprecations and removal timeline

## Rollout

- Feature flag? config keys?
- Telemetry/logging to monitor

## Links

- Related issues/PRs
- Notes/docs
