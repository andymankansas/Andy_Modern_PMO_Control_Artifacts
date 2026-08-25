[CmdletBinding()]
param(
    [string]$Version = "1.0.0",
    [string]$Destination = ""
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$parent = Split-Path -Parent $packageRoot
$name = "WBR_Agent"
if (-not $Destination) {
    $Destination = Join-Path $parent "${name}_Setup_$Version.zip"
}
$Destination = [System.IO.Path]::GetFullPath($Destination)
$stagingRoot = Join-Path ([System.IO.Path]::GetTempPath()) "wbr-release-$([guid]::NewGuid())"
$releaseRoot = Join-Path $stagingRoot "${name}_Setup_$Version"

# Never ship runtime data or personal config.
$exclude = @("drafts", "wbr_config.json", "weekly_input.json", "deck-structure.json", "__pycache__")

try {
    New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null
    Get-ChildItem -LiteralPath $packageRoot -Force | Where-Object { $exclude -notcontains $_.Name -and $_.Extension -ne ".pptx" } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $releaseRoot -Recurse -Force
    }
    # Strip any nested runtime folders/files that slipped in under subfolders.
    Get-ChildItem -LiteralPath $releaseRoot -Recurse -Force -Directory |
        Where-Object { $_.Name -in @("drafts", "__pycache__") } |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }
    Get-ChildItem -LiteralPath $releaseRoot -Recurse -Force -File |
        Where-Object { $_.Name -in @("wbr_config.json", "weekly_input.json", "deck-structure.json") -or $_.Extension -in @(".pyc", ".pptx") } |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }

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
