# Andy Modern PMO Control Artifacts

Reusable project management control artifacts for VS Code and GitHub Copilot.

## RAID Review Agent

The first planned artifact is a configurable RAID Review Agent that can:

1. Use an existing Workback and RAID workbook or create one from an included template.
2. Review configured workbook tabs and project knowledge sources.
3. Produce evidence-grounded recommendations without modifying the workbook.
4. Conduct a formal item-by-item approval phase.
5. Apply only approved changes, with backup, audit, and post-write validation.

## Status

Pre-release development. The downloadable setup ZIP has not been published yet.

Do not use this repository against production project files until a versioned GitHub Release is available.

## Planned Recipient Workflow

1. Download the latest release ZIP.
2. Extract it into a dedicated folder.
3. Open that folder in VS Code.
4. Run `setup.ps1` in PowerShell.
5. Run `RAID Setup` in VS Code Chat.
6. Use the review, approval, and apply prompts in sequence.

## Safety Model

- Review is read-only.
- Approval is persisted separately from review.
- Workbook writes require an approved manifest.
- A changed workbook fingerprint blocks application.
- A timestamped backup is mandatory.
- Creating a new workbook copy is the default.
- Project configuration and generated output are excluded from source control.

## Repository Layout

- `.github/agents/`: VS Code custom agents.
- `.github/prompts/`: focused setup, review, approval, apply, and reconfiguration prompts.
- `config/`: configuration examples and schemas.
- `scripts/`: deterministic workbook tooling.
- `templates/`: distributable workbook templates.
- `tests/`: workbook and workflow validation.
- `docs/`: design and operating documentation.

## Security and Data Handling

Never commit project workbooks, meeting artifacts, email or Teams exports, generated proposals, approval manifests, backups, credentials, or personal configuration.

See `SECURITY.md` before contributing.

## License

No reuse license has been selected yet. A license must be chosen before the first public release.
