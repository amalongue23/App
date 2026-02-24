Set-StrictMode -Version Latest
Write-Output "Apply innodb_force_recovery and attempt dump: $(Get-Date -Format o)"

$paths = @(
    'C:\xampp\mysql\my.ini',
    'C:\xampp\mysql\bin\my.ini',
    'C:\xampp\mysql\data\my.ini',
    'C:\xampp\mysql\my.cnf'
)
$found = $null
foreach ($p in $paths) { if (Test-Path $p) { $found = $p; break } }
if (-not $found) { Write-Output 'my.ini not found in common locations; aborting'; exit 1 }

$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$backup = $found + '.backup_' + $ts
Copy-Item -Path $found -Destination $backup -Force
Write-Output "Backed up $found -> $backup"

$content = Get-Content -Path $found -Raw -ErrorAction Stop
if ($content -match '(?m)^[ \t]*innodb_force_recovery\s*=') {
    $content = [regex]::Replace($content,'(?m)^[ \t]*innodb_force_recovery\s*=\s*\d+','innodb_force_recovery=1')
    Write-Output 'Replaced existing innodb_force_recovery value with 1'
} else {
    if ($content -match '(?m)^\[mysqld\]') {
        $content = $content -replace '(?m)^\[mysqld\]','[mysqld]`r`ninnodb_force_recovery=1'
        Write-Output 'Inserted innodb_force_recovery=1 under existing [mysqld]'
    } else {
        $content = $content + "`r`n[mysqld]`r`ninnodb_force_recovery=1`r`n"
        Write-Output 'Appended [mysqld] and innodb_force_recovery=1 to file'
    }
}

Set-Content -Path $found -Value $content -Encoding UTF8
Write-Output "Updated $found"

# Start mysqld
$mysqld = 'C:\xampp\mysql\bin\mysqld.exe'
if (Test-Path $mysqld) {
    Write-Output 'Starting mysqld (console) in background'
    $proc = Start-Process -FilePath $mysqld -ArgumentList '--console' -PassThru
    Start-Sleep -Seconds 10
    if ($proc.HasExited) { Write-Output 'mysqld terminated immediately after start' } else { Write-Output "mysqld started PID=$($proc.Id)" }
} else {
    Write-Output 'mysqld.exe not found; aborting start'
}

# Check if server reachable on port 3306
Start-Sleep -Seconds 3
$reachable = $false
try {
    $tnc = Test-NetConnection -ComputerName '127.0.0.1' -Port 3306 -WarningAction SilentlyContinue
    if ($tnc.TcpTestSucceeded) { $reachable = $true }
} catch { }

if ($reachable) {
    Write-Output 'Server reachable on 3306. Attempting mysqldump...'
    $dumpFile = 'C:\xampp\mysql\dump_all.sql'
    & 'C:\xampp\mysql\bin\mysqldump.exe' -u root --all-databases --single-transaction --skip-lock-tables --result-file=$dumpFile 2>&1 | ForEach-Object { Write-Output $_ }
    if (Test-Path $dumpFile) { Write-Output "Dump completed: $dumpFile" } else { Write-Output 'Dump failed or file not created' }
} else {
    Write-Output 'Server not reachable on 3306; cannot run mysqldump. Consider increasing innodb_force_recovery level.'
}

Write-Output 'apply_innodb_recovery.ps1 finished.'
