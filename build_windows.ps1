$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$vendorDirectory = Join-Path $projectRoot "build\vendor"
$applicationDirectory = Join-Path $projectRoot "dist\yt-dlp-tool"
$toolsDirectory = Join-Path $applicationDirectory "tools"

Set-Location -LiteralPath $projectRoot

$tools = @("yt-dlp.exe", "ffmpeg.exe", "ffprobe.exe")
$toolPaths = @{}

foreach ($tool in $tools) {
	$application = Get-Command $tool -CommandType Application -ErrorAction SilentlyContinue |
		Select-Object -First 1

	if ($null -eq $application) {
		throw "$tool was not found in PATH."
	}

	$toolPaths[$tool] = $application.Source
}

New-Item -ItemType Directory -Path $vendorDirectory -Force | Out-Null

foreach ($tool in $tools) {
	Copy-Item -LiteralPath $toolPaths[$tool] `
		-Destination (Join-Path $vendorDirectory $tool) -Force
}

python -m PyInstaller `
	--noconfirm `
	--clean `
	--onedir `
	--windowed `
	--specpath build `
	--name yt-dlp-tool `
	--collect-all customtkinter `
	gui.py

if ($LASTEXITCODE -ne 0) {
	throw "La construction PyInstaller a échoué (code $LASTEXITCODE)."
}

New-Item -ItemType Directory -Path $toolsDirectory -Force | Out-Null

foreach ($tool in $tools) {
	Copy-Item -LiteralPath (Join-Path $vendorDirectory $tool) `
		-Destination (Join-Path $toolsDirectory $tool) -Force
}

$ytDlpVersion = (& (Join-Path $vendorDirectory "yt-dlp.exe") --version).Trim()
$ffmpegVersion = & (Join-Path $vendorDirectory "ffmpeg.exe") -version |
	Select-Object -First 1
$ffmpegSource = "https://ffmpeg.org/download.html"

if ($ffmpegVersion -match "git-([0-9a-fA-F]+)") {
	$ffmpegSource = "https://github.com/FFmpeg/FFmpeg/commit/$($matches[1])"
}

$notices = @"
YT-DLP-TOOL - THIRD-PARTY NOTICES

yt-dlp
Version: $ytDlpVersion
Project and license: https://github.com/yt-dlp/yt-dlp

FFmpeg et ffprobe
Version: $ffmpegVersion
This FFmpeg build reports GPL version 3 or later in its license information.
Corresponding FFmpeg source snapshot: $ffmpegSource
Windows build provider: https://www.gyan.dev/ffmpeg/builds/

Node.js is not included. Install it separately if yt-dlp requires it for
some supported sites.
"@

Set-Content -LiteralPath (Join-Path $applicationDirectory "THIRD_PARTY_NOTICES.txt") `
	-Value $notices -Encoding utf8

Write-Host "Ready-to-run folder: $applicationDirectory"
Write-Host "Executable: $(Join-Path $applicationDirectory 'yt-dlp-tool.exe')"
