[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Resolve-Python {
    $candidates = @(
        @{ Command = "py"; Arguments = @("-3.11") },
        @{ Command = "python"; Arguments = @() }
    )
    foreach ($candidate in $candidates) {
        if (Get-Command $candidate.Command -ErrorAction SilentlyContinue) {
            & $candidate.Command @($candidate.Arguments) -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { return $candidate }
        }
    }
    throw "Python 3.11 or later was not found. Install Python, reopen VS Code, and rerun setup.ps1."
}

Write-Host "<Agent Name> setup"
$python = Resolve-Python
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating local virtual environment..."
    & $python.Command @($python.Arguments) -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
}

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
Write-Host "Installing dependencies..."
& $venvPython -m pip install --disable-pip-version-check -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

if (Test-Path "tests") {
    Write-Host "Running tests..."
    & $venvPython -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
}

Write-Host ""
Write-Host "Setup completed successfully." -ForegroundColor Green
Write-Host "Next: open VS Code Chat and select <Agent Name>."
