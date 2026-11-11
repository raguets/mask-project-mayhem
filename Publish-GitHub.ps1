param([switch]$Publish)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath($PSScriptRoot)
$url='https://github.com/raguets/mask-project-mayhem.git'
Set-Location -LiteralPath $root
function Invoke-Git {
    $previousPreference=$ErrorActionPreference
    $ErrorActionPreference='Continue'
    try{ & git -c "safe.directory=$root" @args; $nativeExit=$LASTEXITCODE }
    finally{$ErrorActionPreference=$previousPreference}
    if($nativeExit -ne 0){throw "Git failed (exit $nativeExit): $($args[0])"}
}
if(!(Test-Path -LiteralPath (Join-Path $root '.git-backups/VehicularCombat-20261111.git'))){throw 'Original repository archive missing'}
if(Test-Path -LiteralPath (Join-Path $root 'VehicularCombat/.git')){throw 'Nested repository still present; refusing a gitlink import'}
if(!(Test-Path -LiteralPath (Join-Path $root '.git'))){Invoke-Git init -b main}
$audit=Join-Path $root 'VehicularCombat/Saved/GitHubMigration'
New-Item -ItemType Directory -Path $audit -Force | Out-Null

# Use the existing Windows trust roots with OpenSSL; certificate checks stay on.
$certs=@(Get-ChildItem Cert:\LocalMachine\Root)
$certs+=@(Get-ChildItem Cert:\CurrentUser\Root -ErrorAction SilentlyContinue)
$pem=($certs | Sort-Object Thumbprint -Unique | ForEach-Object {
    '-----BEGIN CERTIFICATE-----'+"`n"+[Convert]::ToBase64String($_.RawData,[Base64FormattingOptions]::InsertLineBreaks)+"`n"+'-----END CERTIFICATE-----'
}) -join "`n"
$bundle=Join-Path $audit 'windows-trusted-roots.pem'
[IO.File]::WriteAllText($bundle,$pem,[Text.Encoding]::ASCII)
Invoke-Git config --local http.sslBackend openssl
Invoke-Git config --local http.sslCAInfo $bundle
Invoke-Git lfs install --local
$origin=& git -c "safe.directory=$root" config --local --get remote.origin.url
if($LASTEXITCODE -ne 0){Invoke-Git remote add origin $url}
elseif($origin -ne $url){throw "Unexpected origin: $origin"}
if((Invoke-Git symbolic-ref --short HEAD) -ne 'main'){throw 'Expected main branch; no branches were reset'}

# The existing remote is public. Fetch without consulting stale credentials.
Invoke-Git -c 'credential.helper=' fetch origin main
& git -c "safe.directory=$root" rev-parse --verify --quiet HEAD *> $null
if($LASTEXITCODE -ne 0){
    # Only on an unborn branch: adopt GitHub's existing LICENSE commit,
    # leaving every working-tree file untouched.
    Invoke-Git reset --mixed origin/main
}else{
    & git -c "safe.directory=$root" merge-base --is-ancestor origin/main HEAD
    if($LASTEXITCODE -ne 0){throw 'Remote history diverged; refusing a forced push or reset'}
}
$remoteLicense=Invoke-Git rev-parse origin/main:LICENSE
if(Test-Path -LiteralPath (Join-Path $root 'LICENSE')){
    if((Invoke-Git hash-object --path=LICENSE -- LICENSE) -ne $remoteLicense){throw 'Local LICENSE differs from GitHub; review it before continuing'}
}else{Invoke-Git restore --source=origin/main --worktree -- LICENSE}

Invoke-Git add --all
$entries=@(Invoke-Git -c core.quotepath=false ls-files --stage)
if($entries | Where-Object {$_ -match '^160000 '}){throw 'Unexpected gitlink/submodule staged'}
if($entries | Where-Object {$_ -match "`t(?:.*\/)?(?:Saved|Intermediate|Binaries|DerivedDataCache|\.git-backups)/"}){throw 'Generated data or Git archive staged'}
$entries | Set-Content -Encoding UTF8 (Join-Path $audit 'staged-files.txt')

