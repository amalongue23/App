<#
offline_recovery_with_docker.ps1

Automatiza criação de um container Ubuntu para análise/recuperação
offline dos arquivos InnoDB/Aria. Monta o backup mais recente em
/data e instala ferramentas básicas (git, python, build-essential)
para permitir clonagem de utilitários de recuperação.

Uso: Execute como Administrador no PowerShell:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\offline_recovery_with_docker.ps1

Após execução, um container nomeado 'innodb_recovery' ficará disponível
com /data apontando para o backup. Você poderá entrar no container com:
  docker exec -it innodb_recovery bash

#>

Set-StrictMode -Version Latest

function Find-LatestBackup {
    $root = 'C:\xampp\mysql'
    if (-not (Test-Path $root)) { return $null }
    $dirs = Get-ChildItem -Path $root -Directory -Filter 'data_backup_*' -ErrorAction SilentlyContinue
    if (-not $dirs -or $dirs.Count -eq 0) { return $null }
    $latest = $dirs | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    return $latest.FullName
}

Write-Output "Procurando backup mais recente em C:\xampp\mysql..."
$backup = Find-LatestBackup
if (-not $backup) {
    Write-Output "Nenhum diretório data_backup_* encontrado em C:\xampp\mysql. Abortando."; exit 1
}

Write-Output "Backup encontrado: $backup"

$containerName = 'innodb_recovery'

# Stop & remove existing container if present (safe cleanup)
if ((docker ps -a --format '{{.Names}}' 2>$null) -contains $containerName) {
    Write-Output "Removendo container existente '$containerName' (se estiver parado)..."
    docker rm -f $containerName | Out-Null
}

Write-Output "Criando container Ubuntu e montando backup (somente leitura)..."
$mount = ($backup + ':/data:ro')
docker run -d --name $containerName --privileged -v $mount ubuntu:22.04 tail -f /dev/null | Out-Null

if ($LASTEXITCODE -ne 0) { Write-Output 'Falha ao criar container. Verifique o Docker.'; exit 2 }

Write-Output "Container '$containerName' criado. Instalando pacotes básicos (pode levar alguns minutos)..."

# Atualiza e instala dependências básicas
docker exec $containerName bash -lc "apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 python3-pip build-essential cmake libssl-dev libboost-all-dev python3-dev pkg-config" 2>&1 | ForEach-Object { Write-Output $_ }

Write-Output "Pacotes instalados. Clonando repositórios de recuperação sugeridos (não executa extração automaticamente)..."

docker exec $containerName bash -lc "cd /root && git clone https://github.com/jeremycole/undrop-for-innodb.git || true && git clone https://github.com/percona/innodb_ruby.git || true" 2>&1 | ForEach-Object { Write-Output $_ }

Write-Output "Preparação completa. Para entrar no container e prosseguir com a extração, execute:"
Write-Output "  docker exec -it $containerName bash"
Write-Output "Dentro do container, inspecione /data e siga instruções de tools:"
Write-Output "  - Para 'undrop-for-innodb', veja README do repo (analisa arquivos .ibd e ibdata1)"
Write-Output "  - Para 'innodb_ruby', use ferramentas de leitura de tablespace (page_parser, etc.)"
Write-Output "Se preferir, posso entrar no container e executar os passos de extração para tentar gerar um dump SQL. Quer que eu continue e execute a extração agora?"

exit 0
