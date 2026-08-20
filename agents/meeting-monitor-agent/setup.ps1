[CmdletBinding()]
param(
    [string]$ProjectPath = "."
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentSource = Join-Path $root ".github\agents\meeting-monitor.agent.md"
if (-not (Test-Path $agentSource)) { throw "Agent file not found next to setup.ps1." }

$target = Join-Path ([System.IO.Path]::GetFullPath($ProjectPath)) ".github\agents"
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -LiteralPath $agentSource -Destination (Join-Path $target "meeting-monitor.agent.md") -Force

Write-Host "Meeting Monitor installed." -ForegroundColor Green
Write-Host "Copied agent to: $target"
Write-Host "Next:"
Write-Host "  1. Reload VS Code (Ctrl+Shift+P, Reload Window)."
Write-Host "  2. Open Copilot Chat and select the Meeting Monitor agent."
Write-Host "  3. The first run starts the setup wizard."
