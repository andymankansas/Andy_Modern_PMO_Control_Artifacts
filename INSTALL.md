# Installation

## Prerequisites

- Windows 10 or later.
- Visual Studio Code.
- GitHub Copilot access in VS Code.
- PowerShell 5.1 or PowerShell 7.
- Python 3.11 or later.
- Network access to install Python packages during first setup.
- Optional: WorkIQ access for Microsoft 365 source sweeps.

## Install from GitHub Release

1. Download `RAID_Review_Agent_Setup_<version>.zip` from the repository Releases page.
2. Extract it to a permanent project tools folder.
3. Open the extracted folder in VS Code.
4. Open a PowerShell terminal.
5. Run:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\setup.ps1
```

The installer creates `.venv`, installs dependencies locally, validates the example configuration and template, and runs the test suite. It does not require administrator access or modify global Python packages.

## Configure

1. Open VS Code Chat.
2. Select **RAID Review Agent**.
3. Run **RAID Setup**.
4. Choose an existing Workback and RAID workbook or the included template.
5. Confirm project scope, exclusions, workbook mappings, knowledge sources, and WorkIQ availability.
6. Review the generated `config/raid-config.json` summary.

Runtime configuration is local and excluded from Git.

## Troubleshooting

- If Python is not found, install Python 3.11 or later and reopen VS Code.
- If the workbook is locked, close Excel and allow OneDrive synchronization to finish.
- If WorkIQ is unavailable, disable it during setup and use local Meeting Monitor or knowledge folders.
- If a workbook fingerprint changes, run a new RAID Review before approval or apply.
- If the package template fails validation, redownload the release ZIP and rerun setup.