# Installation

The RAID Review Agent package is still under development. These steps describe the intended release installation path.

## Prerequisites

- Windows 10 or later
- Visual Studio Code
- GitHub Copilot access in VS Code
- PowerShell 5.1 or PowerShell 7
- Python 3.11 or later
- Microsoft 365 access for optional WorkIQ sources
- Desktop Excel only when a workbook requires Windows COM preservation

## Release Installation

1. Open the repository's Releases page.
2. Download `RAID_Review_Agent_Setup_<version>.zip` from the latest stable release.
3. Extract the ZIP into a dedicated folder.
4. Open the extracted folder in VS Code.
5. Open a PowerShell terminal.
6. Run:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\setup.ps1
```

7. In VS Code Chat, select the RAID Review Agent and run `RAID Setup`.
8. Choose an existing workbook or the included template.
9. Complete workbook mapping, project scope, knowledge source, and write policy configuration.
10. Run a read-only review before approving or applying changes.

## Important

Do not run setup from the repository source ZIP shown under GitHub's automatic Source code links. Use the versioned setup ZIP attached to a GitHub Release because that artifact will include the tested workbook template and package assets.
