# Planning

This folder holds planning documents for features and improvements, structured to be Copilot-friendly and implementation-driven.  Have copilot use this directory to plan and track work.

Conventions (per-feature folders):

- Create a folder per feature: `planning/<component>/yyyy-mm-dd-feature-slug/`
- Inside each folder:
  - `feature-plan.md` — problem, goals, design, impacted code, tests, rollout
  - `implementation-plan.md` — step-by-step checklist the agent will follow
  - `github-issue.md` — GitHub issue template to track the feature
- Keep actionable checklists up to date; Copilot will use them to track progress

Suggested workflow:

1. Create a new folder for your feature
2. Copy `feature-plan-template.md` to `feature-plan.md`
3. Copy `implementation-plan-template.md` to `implementation-plan.md`
4. Copy `github-issue-template.md` to `github-issue.md`
5. Fill in both plans with enough detail for implementation
6. Fill in the GitHub issue template
