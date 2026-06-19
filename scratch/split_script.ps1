$scriptPath = "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\frontend\script.js"
$outDir = "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\frontend\js_extracted"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$lines = Get-Content $scriptPath
$currentSection = "header"
$currentLines = @()

foreach ($line in $lines) {
    if ($line.StartsWith("// ════════════════════════════════════════════════")) {
        continue
    }

    if ($line -match "^// ([A-Z ]+) -?.*" -and $line -notmatch "════") {
        $name = $matches[1].Trim()
        if ($name -in @("CONFIGURATION", "RELIABILITY LAYER", "APPLICATION STATE", "WIZARD STEP DEFINITIONS", "TOAST NOTIFICATION SYSTEM", "LOADING OVERLAY SYSTEM", "API DATA PROCESSOR LAYER", "WIZARD UI LOGIC", "CASE ANALYSIS", "AI REASONING LAYER")) {
            if ($currentLines.Count -gt 0) {
                $filename = $currentSection.ToLower().Replace(" ", "_").Replace("-", "_").Replace("__", "_") + ".js"
                $currentLines | Set-Content (Join-Path $outDir $filename) -Encoding UTF8
                Write-Host "Created $filename with $($currentLines.Count) lines"
            }
            $currentSection = $name
            $currentLines = @($line)
            continue
        }
    }
    $currentLines += $line
}

if ($currentLines.Count -gt 0) {
    $filename = $currentSection.ToLower().Replace(" ", "_").Replace("-", "_").Replace("__", "_") + ".js"
    $currentLines | Set-Content (Join-Path $outDir $filename) -Encoding UTF8
    Write-Host "Created $filename with $($currentLines.Count) lines"
}

Write-Host "Done"
