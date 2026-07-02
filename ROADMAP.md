# design-token-sync Roadmap

> Last Updated: 2026-07-02
> Tier: 2 (see workspace AGENTS.md "Portfolio Tiers")
> Tracking Issue: none — maintain-mode; backlog = [open issues](https://gitlab.flexinfer.ai/libs/design-token-sync/-/issues)

## Current Status

Token synchronization pipeline: canonical `tokens.json` synced to TypeScript (visual-kit) and Python (py-visual-kit) consumers with validation and metadata stripping. Maintain-mode: last organic change 2026-02-18 (baseline roadmap/CI/test coverage); onboarded to the shared platform/gitops python CI template on 2026-07-02 (portfolio-refresh slice 5, MR !2, pipeline 16388 green). Backlog issues #1/#2 closed as shipped-by-template; #3–#10 groomed to P3 in this refresh.

- **Plan store**: plan-workspace-portfolio-refresh-2026-h2-roadmaps-quality-baselin-f3db23 (this refresh; no repo-specific active plan)
- **Deployed**: not deployed (tooling; runs locally against sibling repos)
- **CI**: python template family (platform/gitops `ci/templates/python.yml` + tech-radar `radar.yml`), onboarded 2026-07-02

## Now

- Maintenance only — keep sync green against consumer repos; no active feature work.

## Next

- [ ] ruff/black/mypy config — design-token-sync is explicitly in scope for portfolio-refresh slice 7 (quality gate wave B, pending)
- [ ] Pre-commit hooks + standard Makefile targets alongside the slice-7 rollout

## Later

P3 backlog themes (promote if the tool re-activates): schema validation + malformed-token regression tests (#5, #6), `--dry-run` and diff summary output (#7, #8), SemVer/changelog guidance for breaking token changes (#9, #10).

## Backlog

Full backlog: [P1](https://gitlab.flexinfer.ai/libs/design-token-sync/-/issues/?label_name[]=P1) · [P2](https://gitlab.flexinfer.ai/libs/design-token-sync/-/issues/?label_name[]=P2) · [P3](https://gitlab.flexinfer.ai/libs/design-token-sync/-/issues/?label_name[]=P3) · [all open](https://gitlab.flexinfer.ai/libs/design-token-sync/-/issues)
