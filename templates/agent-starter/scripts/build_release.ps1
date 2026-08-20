[CmdletBinding()]
param(
    [string]$Version = "1.0.0",
    [string]$Name = "<Agent Name>",
    [string]$Destination = ""
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$parent = Split-Path -Parent $packageRoot
$safeName = ($Name -replace "\s+", "_")
if (-not $Destination) {
    $Destination = Join-Path $parent "${safeName}_Setup_$Version.zip"
}
$Destination = [System.IO.Path]::GetFullPath($Destination)
$stagingRoot = Join-Path ([System.IO.Path]::GetTempPath()) "agent-release-$([guid]::NewGuid())"
$releaseRoot = Join-Path $stagingRoot "${safeName}_Setup_$Version"

try {
    New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null
    $excludeDirectories = @(".venv", ".pytest_cache", "__pycache__")
    Get-ChildItem -LiteralPath $packageRoot -Force | ForEach-Object {
        if ($_.PSIsContainer -and $_.Name -in $excludeDirectories) { return }
        if (-not $_.PSIsContainer -and $_.Name -eq "HOW-TO-USE.md") { return }
        Copy-Item -LiteralPath $_.FullName -Destination $releaseRoot -Recurse -Force
    }
    Get-ChildItem -LiteralPath $releaseRoot -Recurse -Directory -Force |
        Where-Object Name -in $excludeDirectories | Remove-Item -Recurse -Force
    if (Test-Path $Destination) { Remove-Item -LiteralPath $Destination -Force }
    Compress-Archive -LiteralPath $releaseRoot -DestinationPath $Destination -CompressionLevel Optimal
    $hash = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
    Set-Content -LiteralPath "$Destination.sha256" -Value "$hash  $(Split-Path -Leaf $Destination)" -Encoding ascii
    Write-Host "Created: $Destination"
    Write-Host "SHA256: $hash"
}
finally {
    if (Test-Path $stagingRoot) { Remove-Item -LiteralPath $stagingRoot -Recurse -Force }
}
