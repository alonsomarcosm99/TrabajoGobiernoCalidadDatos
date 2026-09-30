param(
  [string]$EntregableRoot = (Join-Path $PSScriptRoot "..\entregable"),
  [string]$OutputDir = (Join-Path $PSScriptRoot "..\entregable\imágenes\mermaid"),
  [string]$Theme = "neutral",
  [string]$Background = "white",
  [string]$Width = "1600",
  [switch]$ForceInstall
)

# Renderiza TODOS los bloques mermaid de los .md de entregable/ a PNG bajo entregable/imagenes/mermaid/.
# Nomenclatura: <nombre-md>__<NN>.png  (NN = indice del bloque dentro del archivo, 01, 02, ...)
# Requiere Node.js + npx. Usa @mermaid-js/mermaid-cli al vuelo.

$ErrorActionPreference = "Stop"

# 1. Comprobar npx
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
  Write-Error "npx no esta disponible. Instala Node.js LTS (https://nodejs.org)."
  exit 1
}

# 2. Comprobar mermaid-cli (resolvera via npx; el primer uso descarga el paquete).
if ($ForceInstall) {
  Write-Host "Forzando instalacion global de @mermaid-js/mermaid-cli..."
  npm install -g "@mermaid-js/mermaid-cli"
}

# 3. Preparar destino
if (-not (Test-Path -LiteralPath $OutputDir)) {
  New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# 4. Recoger todos los .md de entregable/ (recursivo)
$mdFiles = Get-ChildItem -LiteralPath $EntregableRoot -Filter "*.md" -Recurse | Sort-Object FullName

$totalBlocks = 0
$totalFiles = 0
foreach ($md in $mdFiles) {
  $text = Get-Content -LiteralPath $md.FullName -Raw
  $regex = '(?ms)```mermaid\r?\n(.*?)\r?\n```'
  $matches = [System.Text.RegularExpressions.Regex]::Matches($text, $regex)
  if ($matches.Count -eq 0) { continue }
  $totalFiles++
  $baseName = [System.IO.Path]::GetFileNameWithoutExtension($md.Name)
  $i = 0
  foreach ($m in $matches) {
    $i++
    $blockNum = "{0:D2}" -f $i
    $tmpMmd = New-TemporaryFile
    Rename-Item -LiteralPath $tmpMmd.FullName -NewName ($tmpMmd.Name + ".mmd")
    $tmpMmdPath = $tmpMmd.FullName + ".mmd"
    Set-Content -LiteralPath $tmpMmdPath -Value $m.Groups[1].Value -Encoding UTF8
    $outPng = Join-Path $OutputDir "$baseName`__$blockNum.png"
    Write-Host "  -> $($md.Name) bloque $blockNum -> $([System.IO.Path]::GetFileName($outPng))"
    & npx -y "@mermaid-js/mermaid-cli" -i $tmpMmdPath -o $outPng -t $Theme -b $Background -w $Width | Out-Null
    Remove-Item -LiteralPath $tmpMmdPath -ErrorAction SilentlyContinue
    $totalBlocks++
  }
}

Write-Host ""
Write-Host "Exportados $totalBlocks diagramas de $totalFiles archivos a $OutputDir"
