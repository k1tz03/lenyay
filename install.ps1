# Lenyay - installation du worker en une commande (Windows / PowerShell)
#
#   irm https://lenyay.org/install.ps1 | iex
#
# Installe dans %LOCALAPPDATA%\Lenyay : le code, un environnement Python isole,
# les dependances, puis cree un raccourci de lancement. N'installe rien
# ailleurs, ne touche pas au Python du systeme, ne demande pas les droits admin.

$ErrorActionPreference = "Stop"

# --- Reglages -----------------------------------------------------------
$Coordinator = if ($env:LENYAY_COORDINATOR_URL) { $env:LENYAY_COORDINATOR_URL }
               else { "https://lenyay.org" }   # <- domaine public
$Repo        = "https://github.com/k1tz03/lenyay"
$InstallDir  = Join-Path $env:LOCALAPPDATA "Lenyay"

function Say($msg)  { Write-Host "  $msg" }
function Step($msg) { Write-Host "`n=> $msg" -ForegroundColor Cyan }
function Die($msg)  { Write-Host "`n[X] $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "  Lenyay - reseau de calcul cooperatif" -ForegroundColor Green
Write-Host "  Ta machine resout des problemes de maths pendant que tu dors."
Write-Host ""

# --- 1. Python ----------------------------------------------------------
Step "Verification de Python"
$python = $null
foreach ($candidate in @("py -3", "python", "python3")) {
    try {
        $parts = $candidate.Split(" ")
        $version = & $parts[0] $parts[1..$parts.Length] --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)") {
            if ([int]$Matches[1] -eq 3 -and [int]$Matches[2] -ge 11) {
                $python = $candidate
                Say "$version trouve"
                break
            }
        }
    } catch { }
}
if (-not $python) {
    Write-Host ""
    Write-Host "  Python 3.11 ou plus recent est necessaire." -ForegroundColor Yellow
    Write-Host "  Installe-le puis relance cette commande :"
    Write-Host "      winget install Python.Python.3.12" -ForegroundColor White
    Write-Host "  (ou telecharge-le sur https://www.python.org/downloads/)"
    Die "Python manquant"
}

# --- 2. Telechargement du code -----------------------------------------
Step "Telechargement de Lenyay"
if (Test-Path $InstallDir) {
    Say "Mise a jour de l'installation existante"
    Remove-Item (Join-Path $InstallDir "code") -Recurse -Force -ErrorAction SilentlyContinue
} else {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
$zip = Join-Path $env:TEMP "lenyay.zip"
Invoke-WebRequest -Uri "$Repo/archive/refs/heads/main.zip" -OutFile $zip -UseBasicParsing
Expand-Archive -Path $zip -DestinationPath $InstallDir -Force
Move-Item (Join-Path $InstallDir "lenyay-main") (Join-Path $InstallDir "code") -Force
Remove-Item $zip -Force
$Code = Join-Path $InstallDir "code"
Say "Installe dans $Code"

# --- 3. Environnement Python isole -------------------------------------
Step "Preparation de l'environnement Python (1-3 minutes)"
$parts = $python.Split(" ")
& $parts[0] $parts[1..$parts.Length] -m venv (Join-Path $InstallDir "venv")
$Py = Join-Path $InstallDir "venv\Scripts\python.exe"
& $Py -m pip install --quiet --upgrade pip
& $Py -m pip install --quiet -r (Join-Path $Code "requirements.txt")
Say "Dependances de base installees"

Step "Installation du moteur d'inference (llama.cpp)"
& $Py -m pip install --quiet -r (Join-Path $Code "requirements-llm.txt")
if ($LASTEXITCODE -ne 0) { Die "Echec de l'installation de llama-cpp-python" }
Say "Moteur installe"

# --- 4. Raccourci de lancement -----------------------------------------
Step "Creation du lanceur"
$launcher = Join-Path $InstallDir "lenyay.ps1"
@"
# Lance le worker Lenyay
`$env:LENYAY_COORDINATOR_URL = "$Coordinator"
Set-Location "$Code"
& "$Py" -m worker.main `$args
"@ | Set-Content -Path $launcher -Encoding UTF8

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcut = Join-Path $desktop "Lenyay.lnk"
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($shortcut)
$link.TargetPath = "powershell.exe"
$link.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$launcher`""
$link.WorkingDirectory = $Code
$link.Description = "Contribuer a l'essaim Lenyay"
$link.Save()
Say "Raccourci 'Lenyay' cree sur le Bureau"

# --- 5. Diagnostic ------------------------------------------------------
Step "Diagnostic"
$env:LENYAY_COORDINATOR_URL = $Coordinator
& $Py -m worker.main --check

Write-Host ""
Write-Host "  Installation terminee." -ForegroundColor Green
Write-Host ""
Write-Host "  Pour contribuer : double-clique sur 'Lenyay' sur ton Bureau,"
Write-Host "  ou lance :"
Write-Host "      powershell -ExecutionPolicy Bypass -File `"$launcher`"" -ForegroundColor White
Write-Host ""
Write-Host "  Au premier lancement, le modele (~1,1 Go) se telecharge."
Write-Host "  Suis la progression de l'essaim sur $Coordinator"
Write-Host ""