# Check the indexed objects, including LFS pointers, rather than working file sizes.
$oids=@($entries | ForEach-Object {($_ -split ' ',3)[1]} | Sort-Object -Unique)
$sizes=@($oids | & git -c "safe.directory=$root" cat-file '--batch-check=%(objectname) %(objecttype) %(objectsize)')
if($LASTEXITCODE -ne 0){throw 'Cannot audit staged object sizes'}
if($sizes | Where-Object {[int64](($_ -split ' ')[2]) -ge 100MB}){throw 'A staged Git object reaches 100 MiB; check LFS rules'}
Invoke-Git diff --cached --stat | Set-Content -Encoding UTF8 (Join-Path $audit 'staged-stat.txt')
Write-Host "Staged files: $($entries.Count). Review: $audit/staged-files.txt and staged-stat.txt"
Invoke-Git status --short | Set-Content -Encoding UTF8 (Join-Path $audit 'staged-status.txt')
Get-Content (Join-Path $audit 'staged-status.txt') -TotalCount 25
if(!$Publish){Write-Host 'Prepared only. To commit and push, rerun with -Publish.'; exit 0}

# Authenticate in the user's own terminal. No token is printed by this script.
$identity=$null
try{$identity=& gh api user --jq .login 2>$null; if($LASTEXITCODE -ne 0){$identity=$null}}catch{$identity=$null}
if(!$identity){
    & gh auth login --hostname github.com --git-protocol https --web
    if($LASTEXITCODE -ne 0){throw 'GitHub login failed; prepared files and original archive remain intact'}
}
$canPush=& gh api repos/raguets/mask-project-mayhem --jq .permissions.push
if($LASTEXITCODE -ne 0 -or $canPush -ne 'true'){throw 'The active GitHub account lacks push access'}
& git -c "safe.directory=$root" diff --cached --quiet
$diffExit=$LASTEXITCODE
if($diffExit -eq 1){Invoke-Git commit -m 'Import M.A.S.K. workspace with Unreal and editable art sources'}
elseif($diffExit -ne 0){throw 'Cannot inspect staged changes'}

# Reset inherited helpers for this push, then use the authenticated GitHub CLI.
# Git propagates these options to the LFS pre-push hook as well.
Invoke-Git -c 'credential.helper=' -c 'credential.helper=!gh auth git-credential' push --set-upstream origin main
Invoke-Git -c 'credential.helper=' fetch origin main
$local=Invoke-Git rev-parse HEAD
$remote=Invoke-Git rev-parse origin/main
if($local -ne $remote){throw 'Local and remote commits differ after push'}
Invoke-Git lfs fsck
# Record the verified migration before reporting completion. Keep this
# idempotent so rerunning after a network interruption adds no duplicate note.
$handoff=Join-Path $root 'HANDOFF.md'
$text=[IO.File]::ReadAllText($handoff)
if($text -notmatch '<!-- github-published:[0-9a-f]{40} -->'){
    $start=$text.IndexOf('## Migration GitHub')
    if($start -lt 0){throw 'Migration section missing from HANDOFF.md'}
    $note=@"
## Migration GitHub — publication vérifiée

<!-- github-published:$local -->
Dépôt unique à la racine, branche main, origin=$url. L'ancien dépôt est conservé dans .git-backups/VehicularCombat-20261111.git (ignoré). Le commit LICENSE de GitHub est conservé comme ancêtre ; première publication du workspace vérifiée : $local. Les assets sont suivis avec Git LFS ; git lfs fsck a réussi. Aucun push forcé, aucune suppression de sources. Les caches, compilations, sauvegardes Blender et dépendances QA installées sont exclus. VehicularCombat/LICENSE est conservée distinctement de la licence racine. Cette publication n'est pas une validation artistique du niveau.

## Première action recommandée

Reprendre la validation de l'environnement : la plantation r6 est enregistrée (298 pins, 10826 herbes, 115 rochers), mais les rendus, le clipping visuel et les régressions restent à vérifier. Exécuter refine_silent_valley_view_distance.py, validate_silent_valley_environment.py, puis capturer/inspecter les dix vues avant toute revendication de qualité finale. Les commandes Git portent désormais sur la racine du workspace.
"@
    [IO.File]::WriteAllText($handoff,$text.Substring(0,$start)+$note,[Text.UTF8Encoding]::new($false))
    Invoke-Git add -- HANDOFF.md
    Invoke-Git commit -m 'Document verified GitHub migration'
    Invoke-Git -c 'credential.helper=' -c 'credential.helper=!gh auth git-credential' push origin main
    Invoke-Git -c 'credential.helper=' fetch origin main
    $local=Invoke-Git rev-parse HEAD
    if($local -ne (Invoke-Git rev-parse origin/main)){throw 'Handoff publication could not be verified'}
}
Write-Host "Verified push: $local"
Write-Host 'https://github.com/raguets/mask-project-mayhem'
