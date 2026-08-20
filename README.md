# Andy Modern PMO Control Artifacts

A collection of installable VS Code and GitHub Copilot agent packages for modern PMO control and reporting. Each agent lives in its own folder under `agents/` and ships as its own versioned release.

## Available agents

| Agent | Folder | Latest release |
| --- | --- | --- |
| RAID Review Agent | [`agents/raid-review-agent`](agents/raid-review-agent) | [releases](https://github.com/andymankansas/Andy_Modern_PMO_Control_Artifacts/releases?q=raid-review-agent) |
| Meeting Monitor Agent | [`agents/meeting-monitor-agent`](agents/meeting-monitor-agent) | [releases](https://github.com/andymankansas/Andy_Modern_PMO_Control_Artifacts/releases?q=meeting-monitor-agent) |

## Download and install

1. Open the [Releases](https://github.com/andymankansas/Andy_Modern_PMO_Control_Artifacts/releases) page.
2. Find the release for the agent you want (the tag name starts with the agent slug).
3. Download that release's `*_Setup_<version>.zip` and, optionally, the matching `.sha256`.
4. Extract it, open the folder in VS Code, and follow that agent's `INSTALL.md`.

## Releases and versioning

Every agent has an independent release series. Tags are product-scoped so each agent is unambiguous:

```
<agent-slug>/vMAJOR.MINOR.PATCH[-prerelease]
```

Examples:

- `raid-review-agent/v1.0.0-preview.1`
- `raid-review-agent/v1.0.0`
- `meeting-monitor-agent/v1.0.0`

Rules:

- One release series per agent. Never reuse a bare `vX.Y.Z` tag across agents.
- Each release carries only that agent's ZIP and `.sha256`.
- Mark unfinished builds as pre-releases.
- Release titles stay human-readable, for example "RAID Review Agent v1.0.0-preview.1".

## Adding a new agent

1. Copy [`templates/agent-starter`](templates/agent-starter) to `agents/<agent-slug>/` and replace the placeholders (see the starter's `HOW-TO-USE.md`).
2. Add a validation job for it under `.github/workflows/`.
3. Build its ZIP and publish a release tagged `<agent-slug>/vX.Y.Z`.
4. Add a row to the table above.

## Data handling

Do not commit runtime configuration, project workbooks, meeting artifacts, exports, proposals, approvals, audits, backups, or any personal or tenant data. See each agent's `SECURITY.md`.


