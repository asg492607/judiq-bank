Set-Location "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\git_repos\backend"

$files = @(
    @{ path = "schemas.py";   msg = "feat: Add strict Pydantic v2 validation bounds, length limits, and field mappings to CaseInput" },
    @{ path = "analysis.py";  msg = "fix: Add generic exception handler to engine execution block in analysis.py" }
)

foreach ($f in $files) {
    git add -- $f.path
    $staged = git diff --cached --name-only
    if ($staged) {
        git commit -m $f.msg
        Write-Host "Committed: $($f.msg)" -ForegroundColor Green
    } else {
        Write-Host "Skipped (no change): $($f.path)" -ForegroundColor Yellow
    }
}

Write-Host "`nPushing to origin/main..." -ForegroundColor Cyan
git push origin main
Write-Host "Final backend push complete!" -ForegroundColor Green
