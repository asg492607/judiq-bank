$lines = Get-Content -Path "scratch/old_script.js" -Raw
# Let's find the lines by matching content to be extremely robust.
# We want from 'const DRAFT_TYPES = [' to the end of the numberToWords function.
# Let's read by line number. In Get-Content without -Raw, lines are 0-indexed.
$lineArray = Get-Content -Path "scratch/old_script.js"
$extracted = $lineArray[3650..4779]

# Append export block
$extracted += ""
$extracted += "export { DRAFT_TYPES, formatDraftDate, numberToWords };"

# Write to file
$extracted | Out-File -FilePath "frontend/draft_templates.js" -Encoding utf8
