# RAID Review Agent

A configurable VS Code and GitHub Copilot workflow for evidence-grounded Workback and RAID reviews.

## Capabilities

- Uses an existing workbook or copies the included sanitized template.
- Reviews configured project plan, risk, action, and decision tabs.
- Reads local Meeting Monitor and knowledge-base artifacts.
- Optionally supplements local evidence with WorkIQ meetings, email, Teams, and files.
- Produces a read-only proposal before any workbook change.
- Conducts formal item-by-item approval.
- Applies only approved changes through a deterministic Python writer.
- Creates a timestamped backup and validates every saved value.

## Safety Model

The workflow has four persisted phases:

1. Review and proposal.
2. User review and disposition.
3. Approval manifest finalization.
4. Apply, reopen, validate, and audit.

Review and approval never modify the workbook. Uncertain recommendations cannot be written. A changed workbook fingerprint invalidates prior approval.

## Install

Extract the release ZIP, open the extracted folder in VS Code, and run:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\setup.ps1
```

Then select **RAID Review Agent** in VS Code Chat and run **RAID Setup**.

See [INSTALL.md](INSTALL.md) for prerequisites and setup details.

## Normal Workflow

1. Run **RAID Review**.
2. Inspect the generated Markdown proposal.
3. Run **RAID Approve** and disposition every item.
4. Run **RAID Apply Approved**.
5. Retain the generated audit JSON with the updated workbook.

## Package Layout

- `.github/agents/`: custom agent definition.
- `.github/prompts/`: setup, review, approval, apply, and reconfiguration prompts.
- `config/`: example runtime configuration.
- `schemas/`: JSON contracts for configuration, proposals, and approvals.
- `scripts/`: deterministic workbook and release tools.
- `templates/`: sanitized Workback and RAID template.
- `tests/`: executable safety and writer tests.
- `output/`: local proposals, approvals, and audits. Contents are ignored by Git.

## Data Handling

Do not commit runtime configuration, project workbooks, meeting artifacts, proposals, approvals, audits, backups, mailbox data, or Teams data. The included template contains no project data.

## Current Platform

The installer targets Windows because the intended experience uses VS Code, PowerShell, OneDrive or SharePoint synced paths, and optional desktop Excel compatibility. Standard `.xlsx` writing uses Python and does not require desktop Excel.