# Installation

## Prerequisites

- Windows 10 or later.
- Visual Studio Code.
- GitHub Copilot access in VS Code.
- PowerShell 5.1 or PowerShell 7.
- Python 3.11 or later.
- Network access to install Python packages during first setup.
- Optional: `faster-whisper` for local recording transcription.
- Optional: WorkIQ access for Microsoft 365 source grounding.

## Install from GitHub Release

1. Download `Walking_Deck_Agent_Setup_<version>.zip` from the repository Releases page.
2. Extract it to a permanent project tools folder.
3. Open the extracted folder in VS Code.
4. Open a PowerShell terminal.
5. Run:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\setup.ps1
```

The installer creates `.venv`, installs dependencies locally, validates the
example configuration and sample content, builds a demo deck, and runs the test
suite. It does not require administrator access or modify global Python packages.

## Optional: recording transcription

To transcribe meeting recordings locally (offline, CPU):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-transcribe.txt
```

## Configure and build

1. Open VS Code Chat.
2. Select **Walking Deck Agent**.
3. Run **Walking Deck Setup** (project, brand, output, slides, sources).
4. Run **Walking Deck Intake** to catalog artifacts (optional).
5. Run **Walking Deck Interview** to answer the content questions.
6. Run **Walking Deck Build** to generate the deck.

Runtime configuration and content are local and excluded from Git.

## Troubleshooting

- If Python is not found, install Python 3.11 or later and reopen VS Code.
- If a build reports a missing block, run `build_deck.py --list-blocks`.
- If transcription is unavailable, install `requirements-transcribe.txt` or
  provide a transcript file instead.
- If WorkIQ is unavailable, continue with local artifacts and interview answers.
