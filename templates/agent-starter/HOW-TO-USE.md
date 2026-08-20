HOW TO USE THIS STARTER

1. Copy this folder to agents/<agent-slug>/ (lowercase, hyphenated, e.g. meeting-monitor-agent).
2. Replace every placeholder across all files:
   <Agent Name>    human-readable name, e.g. Meeting Monitor Agent
   <agent-slug>    folder and tag slug, e.g. meeting-monitor-agent
   <agent_module>  python module/name base, e.g. meeting_monitor
3. Add real code under scripts/, tests under tests/, and any agent/prompt files under .github/.
4. Fill requirements.txt with real dependencies.
5. Copy ci-workflow.yml.template to .github/workflows/validate-<agent-slug>.yml at the REPO ROOT and replace placeholders.
6. Add a row for the agent to the root README.md table.
7. Delete this HOW-TO-USE.md from your copied folder.
8. Build and publish:
     .\setup.ps1
     .\scripts\build_release.ps1 -Version 1.0.0
     gh release create "<agent-slug>/v1.0.0" ... --prerelease
