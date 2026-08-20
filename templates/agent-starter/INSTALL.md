# Installation

## Prerequisites

- Windows 10 or later.
- Visual Studio Code with GitHub Copilot.
- PowerShell 5.1 or 7.
- Python 3.11 or later.
- Network access for first-time dependency install.

## Install from GitHub Release

1. Download `<Agent Name>_Setup_<version>.zip` from the Releases page (tag starts with `<agent-slug>/`).
2. Extract it to a permanent tools folder.
3. Open the folder in VS Code.
4. In a PowerShell terminal run:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\setup.ps1
```

The installer creates a local `.venv`, installs dependencies, and runs tests. It needs no administrator rights.
