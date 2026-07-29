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
REPO="https://github.com/k1tz03/lenyay"
INSTALL_DIR="${LENYAY_HOME:-$HOME/.lenyay}"

say()  { printf '  %s\n' "$1"; }
step() { printf '\n=> %s\n' "$1"; }
die()  { printf '\n[X] %s\n' "$1" >&2; exit 1; }

printf '\n  Lenyay — reseau de calcul cooperatif\n'
printf '  Ta machine resout des problemes de maths pendant que tu dors.\n\n'

# --- 1. Python ----------------------------------------------------------
step "Verification de Python"
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 11) else 1)' 2>/dev/null; then
            PYTHON="$candidate"
            say "$("$candidate" --version) trouve"
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
step "Telechargement de Lenyay"
mkdir -p "$INSTALL_DIR"
rm -rf "$INSTALL_DIR/code"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$REPO/archive/refs/heads/main.tar.gz" -o "$TMP/lenyay.tar.gz"
elif command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP/lenyay.tar.gz" "$REPO/archive/refs/heads/main.tar.gz"
else
    die "curl ou wget est necessaire"
fi
tar -xzf "$TMP/lenyay.tar.gz" -C "$TMP"
mv "$TMP/lenyay-main" "$INSTALL_DIR/code"
CODE="$INSTALL_DIR/code"
say "Installe dans $CODE"

# --- 3. Environnement Python isole -------------------------------------
step "Preparation de l'environnement Python (1-3 minutes)"
"$PYTHON" -m venv "$INSTALL_DIR/venv" || die "Echec de la creation du venv (paquet python3-venv manquant ?)"
PY="$INSTALL_DIR/venv/bin/python"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r "$CODE/requirements.txt"
say "Dependances de base installees"

step "Installation du moteur d'inference (llama.cpp)"
"$PY" -m pip install --quiet -r "$CODE/requirements-llm.txt" \
    || die "Echec de l'installation de llama-cpp-python (outils de compilation manquants ?)"
say "Moteur installe"

# --- 4. Lanceur ---------------------------------------------------------
step "Creation du lanceur"
LAUNCHER="$INSTALL_DIR/lenyay"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
export LENYAY_COORDINATOR_URL="$COORDINATOR"
cd "$CODE"
exec "$PY" -m worker.main "\$@"
EOF
chmod +x "$LAUNCHER"
say "Lanceur : $LAUNCHER"

# --- 5. Diagnostic ------------------------------------------------------
step "Diagnostic"
LENYAY_COORDINATOR_URL="$COORDINATOR" "$PY" -m worker.main --check || true

printf '\n  Installation terminee.\n\n'
printf '  Pour contribuer :\n'
printf '      %s\n\n' "$LAUNCHER"
printf '  Au premier lancement, le modele (~1,1 Go) se telecharge.\n'
printf '  Suis la progression de l essaim sur %s\n\n' "$COORDINATOR"
