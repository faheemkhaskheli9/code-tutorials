# Write one post with Claude, then publish it to Blogger as a draft.
# Add -Live to publish immediately instead of saving a draft.
param([switch]$Live)
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force logs | Out-Null
$log = "logs\$(Get-Date -Format yyyy-MM-dd_HHmm).log"

git pull --quiet origin main
claude -p "Follow the instructions in WRITE_POST.md exactly." --permission-mode auto *>> $log
if ($Live) { python publish.py --live *>> $log } else { python publish.py *>> $log }
