# Lenyay - installation du worker en une commande (Windows / PowerShell)
#
#   irm https://lenyay.org/install.ps1 | iex
#
# Installe dans %LOCALAPPDATA%\Lenyay : le code, un environnement Python isole,
# les dependances, puis cree un raccourci de lancement. N'installe rien
# ailleurs, ne touche pas au Python du systeme, ne demande pas les droits admin.
#
# NOTE : ce fichier doit rester en ASCII pur avec BOM. PowerShell 5.1 relit un
# .ps1 sans BOM en cp1252, ou le dernier octet d'un caractere accentue peut
# valoir un guillemet fermant : le script entier devient alors insyntaxique.

# Le script tourne DANS la session de l'utilisateur (irm | iex) : pas de
# "exit", qui refermerait sa fenetre avec le message d'erreur.
$ErrorActionPreference = "Stop"

# --- Reglages -----------------------------------------------------------
$Coordinator = if ($env:LENYAY_COORDINATOR_URL) { $env:LENYAY_COORDINATOR_URL }
               else { "https://lenyay.org" }   # <- domaine public
# codeload et non github.com/.../archive/ : cette derniere repond 404 a
# certains clients selon leur agent utilisateur.
$Archive     = "https://codeload.github.com/k1tz03/lenyay/zip/refs/heads/main"
$InstallDir  = Join-Path $env:LOCALAPPDATA "Lenyay"
$Code        = Join-Path $InstallDir "code"
# Modele et identite vivent HORS du dossier de code : une reinstallation ne
# doit jamais couter un nouveau telechargement de 1,1 Go ni la perte des credits.
$DataDir     = Join-Path $InstallDir "data"
$ModelsDir   = Join-Path $InstallDir "models"

function Say($msg)  { Write-Host "  $msg" }
function Step($msg) { Write-Host "`n=> $msg" -ForegroundColor Cyan }
function Die($msg)  {
    Write-Host "`n[X] $msg" -ForegroundColor Red
    Write-Host "  (rien n'a ete casse : ton installation precedente est intacte)"
    throw $msg
}

Write-Host ""
Write-Host "  Lenyay - reseau de calcul cooperatif" -ForegroundColor Green
Write-Host "  Ta machine resout des problemes de maths pendant que tu dors."
Write-Host ""

# --- 1. Python ----------------------------------------------------------
Step "Verification de Python"
$python = $null
$candidates = @(
    @("py", @("-3")),
    @("python", @()),
    @("python3", @())
)
foreach ($candidate in $candidates) {
    $exe = $candidate[0]
    $prefix = $candidate[1]
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
    # On ne juge PAS sur le chemin : un Python installe depuis le Microsoft
    # Store passe par le meme dossier WindowsApps que le raccourci-leurre.
    # Seule la reponse a --version fait foi : le leurre repond "Python was not
    # found...", qui ne correspond pas au motif de version ci-dessous.
    try {
        # Pas de 2>&1 : sous ErrorActionPreference=Stop, la moindre ligne sur
        # stderr d'un programme externe deviendrait une exception.
        $raw = & $exe @prefix --version
        $version = ($raw | Out-String).Trim()   # une seule chaine : -match remplit $Matches
        if ($version -match "Python (\d+)\.(\d+)") {
            if ([int]$Matches[1] -eq 3 -and [int]$Matches[2] -ge 11) {
                $python = $candidate
                Say "$version trouve"
                break
            } else {
                Say "$version est trop ancien (il faut 3.11 ou plus)"
            }
        }
    } catch {
        Say "$exe n'a pas repondu ($($_.Exception.Message))"
    }
}
if (-not $python) {
    Write-Host ""
    Write-Host "  Python 3.11 ou plus recent est necessaire." -ForegroundColor Yellow
    Write-Host "  Installe-le puis relance cette commande :"
    Write-Host "      winget install Python.Python.3.12" -ForegroundColor White
    Write-Host "  (ou telecharge-le sur https://www.python.org/downloads/)"
    Write-Host "  Pense a cocher 'Add Python to PATH' pendant l'installation."
    Die "Python manquant"
}

