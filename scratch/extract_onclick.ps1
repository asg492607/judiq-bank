$html = Get-Content -Raw -Path "frontend/index.html"
$regex = [regex]'onclick="([^"]*)"'
$matches = $regex.Matches($html)
$unique = $matches | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
$unique | Out-File -FilePath "scratch/onclicks.txt"
