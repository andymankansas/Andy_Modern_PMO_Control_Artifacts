# Meeting Monitor Agent

A self-configuring GitHub Copilot Chat agent that gathers your meeting notes (Copilot recap, AI notes, transcript highlights), sweeps your Outlook email, and sweeps your Teams chats for your project keywords, then saves everything as .docx and .md files in folders you choose. You do not edit any code. On first use it runs a short setup wizard; after that, one command captures the day.

## What is in this package

- `.github/agents/meeting-monitor.agent.md` - the agent. This is the only file you install.
- `docs/Meeting_Monitor_Setup_Guide.docx` - the full illustrated guide. Read this first.
- `setup.ps1` - optional helper that copies the agent into your project.
- `README.md`, `INSTALL.md`, `SECURITY.md` - quick start, setup, and data-handling notes.

## Prerequisites

- Visual Studio Code with the GitHub Copilot and GitHub Copilot Chat extensions.
- WorkIQ access in Copilot Chat (used to read your meetings, email, and Teams).

## 60-second setup

1. Extract this package.
2. In your project folder, create the folder path `.github/agents/`.
3. Copy `meeting-monitor.agent.md` into `.github/agents/` (the file name must end in `.agent.md`).
   Or run `.\setup.ps1` from the extracted folder to copy it for you.
4. Reload VS Code: press `Ctrl+Shift+P`, type `Reload Window`, and press Enter.
5. Open Copilot Chat and select the `Meeting Monitor` agent.
6. The first time, it runs a short setup wizard. It asks for your email, the folder to save into, your keywords, and which meetings to track, then saves your answers automatically.

## Every day after that

Run the `Meeting Monitor` agent once (end of day is best, because recaps can take 30 to 60 minutes to appear after a meeting).

## Useful commands

- `setup` - change your folders, keywords, or meetings anytime.
- `since 2026-07-01` - look back to a specific date.
- `dry-run` - preview what it would save without writing files.

## WorkIQ

The agent uses WorkIQ to read your meetings, email, and Teams. In Copilot Chat, run `@workiq` once and accept the agreement it shows. If it responds, you are ready.

Full details and troubleshooting are in `docs/Meeting_Monitor_Setup_Guide.docx`.
