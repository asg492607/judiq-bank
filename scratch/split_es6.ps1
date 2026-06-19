$scriptPath = "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\frontend\script.js"
$outDir = "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\frontend\js\es6_modules"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$lines = Get-Content $scriptPath
$currentSection = "core"
$sections = @{}
$sections[$currentSection] = @()

foreach ($line in $lines) {
    if ($line -match "^\s*//\s*([A-Z\s&]+?)\s*(?:[-—].*)?$") {
        $name = $matches[1].Trim()
        if ($name -in @("CONFIGURATION", "RELIABILITY LAYER", "APPLICATION STATE", "WIZARD STEP DEFINITIONS", "TOAST NOTIFICATION SYSTEM", "LOADING OVERLAY SYSTEM", "API DATA PROCESSOR LAYER", "INITIALIZATION", "DASHBOARD FUNCTIONS", "CASE WIZARD FUNCTIONS", "RESULTS TAB SYSTEM", "WIZARD UI LOGIC", "CASE ANALYSIS", "AI REASONING LAYER", "SMART UPLOAD FUNCTIONS", "UTILITY FUNCTIONS")) {
            $currentSection = $name.ToLower() -replace "[^a-z0-9]", "_" -replace "_+", "_" -replace "^_|_$", ""
            if (-not $sections.ContainsKey($currentSection)) {
                $sections[$currentSection] = @()
            }
        }
    }
    $sections[$currentSection] += $line
}

# Create main.js that imports everything
$mainImports = @()
$mainExports = @()

foreach ($key in $sections.Keys) {
    $content = $sections[$key]
    if ($content.Count -lt 5) { continue }
    
    $filename = "$key.js"
    $outPath = Join-Path $outDir $filename
    
    # We will just write the content as is, but we need to export all functions/consts
    # To avoid complex AST parsing in powershell, we will just export everything matching function or const/let at top level
    
    $newContent = @()
    $exports = @()
    
    foreach ($line in $content) {
        if ($line -match "^function\s+([a-zA-Z0-9_]+)\s*\(") {
            $exports += $matches[1]
        }
        elseif ($line -match "^(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=") {
            $exports += $matches[1]
        }
        $newContent += $line
    }
    
    if ($exports.Count -gt 0) {
        $exportStr = "export { " + ($exports -join ", ") + " };"
        $newContent += $exportStr
    }
    
    $newContent | Set-Content $outPath -Encoding UTF8
    Write-Host "Created $filename with $($newContent.Count) lines"
    
    $mainImports += "import * as $key from './$filename';"
    $mainExports += "window.JudiQ_$key = $key;"
}

$mainJsContent = $mainImports + "" + $mainExports
$mainJsContent | Set-Content (Join-Path $outDir "index.js") -Encoding UTF8

Write-Host "Done parsing to ES6."
