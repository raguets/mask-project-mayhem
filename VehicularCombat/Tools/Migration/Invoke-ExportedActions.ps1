param([Parameter(Mandatory=$true)][string]$Graph,[Parameter(Mandatory=$true)][string]$RunName,[int]$StartActionId=0,[int]$EndActionId=[int]::MaxValue)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if($RunName -notmatch '^[A-Za-z0-9_-]+$'){throw 'Use a simple run name.'}
$folder=Join-Path $repo ('Saved/SilentValley/'+$RunName)
if(Test-Path -LiteralPath $folder){throw 'Choose a fresh RunName.'}
New-Item -ItemType Directory -Path $folder | Out-Null
$data=Get-Content -LiteralPath $Graph -Raw | ConvertFrom-Json
foreach($entry in $data.Environment.PSObject.Properties){[Environment]::SetEnvironmentVariable($entry.Name,[string]$entry.Value,'Process')}
$env:DOTNET_CLI_HOME=Join-Path $repo 'Intermediate/DotNetHome'
$env:DOTNET_EnableDiagnostics='0'
$done=@();$results=@()
foreach($action in $data.Actions){
    if($action.Id -gt $EndActionId){break}
    if($action.Id -lt $StartActionId){$done+=$action.Id;continue}
    foreach($dependency in $action.PrerequisiteActions){if($done -notcontains $dependency){throw 'Actions must be topologically ordered.'}}
    foreach($output in $action.ProducedItems){if(![IO.Path]::GetFullPath($output).StartsWith($repo+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Output outside project: $output"}}
    # Pass UBT's exact Windows command line; reparsing loses nested RC /D quotes.
    $info=New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName=$action.CommandPath;$info.Arguments=$action.CommandArguments;$info.WorkingDirectory=$action.WorkingDirectory
    $info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
    $p=New-Object System.Diagnostics.Process;$p.StartInfo=$info
    try{
        [void]$p.Start();$stdout=$p.StandardOutput.ReadToEndAsync();$stderr=$p.StandardError.ReadToEndAsync();$p.WaitForExit();$nativeExit=$p.ExitCode
        [IO.File]::WriteAllText((Join-Path $folder ($action.Id.ToString()+'-stdout.txt')),$stdout.GetAwaiter().GetResult())
        [IO.File]::WriteAllText((Join-Path $folder ($action.Id.ToString()+'-stderr.txt')),$stderr.GetAwaiter().GetResult())
    }finally{$p.Dispose()}
    $results += [ordered]@{id=$action.Id;description=$action.StatusDescription;exit_code=$nativeExit}
    $results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $folder 'results.json') -Encoding UTF8
    Write-Output ($action.StatusDescription+' EXIT='+$nativeExit)
    if($nativeExit -ne 0){Get-Content (Join-Path $folder ($action.Id.ToString()+'-stdout.txt'));Get-Content (Join-Path $folder ($action.Id.ToString()+'-stderr.txt'));throw 'Exported action failed.'}
    $done += $action.Id
}
