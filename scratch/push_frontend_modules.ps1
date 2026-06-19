Set-Location "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\git_repos\frontend"

$files = @(
    @{ path = "js/modules/config.js";       msg = "feat: Add runtime config module - replaces hardcoded API/WS URLs" },
    @{ path = "js/modules/state.js";        msg = "feat: Add centralized state management with pub/sub and localStorage persistence" },
    @{ path = "js/modules/error_handler.js"; msg = "refactor: Comprehensive error boundary - graceful banners, telemetry, JudiQError.wrap()" },
    @{ path = "js/modules/ui.js";           msg = "feat: Enhance UI module - toast system, debounce, throttle, image fallback handlers" },
    @{ path = "js/modules/charts.js";       msg = "refactor: ChartRegistry pattern - memory-safe destroy-before-create, dark-theme charts" },
    @{ path = "js/modules/validation.js";   msg = "feat: Add input validation module - IFSC, date, amount validators, form step validation" },
    @{ path = "js/modules/caseroom.js";     msg = "fix: Caseroom WebSocket exponential backoff, remove duplicate onclose block, offline queue improvements" },
    @{ path = "js/modules/modals.js";       msg = "feat: Add modal system - legal disclaimer on first visit, confirm dialogs, keyboard/backdrop dismiss" },
    @{ path = "styles.css";                 msg = "fix: Complete [data-theme=light] overrides - success/warning/error/glass/shadow tokens" },
    @{ path = "index.html";                 msg = "refactor: Correct module load order, remove embedded scripts, add new module script tags" }
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
Write-Host "Frontend push complete!" -ForegroundColor Green
