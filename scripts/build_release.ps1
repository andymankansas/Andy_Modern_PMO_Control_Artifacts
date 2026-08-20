[CmdletBinding()]
param(
    [string]$Version = '1.0.0-preview.1',
    [string]$Destination = ''
)

$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$parent = Split-Path -Parent $packageRoot
if (-not $Destination) {
    $Destination = Join-Path $parent "RAID_Review_Agent_Setup_$Version.zip"
}
$Destination = [System.IO.Path]::GetFullPath($Destination)
$stagingRoot = Join-Path ([System.IO.Path]::GetTempPath()) "raid-review-agent-$([guid]::NewGuid())"
$releaseRoot = Join-Path $stagingRoot "RAID_Review_Agent_Setup_$Version"

try {
    New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null
    $excludeDirectories = @('.venv', '.pytest_cache', '__pycache__')
    $excludeFiles = @('raid-config.json')
    Get-ChildItem -LiteralPath $packageRoot -Force | ForEach-Object {
        if ($_.PSIsContainer -and $_.Name -in $excludeDirectories) { return }
        if (-not $_.PSIsContainer -and $_.Name -in $excludeFiles) { return }
        Copy-Item -LiteralPath $_.FullName -Destination $releaseRoot -Recurse -Force
    }
    Get-ChildItem -LiteralPath $releaseRoot -Recurse -Directory -Force |
        Where-Object Name -in $excludeDirectories |
        Remove-Item -Recurse -Force
    Get-ChildItem -LiteralPath $releaseRoot -Recurse -File -Force |
        Where-Object {
            $_.Name -eq 'raid-config.json' -or
            $_.Name -match '^raid-(proposal|approval|audit)_' -or
            $_.Name -match '\.backup_.*\.xls[xm]$'
        } |
        Remove-Item -Force
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