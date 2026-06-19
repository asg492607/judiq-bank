Set-Location "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\git_repos\backend"

$files = @(
    @{ path = "tests/test_engine.py";       msg = "test: Rewrite engine tests - proper fixtures, strict score assertions, no brittle string checks" },
    @{ path = "tests/test_scoring.py";      msg = "test: Rewrite scoring tests - output key assertions, bounds checks, penalty-not-zero validation" },
    @{ path = "tests/test_llmless.py";      msg = "test: Rewrite LLM-less tests - remove string matching, relaxed thresholds, graceful degradation checks" },
    @{ path = "tests/test_jurisdiction.py"; msg = "test: Add jurisdiction engine test suite - map_jurisdiction, court tiers, apply_jurisdiction_guards" }
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
Write-Host "Backend test push complete!" -ForegroundColor Green
