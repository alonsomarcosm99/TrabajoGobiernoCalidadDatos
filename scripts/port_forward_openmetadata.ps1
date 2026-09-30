param(
  [string]$Namespace = "default",
  [int]$LocalPort = 8585,
  [int]$RemotePort = 8585,
  [int]$RetrySeconds = 2
)

# Port-forward al OpenMetadata del TFM (mismo cluster Kind: tfm-om).
# Este script SOLO abre un tunel local; no modifica ninguna entidad del TFM.

$ErrorActionPreference = "Continue"

Write-Host "Port-forward a OpenMetadata (auto-reconexion)."
Write-Host "Destino : svc/openmetadata (-n $Namespace)"
Write-Host "URL     : http://127.0.0.1:$LocalPort"
Write-Host "Ctrl+C para terminar."

while ($true) {
  try {
    kubectl -n $Namespace port-forward svc/openmetadata "$LocalPort`:$RemotePort"
  } catch {
    Write-Host "Port-forward interrumpido: $($_.Exception.Message)"
  }
  Write-Host "Reintentando en $RetrySeconds s..."
  Start-Sleep -Seconds $RetrySeconds
}
