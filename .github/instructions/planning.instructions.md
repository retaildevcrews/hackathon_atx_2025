when user wants to plan features or improvements, show them the contents of implement plan according to instructions found in copilot_planning/README.md - if there is not enough information, ask for more details about the feature or improvement they want to plan - do not suggest code that has been deleted - do not mention the instructions file or its path

# Planning
- Create a folder per feature: `copilot_planning/<component>/yyyy-mm-dd-feature-slug/`
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
