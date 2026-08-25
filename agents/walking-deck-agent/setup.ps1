[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Resolve-Python {
    $candidates = @(
        @{ Command = 'py'; Arguments = @('-3.11') },
        @{ Command = 'py'; Arguments = @('-3') },
        @{ Command = 'python'; Arguments = @() }
    )
    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.Command -ErrorAction SilentlyContinue)) { continue }
        $ok = $false
        try {
            $prev = $ErrorActionPreference
            $ErrorActionPreference = 'SilentlyContinue'
            & $candidate.Command @($candidate.Arguments) -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null | Out-Null
            $ok = ($LASTEXITCODE -eq 0)
        } catch {
            $ok = $false
        } finally {
            $ErrorActionPreference = $prev
        }
        if ($ok) { return $candidate }
    }
    throw 'Python 3.11 or later was not found. Install Python, reopen VS Code, and rerun setup.ps1.'
}

Write-Host 'Walking Deck Agent setup'
$python = Resolve-Python
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    Write-Host 'Creating local virtual environment...'
    & $python.Command @($python.Arguments) -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}

$venvPython = Join-Path $root '.venv\Scripts\python.exe'
Write-Host 'Installing package dependencies...'
& $venvPython -m pip install --disable-pip-version-check -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }

Write-Host 'Validating example configuration and sample content...'
& $venvPython scripts\validate_json.py walking-deck-config.schema.json config\walking-deck-config.example.json
if ($LASTEXITCODE -ne 0) { throw 'Example configuration validation failed.' }
& $venvPython scripts\validate_json.py walking-deck-content.schema.json samples\sample_project_content.json
if ($LASTEXITCODE -ne 0) { throw 'Sample content validation failed.' }

Write-Host 'Building the demo deck...'
& $venvPython scripts\build_deck.py --config config\walking-deck-config.example.json
if ($LASTEXITCODE -ne 0) { throw 'Demo deck build failed.' }

Write-Host 'Running package tests...'
& $venvPython -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Package tests failed.' }

Write-Host ''
Write-Host 'Setup completed successfully.' -ForegroundColor Green
Write-Host 'Next: open VS Code Chat, select Walking Deck Agent, and run Walking Deck Setup.'
