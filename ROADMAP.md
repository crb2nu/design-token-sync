# ROADMAP

## Mission

Provide a reliable and auditable token synchronization pipeline for FlexInfer UI libraries.

## Current State

- Source tokens are centralized in `tokens.json`.
- Sync script supports TypeScript and Python targets.
- Validation exists, but delivery process and guardrails were missing.

## Next Priorities

- **P0 - Delivery Reliability**
- Add CI for lint, test, and build on every merge request.
- Keep publish stage manual and tag-gated.

- **P0 - Baseline Quality**
- Maintain unit tests for token validation and output generation.
- Ensure metadata stripping behavior is locked down by tests.

- **P1 - Contract Safety**
- Add schema-level validation for optional sections (`gradients`, `shadows`) and value types.
- Add regression tests for malformed token structures.

- **P1 - Operational UX**
- Add a `--dry-run` mode that reports proposed file changes without writing.
- Add diff summary output for changed token keys.

- **P2 - Release Hygiene**
- Add semantic version bump and changelog guidance for token-breaking changes.
- Document consumer upgrade expectations.

## Dependencies and Risks

- Sync targets assume sibling repos exist at:
- `../visual-kit/tokens.json`
- `../py-visual-kit/src/visual_kit/tokens.json`
- Token schema drift between source and consumers can cause downstream breakage without CI checks.
