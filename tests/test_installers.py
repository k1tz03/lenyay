"""Tests des installateurs — vérifiés par lecture du script, sans rien installer.

Ces contrôles auraient attrapé le bug d'encodage qui empêchait install.ps1 de
démarrer sur Windows, ainsi que les sept défauts trouvés par la revue.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PS1 = REPO / "install.ps1"
SH = REPO / "install.sh"


@pytest.fixture(scope="module")
def ps1() -> str:
    return PS1.read_text(encoding="utf-8-sig")


@pytest.fixture(scope="module")
def sh() -> str:
    return SH.read_text(encoding="utf-8")


class TestEncodage:
    def test_ps1_est_ascii_pur(self):
        """PowerShell 5.1 relit un .ps1 sans BOM en cp1252 : un seul caractère
        accentué ou tiret long y casse la première chaîne du script."""
        raw = PS1.read_bytes()
        body = raw[3:] if raw.startswith(b"\xef\xbb\xbf") else raw
        body.decode("ascii")  # lève UnicodeDecodeError si non-ASCII

    def test_ps1_a_un_bom(self):
        assert PS1.read_bytes().startswith(b"\xef\xbb\xbf")

    def test_ps1_syntaxe_valide(self):
        """Fait valider le script par le parseur PowerShell lui-même."""
        script = (
            "$e=$null;"
            f"[void][System.Management.Automation.Language.Parser]::ParseFile('{PS1}',"
            "[ref]$null,[ref]$e);"
            "if($e){$e[0].Message; exit 1} else {'OK'}"
        )
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, text=True, timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    def test_sh_sans_crlf(self):
        """Un shebang suivi de \\r rend le script inexécutable sous Linux."""
        assert b"\r\n" not in SH.read_bytes()


class TestPreservationDesDonnees:
    def test_le_modele_et_l_identite_survivent_a_une_reinstallation(self, ps1, sh):
        # Le modèle et l'identité vivent hors du dossier de code jetable.
        for script in (ps1, sh):
            assert "LENYAY_MODELS_DIR" in script
            assert "LENYAY_DEVICE_FILE" in script

    def test_pas_de_suppression_avant_telechargement(self, ps1, sh):
        """L'installation en place ne doit pas être détruite avant d'avoir un
        remplacement valide en main."""
        for script in (ps1, sh):
            fetch = min(
                (script.index(m) for m in ("Invoke-WebRequest", "curl -fsSL", "DownloadFile")
                 if m in script),
                default=-1,
            )
            assert fetch > 0
            for destructive in ("Remove-Item (Join-Path $InstallDir \"code\")",
                                'rm -rf "$INSTALL_DIR/code"'):
                if destructive in script:
                    assert script.index(destructive) > fetch, destructive


class TestMessagesDErreur:
    def test_ps1_ne_ferme_pas_la_fenetre(self, ps1):
        """`irm | iex` exécute dans la session de l'utilisateur : un exit
        referme sa fenêtre et son message d'erreur avec."""
        assert "exit 1" not in ps1
        assert "throw" in ps1

    def test_python_manquant_donne_une_marche_a_suivre(self, ps1, sh):
        assert "winget install" in ps1
        assert "apt install" in sh


class TestDetectionPython:
    def test_pas_de_catch_vide(self, ps1):
        """Un catch vide transforme « Python présent mais bavard » en
        « Python manquant »."""
        assert not re.search(r"catch\s*\{\s*\}", ps1)

    def test_version_lue_sur_une_chaine_unique(self, ps1):
        # -match sur un tableau ne remplit pas $Matches : la sortie de
        # `--version` doit être aplatie en une seule chaîne au préalable.
        assert "Out-String" in ps1 or "-join" in ps1

    def test_python_juge_sur_sa_reponse_pas_sur_son_chemin(self, ps1):
        """Le raccourci-leurre du Microsoft Store et un vrai Python installé
        depuis le Store partagent le même dossier : seul `--version` tranche."""
        assert r"Python (\d+)\.(\d+)" in ps1
        assert '-like "*WindowsApps*"' not in ps1  # filtrer sur le chemin exclurait de vrais Python


class TestVerificationsPostInstallation:
    def test_toutes_les_etapes_sont_controlees(self, ps1):
        # venv, pip de base et pip llm : chaque étape native doit être testée.
        assert ps1.count("$LASTEXITCODE") >= 3

    def test_import_du_moteur_verifie(self, ps1, sh):
        """Une roue llama-cpp peut s'installer puis échouer à l'import
        (runtime MSVC absent, DLL en quarantaine)."""
        for script in (ps1, sh):
            assert "import llama_cpp" in script
