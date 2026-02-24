<#
Recover MySQL data directory: backup, quarantine corrupted mysql system files,
repair Aria tables and attempt to restart mysqld. Run as Administrator.
#>
Set-StrictMode -Version Latest
Write-Output "Starting MySQL recovery script at $(Get-Date -Format o)"

# 1) Kill any running mysqld
Write-Output 'Killing mysqld if running...'
try { taskkill /F /IM mysqld.exe 2>$null } catch { }

# 2) Create backup directory
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$base = 'C:\xampp\mysql'
$dataDir = Join-Path $base 'data'
$backupDir = Join-Path $base ('data_backup_' + $ts)
Write-Output "Creating backup directory: $backupDir"
New-Item -Path $backupDir -ItemType Directory -Force | Out-Null

Write-Output 'Starting robocopy (this may take a while)...'
robocopy $dataDir $backupDir /MIR /NFL /NDL /NJH /NJS /NC /NS | Out-Null
Write-Output "Backup completed: $backupDir"

# 3) Create quarantine and move problematic mysql system files
$quarantine = Join-Path $base 'data_quarantine'
New-Item -Path $quarantine -ItemType Directory -Force | Out-Null

$patterns = @(
    'C:\xampp\mysql\data\mysql\db.*',
    'C:\xampp\mysql\data\mysql\global_priv.*',
    'C:\xampp\mysql\data\mysql\plugin.*',
    'C:\xampp\mysql\data\mysql\*.MAI',
    'C:\xampp\mysql\data\mysql\*.MAD'
)
foreach ($p in $patterns) {
    try {
        Get-ChildItem -Path $p -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Output "Moving $($_.FullName) to quarantine"
            Move-Item -Path $_.FullName -Destination $quarantine -Force -ErrorAction SilentlyContinue
        }
    } catch { }
}

Write-Output 'Files moved to quarantine (if present)'

# 4) Remove Aria logs
Write-Output 'Removing Aria logs if present'
Remove-Item -Path (Join-Path $dataDir 'aria_log.*') -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $dataDir 'aria_log_control') -Force -ErrorAction SilentlyContinue

# 5) Run aria_chk if available
$aria = 'C:\xampp\mysql\bin\aria_chk.exe'
if (Test-Path $aria) {
    Write-Output "Running aria_chk on $dataDir"
    & $aria -r "$dataDir\*.MAI" 2>&1 | ForEach-Object { Write-Output $_ }
} else { Write-Output 'aria_chk not found, skipping' }

# 6) Start mysqld and capture brief console output
$mysqld = 'C:\xampp\mysql\bin\mysqld.exe'
if (Test-Path $mysqld) {
    Write-Output 'Starting mysqld (console) in background'
    $proc = Start-Process -FilePath $mysqld -ArgumentList '--console' -PassThru
    Start-Sleep -Seconds 8
    if ($proc.HasExited) { Write-Output 'mysqld terminated immediately after start' } else { Write-Output "mysqld running PID=$($proc.Id)" }
} else { Write-Output 'mysqld.exe not found; aborting start' }

# 7) Run mysql_upgrade if exists
$upgrade = 'C:\xampp\mysql\bin\mysql_upgrade.exe'
if (Test-Path $upgrade) {
    Write-Output 'Running mysql_upgrade (may prompt for password if root has one).'
    & $upgrade -u root --force 2>&1 | ForEach-Object { Write-Output $_ }
} else { Write-Output 'mysql_upgrade not found, skipping' }

# 8) Attempt mysqlcheck --all-databases
$mysqlcheck = 'C:\xampp\mysql\bin\mysqlcheck.exe'
if (Test-Path $mysqlcheck) {
    Write-Output 'Running mysqlcheck --all-databases --auto-repair (may fail if server not accepting connections)'
    & $mysqlcheck --all-databases -u root --password= --auto-repair 2>&1 | ForEach-Object { Write-Output $_ }
} else { Write-Output 'mysqlcheck not found, skipping' }

# 9) Show last .err log contents
Write-Output 'Collecting last .err log (200 lines)'
$err = Get-ChildItem $dataDir -Filter '*.err' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($err) { Write-Output "---- Last lines of $($err.FullName) ----"; Get-Content $err.FullName -Tail 200 | ForEach-Object { Write-Output $_ } } else { Write-Output 'No .err file found' }

Write-Output 'Recovery script finished.'
