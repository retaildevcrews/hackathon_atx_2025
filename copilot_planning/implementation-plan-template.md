# Implementation plan — Template

This plan defines discrete, verifiable steps for the agent to implement a feature. Check off each step as it’s completed.

## Pre-flight

- [ ] Confirm dependencies and add to project manifest
- [ ] Add lazy import entries (if applicable)
- [ ] Confirm no breaking changes; note feature flags if needed

## Implementation

- [ ] Create or update modules and classes
- [ ] Implement core logic and data paths
- [ ] Logging via `logging.getLogger(__name__)`; no prints
- [ ] Wire up configuration and env var resolution

## Validation

- [ ] Unit tests for happy path and edge cases
- [ ] Contract tests for error conditions
- [ ] Update or add integration tests (optional)

## Samples and documentation

- [ ] Add a sample under `samples/<feature>/`
- [ ] Add or update docs under `documentation/`

## Rollout

- [ ] Update dependencies in `pyproject.toml`
- [ ] Update README and any CLI docs
- [ ] Add telemetry/metrics notes (if applicable)
