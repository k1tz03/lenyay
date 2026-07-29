"""Vérification des tâches de code : les tests unitaires font foi.

Le principe est le même que pour les maths — juste ou faux, sans arbitre —
mais l'exécution de code produit par des machines inconnues est un risque en
soi. Défense en trois couches, du moins cher au plus sûr :

1. filtrage statique : les motifs dangereux (système, réseau, fichiers) sont
   écartés AVANT toute exécution — un modèle honnête n'en a jamais besoin
   pour une fonction pure ;
2. exécution en sous-processus isolé (`python -I` : pas de site-packages, pas
   de variables d'environnement héritées), répertoire temporaire jetable,
   délai strict, sortie bornée ;
3. limites de ressources POSIX (mémoire, CPU, taille de fichier) quand la
   plateforme les offre — le VPS de production est sous Linux.

Ce n'est PAS une sandbox parfaite : le déploiement public doit ajouter une
isolation système (conteneur, utilisateur dédié sans droits). C'est documenté
dans FEUILLE-DE-ROUTE.md et ça conditionne l'ouverture du palier code.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from common import config

# Ce qu'une fonction pure n'a aucune raison de faire. Liste courte et frappée
# large : un faux positif coûte une tentative, un faux négatif coûte le serveur.
_BANNED = re.compile(
    r"\b(import\s+(os|sys|subprocess|socket|shutil|pathlib|ctypes|signal|threading|"
    r"multiprocessing|importlib|urllib|http|requests|pickle|marshal)\b"
    r"|from\s+(os|sys|subprocess|socket|shutil|pathlib|ctypes|signal|threading|"
    r"multiprocessing|importlib|urllib|http|requests|pickle|marshal)\b"
    r"|__import__|open\s*\(|exec\s*\(|eval\s*\(|compile\s*\(|globals\s*\(|"
    r"breakpoint\s*\(|input\s*\()"
)

_FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)

# Le lot exécuté : la solution, puis les tests, puis un marqueur que seul un
# passage complet peut imprimer.
_SENTINEL = "LENYAY_TESTS_OK"


def extract_code(trace: str) -> str | None:
    """Le premier bloc ```python de la réponse ; à défaut, le texte entier
    s'il ressemble à du code (il définit une fonction)."""
    match = _FENCE.search(trace)
    if match:
        return match.group(1).strip()
    if "def " in trace and "```" not in trace:
        return trace.strip()
    return None


def _resource_limits() -> None:  # pragma: no cover — POSIX uniquement
    import resource

    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (config.CODE_TIMEOUT,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NPROC, (16,) * 2)


def verify_code(trace: str, tests: str) -> tuple[bool, str | None]:
    """Renvoie (accepté, détail) — détail ∈ {tests:ok, code:absent,
    code:refuse, code:trop-long, tests:echec, tests:timeout, tests:erreur}."""
    code = extract_code(trace)
    if code is None:
        return False, "code:absent"
    if len(code) > config.CODE_MAX_CHARS:
        return False, "code:trop-long"
    if _BANNED.search(code):
        return False, "code:refuse"

    runner = f"{code}\n\n{tests}\nprint({_SENTINEL!r})\n"
    kwargs: dict = {}
    if sys.platform != "win32":  # pragma: no cover — exercé sur le VPS
        kwargs["preexec_fn"] = _resource_limits
    try:
        with tempfile.TemporaryDirectory(prefix="lenyay-code-") as tmp:
            script = Path(tmp) / "runner.py"
            script.write_text(runner, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-I", "-B", str(script)],
                capture_output=True, text=True, cwd=tmp,
                timeout=config.CODE_TIMEOUT, **kwargs,
            )
    except subprocess.TimeoutExpired:
        return False, "tests:timeout"
    except OSError:
        return False, "tests:erreur"

    if proc.returncode == 0 and _SENTINEL in proc.stdout:
        return True, "tests:ok"
    return False, "tests:echec"
