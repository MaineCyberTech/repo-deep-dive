$env:GIT_TERMINAL_PROMPT='0'; $env:GCM_INTERACTIVE='never'
$out = ("protocol=https`nhost=github.com`n`n" | git credential fill 2>&1)
$token = (($out | Where-Object { $_ -match '^password=' }) -replace '^password=', '')
$H = @{ Authorization = "Bearer $token"; Accept = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28' }
$pr = Invoke-RestMethod -Uri 'https://api.github.com/repos/MaineCyberTech/repo-deep-dive/pulls/10' -Headers $H
Write-Host ("draft=" + $pr.draft)
Write-Host ("state=" + $pr.state)
Write-Host ("base=" + $pr.base.ref)
Write-Host ("head=" + $pr.head.ref)
Write-Host ("mergeable_state=" + $pr.mergeable_state)
Write-Host ("url=" + $pr.html_url)
