$sourceDir = "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\backend"
$targetDir = "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\git_repos\backend"

# Ensure target exists
if (!(Test-Path $targetDir)) {
    Write-Error "Target directory does not exist!"
    exit 1
}

# Copy files
Copy-Item -Path "$sourceDir\*" -Destination $targetDir -Recurse -Force

Set-Location $targetDir

# Get all files inside the repo (excluding .git)
$files = Get-ChildItem -File -Recurse -Exclude ".git" | Select-Object -ExpandProperty FullName

foreach ($file in $files) {
    # Get relative path for the commit message
    $relativePath = $file.Substring($targetDir.Length + 1).Replace('\', '/')
    
    # Add file
    git add $relativePath
    
    # Commit file
    git commit -m "Add $relativePath"
}

# Push all commits
git push origin main
git push origin master
