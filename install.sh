#!/usr/bin/env bash
# Lenyay — installation du worker en une commande (Linux / macOS)
#
#   curl -fsSL https://lenyay.org/install.sh | bash
#
# Installe dans ~/.lenyay : le code, un environnement Python isolé, les
# dépendances, puis crée un lanceur. Ne touche pas au Python du système,
# ne demande jamais sudo.

set -euo pipefail

COORDINATOR="${LENYAY_COORDINATOR_URL:-https://lenyay.org}"
# codeload et non github.com/.../archive/ : cette derniere renvoie 404 aux
# requetes du curl par defaut (GitHub filtre sur l'agent utilisateur).
ARCHIVE="https://codeload.github.com/k1tz03/lenyay/tar.gz/refs/heads/main"
INSTALL_DIR="${LENYAY_HOME:-$HOME/.lenyay}"
CODE="$INSTALL_DIR/code"
# Modèle et identité vivent HORS du dossier de code : une réinstallation ne
# doit jamais coûter un nouveau téléchargement de 1,1 Go ni la perte des crédits.
DATA_DIR="$INSTALL_DIR/data"
MODELS_DIR="$INSTALL_DIR/models"

say()  { printf '  %s\n' "$1"; }
step() { printf '\n=> %s\n' "$1"; }
die()  {
    printf '\n[X] %s\n' "$1" >&2
    printf '  (rien n a ete casse : ton installation precedente est intacte)\n' >&2
    exit 1
}

printf '\n  Lenyay — reseau de calcul cooperatif\n'
printf '  Ta machine resout des problemes de maths pendant que tu dors.\n\n'

# --- 1. Python ----------------------------------------------------------
step "Verification de Python"
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 11) else 1)' 2>/dev/null; then
            PYTHON="$candidate"
            say "$("$candidate" --version 2>&1) trouve"
            break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    printf '\n  Python 3.11 ou plus recent est necessaire.\n'
    printf '    Debian/Ubuntu : sudo apt install python3 python3-venv\n'
    printf '    Fedora        : sudo dnf install python3\n'
    printf '    macOS         : brew install python@3.12\n'
    die "Python manquant"
fi

# --- 2. Telechargement du code -----------------------------------------
# On telecharge et on valide AVANT de toucher a l'installation en place.
step "Telechargement de Lenyay"
mkdir -p "$INSTALL_DIR" "$DATA_DIR" "$MODELS_DIR"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$ARCHIVE" -o "$TMP/lenyay.tar.gz" \
        || die "Telechargement impossible. Verifie ta connexion."
elif command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP/lenyay.tar.gz" "$ARCHIVE" \
        || die "Telechargement impossible. Verifie ta connexion."
else
    die "curl ou wget est necessaire"
fi
tar -xzf "$TMP/lenyay.tar.gz" -C "$TMP" || die "Archive illisible."
[ -f "$TMP/lenyay-main/worker/main.py" ] || die "Archive incomplete : worker/main.py absent."
# Remplacement seulement maintenant, une fois le nouveau code valide en main.
rm -rf "$CODE.old"
[ -d "$CODE" ] && mv "$CODE" "$CODE.old"
mv "$TMP/lenyay-main" "$CODE"
rm -rf "$CODE.old"
say "Installe dans $CODE"

# --- 3. Environnement Python isole -------------------------------------
step "Preparation de l'environnement Python (1-3 minutes)"
PY="$INSTALL_DIR/venv/bin/python"
if [ ! -x "$PY" ]; then
    "$PYTHON" -m venv "$INSTALL_DIR/venv" \
        || die "Echec de la creation du venv (paquet python3-venv manquant ?)"
fi
"$PY" -m pip install --quiet --upgrade pip
say "Installation des dependances de base..."
"$PY" -m pip install --quiet -r "$CODE/requirements.txt" \
    || die "Installation des dependances impossible (proxy ou coupure reseau ?)"
say "Dependances de base installees"

step "Installation du moteur d'inference (llama.cpp, ~200 Mo)"
"$PY" -m pip install --quiet -r "$CODE/requirements-llm.txt" \
    || die "Echec de l'installation de llama-cpp-python (outils de compilation manquants ?)"
# Une roue peut s'installer proprement puis refuser de s'importer.
"$PY" -c "import llama_cpp" 2>/dev/null \
    || die "Le moteur s'installe mais refuse de demarrer (bibliotheque systeme manquante ?)"
say "Moteur installe et verifie"

# --- 4. Lanceur ---------------------------------------------------------
step "Creation du lanceur"
LAUNCHER="$INSTALL_DIR/lenyay"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
export LENYAY_COORDINATOR_URL="$COORDINATOR"
export LENYAY_MODELS_DIR="$MODELS_DIR"
export LENYAY_DEVICE_FILE="$DATA_DIR/device.json"
cd "$CODE"
exec "$PY" -m worker.main "\$@"
EOF
chmod +x "$LAUNCHER"
say "Lanceur : $LAUNCHER"

# --- 5. Diagnostic ------------------------------------------------------
step "Diagnostic"
LENYAY_COORDINATOR_URL="$COORDINATOR" LENYAY_MODELS_DIR="$MODELS_DIR" \
    LENYAY_DEVICE_FILE="$DATA_DIR/device.json" \
    "$PY" -c "import sys; sys.path.insert(0, '$CODE')
from common import config
from worker import preflight
ok, report = preflight.run_all(config)
print(report)
print('\nTout est pret.' if ok else '\nCorrige les points en ECHEC ci-dessus.')" || true

printf '\n  Installation terminee.\n\n'
printf '  Pour contribuer :\n'
printf '      %s\n\n' "$LAUNCHER"
printf '  Au premier lancement, le modele (~1,1 Go) se telecharge une fois pour\n'
printf '  toutes. Il est conserve meme si tu reinstalles Lenyay.\n'
printf '  Suis la progression de l essaim sur %s\n\n' "$COORDINATOR"
