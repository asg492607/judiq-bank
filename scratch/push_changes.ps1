param(
    [string]$RepoDir,
    [string]$Branch = "main"
)

Set-Location $RepoDir

# Get all modified and untracked files
$status = git status --porcelain

if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "No changes to commit." -ForegroundColor Yellow
    exit 0
}

$lines = $status -split "`n" | Where-Object { $_ -ne "" }

foreach ($line in $lines) {
    $statusCode = $line.Substring(0,2).Trim()
    $filePath = $line.Substring(3).Trim().Trim('"')

    # Skip .git directory files
    if ($filePath -like ".git*") { continue }

    # Add the specific file
    git add -- $filePath

    # Only commit if there's something staged
    $staged = git diff --cached --name-only
    if ($staged) {
        $action = switch -Wildcard ($statusCode) {
            "??" { "Add" }
            "M"  { "Update" }
            "A"  { "Add" }
            "D"  { "Remove" }
            default { "Update" }
        }
        $msg = "$action $filePath"
        git commit -m $msg
        Write-Host "Committed: $msg" -ForegroundColor Green
    }
}

# Push once at the end
Write-Host "`nPushing all commits to origin/$Branch ..." -ForegroundColor Cyan
git push origin $Branch
Write-Host "Done!" -ForegroundColor Green
