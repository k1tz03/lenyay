# Construit l'application de bureau et son installateur.
# Usage :  powershell -File scripts\build_desktop.ps1
# Sortie :  dist\Lenyay-Setup.exe  (a distribuer telle quelle)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "== Dependances de build =="
.\.venv\Scripts\pip.exe install -q pyinstaller pywebview

Write-Host "== 1/3 Application (dossier, demarre vite) =="
.\.venv\Scripts\pyinstaller.exe --noconfirm --noconsole --name Lenyay `
  --paths . `
  --collect-all llama_cpp `
  --collect-submodules worker --collect-submodules common `
  --hidden-import worker.main --hidden-import worker.inference `
  --hidden-import worker.generation --hidden-import worker.client `
  desktop\lenyay_app.py

Write-Host "== 2/3 Archive de l'application =="
if (Test-Path dist\Lenyay-app.zip) { Remove-Item dist\Lenyay-app.zip }
Compress-Archive -Path dist\Lenyay -DestinationPath dist\Lenyay-app.zip

Write-Host "== 3/3 Installateur (un seul .exe) =="
.\.venv\Scripts\pyinstaller.exe --noconfirm --noconsole --onefile `
  --name Lenyay-Setup `
  --add-data "dist\Lenyay-app.zip;." `
  desktop\installer.py

Write-Host ""
Write-Host "Termine : dist\Lenyay-Setup.exe"
Write-Host "Test silencieux : dist\Lenyay-Setup.exe --silent --dir C:\Temp\lenyay-test"
