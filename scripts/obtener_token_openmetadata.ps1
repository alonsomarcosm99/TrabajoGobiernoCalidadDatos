param(
  [string]$Namespace = "default",
  [string]$Deployment = "openmetadata",
  [string]$Subject = "admin",
  [string]$Email = "admin@open-metadata.org",
  [string]$PreferredUsername = "admin",
  [int]$TtlHours = 8,
  [switch]$SetEnv,
  [string]$JwtScript = "F:\DISCO DURO PORTABLE\INGENIERIA\MASTER\TFM\TFM_Alonso_Marcos_Mu-oz\scripts\infra\generate_om_jwt.py"
)

# Wrapper que reutiliza el generador de JWT del TFM (no copia codigo).
# Si --SetEnv esta presente, deja $env:OM_TOKEN listo para los scripts Python.

if (-not (Test-Path -LiteralPath $JwtScript)) {
  Write-Error "No se encuentra el generador JWT del TFM en: $JwtScript"
  exit 1
}

$token = & python $JwtScript `
  --namespace $Namespace `
  --deployment $Deployment `
  --subject $Subject `
  --email $Email `
  --preferred-username $PreferredUsername `
  --ttl-hours $TtlHours

if ($LASTEXITCODE -ne 0) {
  Write-Error "Fallo generando JWT (codigo $LASTEXITCODE)."
  exit $LASTEXITCODE
}

if ($SetEnv) {
  $env:OM_TOKEN = $token
  Write-Host "Token escrito en `$env:OM_TOKEN (TTL = $TtlHours h)."
  Write-Host "Ya puedes lanzar:  python .\scripts\insertar_energitech.py"
} else {
  Write-Output $token
}
