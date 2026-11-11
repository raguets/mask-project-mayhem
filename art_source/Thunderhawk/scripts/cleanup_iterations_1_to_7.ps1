$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath 'G:/DEV/mask-project-mayhem').Path
$artRoot = (Resolve-Path -LiteralPath (Join-Path $projectRoot 'art_source/Thunderhawk')).Path
$reportPath = Join-Path $projectRoot 'docs/qa/cleanup_iterations_1_to_7.json'
$activePaths = @('Thunderhawk_V8.blend', 'Thunderhawk_V8.blend1', 'scripts/build_thunderhawk_v8.py', 'exports/THK_V8.fbx')
$activeBefore = @{}
foreach ($relative in $activePaths) { $activeBefore[$relative] = (Get-FileHash -LiteralPath (Join-Path $artRoot $relative) -Algorithm SHA256).Hash }
$targets = @()
foreach ($relative in @('', 'scripts', 'exports')) {
    $dir = Join-Path $artRoot $relative
    $targets += Get-ChildItem -LiteralPath $dir -File | Where-Object { $_.Name -match '(?i)(?:^|_)v[1-7](?=[_.]|$)' }
}
foreach ($version in 1..7) {
    $candidate = Join-Path $artRoot ('renders/v' + $version)
    if (Test-Path -LiteralPath $candidate) { $targets += Get-Item -LiteralPath $candidate }
}
$targets = @($targets | Sort-Object FullName -Unique)
$inventory = @()
foreach ($target in $targets) {
    $resolved = (Resolve-Path -LiteralPath $target.FullName).Path
    if (-not $resolved.StartsWith($artRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Target outside Thunderhawk art workspace: $resolved" }
    if ($resolved -match '(?i)\\Images reference\\|(?:^|[\\_])v8(?:[\\_.]|$)') { throw "Protected target: $resolved" }
    $children = if ($target.PSIsContainer) { @(Get-ChildItem -LiteralPath $resolved -File -Recurse) } else { @($target) }
    foreach ($file in $children) { $inventory += [pscustomobject]@{path=$file.FullName.Substring($projectRoot.Length+1); bytes=$file.Length} }
}
# Record the exact deletion set before applying it. References and active V8 files are excluded.
$report = [ordered]@{authorized_by='User request, 2026-11-01';scope='Thunderhawk Blender iterations 1 through 7';files=$inventory;file_count=$inventory.Count;bytes=($inventory | Measure-Object bytes -Sum).Sum;active_hashes_before=$activeBefore;complete=$false}
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding UTF8
foreach ($target in $targets) { Remove-Item -LiteralPath $target.FullName -Recurse -Force }
$activeAfter = @{}
foreach ($relative in $activePaths) {
    $activeAfter[$relative] = (Get-FileHash -LiteralPath (Join-Path $artRoot $relative) -Algorithm SHA256).Hash
    if ($activeBefore[$relative] -ne $activeAfter[$relative]) { throw "Active source changed: $relative" }
}
$remaining = @($targets | Where-Object { Test-Path -LiteralPath $_.FullName })
if ($remaining.Count) { throw 'Some targets remain' }
$report['active_hashes_after']=$activeAfter
$report['active_sources_unchanged']=$true
$report['complete']=$true
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding UTF8
[pscustomobject]@{deleted_files=$inventory.Count;deleted_bytes=$report.bytes;active_sources_unchanged=$true} | ConvertTo-Json
