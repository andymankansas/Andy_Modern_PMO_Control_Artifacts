[CmdletBinding()]
param(
    [string]$Version = "1.0.0",
    [string]$Destination = ""
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$parent = Split-Path -Parent $packageRoot
$name = "Meeting_Monitor_Agent"
if (-not $Destination) {
    $Destination = Join-Path $parent "${name}_Setup_$Version.zip"
}
$Destination = [System.IO.Path]::GetFullPath($Destination)
$stagingRoot = Join-Path ([System.IO.Path]::GetTempPath()) "mm-release-$([guid]::NewGuid())"
$releaseRoot = Join-Path $stagingRoot "${name}_Setup_$Version"

try {
    New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null
    Get-ChildItem -LiteralPath $packageRoot -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $releaseRoot -Recurse -Force
    }
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
