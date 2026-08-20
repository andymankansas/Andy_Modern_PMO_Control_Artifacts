# Installation

## Prerequisites

- Windows 10 or later.
- Visual Studio Code with the GitHub Copilot and GitHub Copilot Chat extensions.
- WorkIQ access in Copilot Chat.

## Install from GitHub Release

1. Download `Meeting_Monitor_Agent_Setup_<version>.zip` from the Releases page (the tag starts with `meeting-monitor-agent/`).
2. Extract it to a permanent folder.
3. Copy `.github/agents/meeting-monitor.agent.md` into your project's `.github/agents/` folder, or run `.\setup.ps1` from the extracted folder and give it your project path.
4. Reload VS Code: press `Ctrl+Shift+P`, type `Reload Window`, and press Enter.
5. Open Copilot Chat and select the `Meeting Monitor` agent.

## First run

The first run starts a short setup wizard that asks for:

- Your work email (the mailbox WorkIQ reads).
- The OneDrive-synced folder to save notes into.
- Your project keywords.
- The meetings to track and whether to sweep email and Teams.

Your answers are written to `meeting_monitor_config.json` in your project. Re-run with `setup` to change them anytime.

## Verify WorkIQ

In Copilot Chat, run `@workiq` once and accept the agreement. If it responds, the agent can read your meetings, email, and Teams.

## Troubleshooting

- If the agent does not appear, confirm the file is at `.github/agents/meeting-monitor.agent.md` and reload the window.
- If notes do not save, confirm the destination folder path exists and OneDrive is syncing.
- If a meeting has no recap yet, wait 30 to 60 minutes and run again, or pass `since <date>`.

Full illustrated steps are in `docs/Meeting_Monitor_Setup_Guide.docx`.


