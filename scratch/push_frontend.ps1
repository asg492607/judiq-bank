$sourceDir = "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\frontend"
$repoUrl = "https://github.com/asg492607/judiq-frontend.git"
$targetDir = "c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\git_repos\frontend"

# Clone if not exists
if (!(Test-Path $targetDir)) {
    git clone $repoUrl $targetDir
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