# --- 2. Telechargement du code -----------------------------------------
# On telecharge et on valide AVANT de toucher a l'installation en place.
Step "Telechargement de Lenyay"
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
$staging = Join-Path $InstallDir "staging"
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Path $staging -Force | Out-Null
$zip = Join-Path $staging "lenyay.zip"
try {
    Invoke-WebRequest -Uri $Archive -OutFile $zip -UseBasicParsing
} catch {
    Die "Telechargement impossible ($($_.Exception.Message)). Verifie ta connexion."
}
try {
    Expand-Archive -Path $zip -DestinationPath $staging -Force
} catch {
    Die "Archive illisible ($($_.Exception.Message))."
}
$extracted = Join-Path $staging "lenyay-main"
if (-not (Test-Path (Join-Path $extracted "worker\main.py"))) {
    Die "Archive incomplete : worker\main.py absent."
}
# Remplacement seulement maintenant, une fois le nouveau code valide en main.
if (Test-Path $Code) {
    $old = Join-Path $InstallDir "code-old"
    if (Test-Path $old) { Remove-Item $old -Recurse -Force -ErrorAction SilentlyContinue }
    try {
        Move-Item $Code $old -Force
    } catch {
        Die "Impossible de remplacer l'installation existante : Lenyay tourne peut-etre encore. Ferme-le et relance."
    }
}
Move-Item $extracted $Code -Force
Remove-Item $staging -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $InstallDir "code-old") -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
New-Item -ItemType Directory -Path $ModelsDir -Force | Out-Null
Say "Installe dans $Code"

# --- 3. Environnement Python isole -------------------------------------
Step "Preparation de l'environnement Python (1-3 minutes)"
$venv = Join-Path $InstallDir "venv"
$Py = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $Py)) {
    & $python[0] @($python[1]) -m venv $venv
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $Py)) {
        Die "Creation de l'environnement Python impossible (module venv absent ?)."
    }
}
& $Py -m pip install --quiet --upgrade pip
Say "Installation des dependances de base..."
& $Py -m pip install --quiet -r (Join-Path $Code "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    Die "Installation des dependances impossible (proxy ou coupure reseau ?)."
}
Say "Dependances de base installees"

Step "Installation du moteur d'inference (llama.cpp, ~200 Mo)"
& $Py -m pip install --quiet -r (Join-Path $Code "requirements-llm.txt")
if ($LASTEXITCODE -ne 0) { Die "Echec de l'installation de llama-cpp-python." }
# Une roue peut s'installer proprement puis refuser de s'importer : DLL mise en
# quarantaine par l'antivirus, runtime MSVC absent. On verifie tout de suite.
& $Py -c "import llama_cpp"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  Le moteur s'installe mais refuse de demarrer." -ForegroundColor Yellow
    Write-Host "  Causes frequentes : antivirus qui met la DLL en quarantaine,"
    Write-Host "  ou composants Visual C++ manquants :"
    Write-Host "      winget install Microsoft.VCRedist.2015+.x64" -ForegroundColor White
    Die "llama_cpp inutilisable"
}
Say "Moteur installe et verifie"

# --- 4. Raccourci de lancement -----------------------------------------
Step "Creation du lanceur"
$launcher = Join-Path $InstallDir "lenyay.ps1"
@"
# Lance le worker Lenyay
`$env:LENYAY_COORDINATOR_URL = "$Coordinator"
`$env:LENYAY_MODELS_DIR = "$ModelsDir"
`$env:LENYAY_DEVICE_FILE = "$DataDir\device.json"
Set-Location "$Code"
try {
    & "$Py" -m worker.main `$args
} catch {
    Write-Host "`nErreur : `$(`$_.Exception.Message)" -ForegroundColor Red
}
if (-not `$args) {
    Write-Host "`nAppuie sur Entree pour fermer."
    Read-Host | Out-Null
}
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
$env:LENYAY_MODELS_DIR = $ModelsDir
$env:LENYAY_DEVICE_FILE = Join-Path $DataDir "device.json"
Push-Location $Code
& $Py -m worker.main --check
Pop-Location

Write-Host ""
Write-Host "  Installation terminee." -ForegroundColor Green
Write-Host ""
Write-Host "  Pour contribuer : double-clique sur 'Lenyay' sur ton Bureau."
Write-Host ""
Write-Host "  Au premier lancement, le modele (~1,1 Go) se telecharge une fois"
Write-Host "  pour toutes. Il est conserve meme si tu reinstalles Lenyay."
Write-Host "  Suis la progression de l'essaim sur $Coordinator"
Write-Host ""
