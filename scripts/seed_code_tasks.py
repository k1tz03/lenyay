"""Génère data/code_tasks.jsonl — le premier catalogue de tâches de code.

24 fonctions pures, énoncées en français, vérifiées par des tests que le
worker ne voit jamais (ils jouent le rôle de la réponse attendue des maths).
Chaque jeu de tests inclut des cas limites : une solution naïve qui ignore
l'énoncé doit échouer.

Usage : python scripts/seed_code_tasks.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import config  # noqa: E402

TASKS = [
    ("inverser_mots",
     "Écris `inverser_mots(phrase)` qui renvoie la phrase avec l'ordre des mots "
     "inversé. Les mots sont séparés par des espaces simples.",
     'assert inverser_mots("le chat dort") == "dort chat le"\n'
     'assert inverser_mots("bonjour") == "bonjour"\n'
     'assert inverser_mots("") == ""\n'),
    ("deuxieme_plus_grand",
     "Écris `deuxieme_plus_grand(nombres)` qui renvoie le deuxième plus grand "
     "élément d'une liste d'entiers distincts, ou None s'il y a moins de deux "
     "éléments.",
     "assert deuxieme_plus_grand([3, 9, 1, 7]) == 7\n"
     "assert deuxieme_plus_grand([5]) is None\n"
     "assert deuxieme_plus_grand([]) is None\n"
     "assert deuxieme_plus_grand([2, 1]) == 1\n"),
    ("est_palindrome",
     "Écris `est_palindrome(texte)` qui renvoie True si le texte est un "
     "palindrome en ignorant la casse, les espaces et les accents non traités "
     "(compare simplement les lettres et chiffres, en minuscules).",
     'assert est_palindrome("Esope reste ici et se repose".replace(" ", "")) in (True, False)\n'
     'assert est_palindrome("kayak") is True\n'
     'assert est_palindrome("Kayak") is True\n'
     'assert est_palindrome("a b a") is True\n'
     'assert est_palindrome("python") is False\n'),
    ("compte_voyelles",
     "Écris `compte_voyelles(texte)` qui compte les voyelles a, e, i, o, u, y "
     "(minuscules et majuscules).",
     'assert compte_voyelles("Python") == 2\n'
     'assert compte_voyelles("") == 0\n'
     'assert compte_voyelles("AEIOUY") == 6\n'),
    ("aplatir",
     "Écris `aplatir(listes)` qui transforme une liste de listes en une seule "
     "liste, dans l'ordre.",
     "assert aplatir([[1, 2], [3], []]) == [1, 2, 3]\n"
     "assert aplatir([]) == []\n"
     "assert aplatir([[], []]) == []\n"),
    ("fusion_triee",
     "Écris `fusion_triee(a, b)` qui fusionne deux listes déjà triées en une "
     "liste triée, sans utiliser sort() ni sorted().",
     "import re as _re\nimport inspect as _inspect\n"
     "assert fusion_triee([1, 3], [2, 4]) == [1, 2, 3, 4]\n"
     "assert fusion_triee([], [1]) == [1]\n"
     "assert fusion_triee([5, 6], []) == [5, 6]\n"
     "_src = _inspect.getsource(fusion_triee)\n"
     "assert not _re.search(r'\\bsorted?\\s*\\(', _src), 'tri interdit'\n"),
    ("chiffres_romains",
     "Écris `chiffres_romains(n)` qui convertit un entier de 1 à 3999 en "
     "chiffres romains.",
     'assert chiffres_romains(9) == "IX"\n'
     'assert chiffres_romains(14) == "XIV"\n'
     'assert chiffres_romains(1990) == "MCMXC"\n'
     'assert chiffres_romains(3999) == "MMMCMXCIX"\n'),
    ("anagrammes",
     "Écris `anagrammes(a, b)` qui renvoie True si les deux chaînes sont des "
     "anagrammes (mêmes lettres, casse ignorée, espaces ignorés).",
     'assert anagrammes("chien", "niche") is True\n'
     'assert anagrammes("Marie", "aimer") is True\n'
     'assert anagrammes("chat", "chats") is False\n'),
    ("premiers_jusqu_a",
     "Écris `premiers_jusqu_a(n)` qui renvoie la liste des nombres premiers "
     "inférieurs ou égaux à n.",
     "assert premiers_jusqu_a(10) == [2, 3, 5, 7]\n"
     "assert premiers_jusqu_a(2) == [2]\n"
     "assert premiers_jusqu_a(1) == []\n"),
    ("rotation_liste",
     "Écris `rotation_liste(elements, k)` qui fait tourner la liste de k crans "
     "vers la droite (k peut dépasser la longueur).",
     "assert rotation_liste([1, 2, 3, 4], 1) == [4, 1, 2, 3]\n"
     "assert rotation_liste([1, 2, 3], 5) == [2, 3, 1]\n"
     "assert rotation_liste([], 3) == []\n"),
    ("profondeur_parentheses",
     "Écris `profondeur_parentheses(s)` qui renvoie la profondeur maximale "
     "d'imbrication de parenthèses, ou -1 si elles sont mal appariées.",
     'assert profondeur_parentheses("(a(b)c)") == 2\n'
     'assert profondeur_parentheses("()()") == 1\n'
     'assert profondeur_parentheses("(()") == -1\n'
     'assert profondeur_parentheses("") == 0\n'),
    ("somme_chiffres",
     "Écris `somme_chiffres(n)` qui additionne les chiffres d'un entier positif "
     "jusqu'à obtenir un seul chiffre (racine numérique).",
     "assert somme_chiffres(942) == 6\n"
     "assert somme_chiffres(9) == 9\n"
     "assert somme_chiffres(999999999) == 9\n"),
    ("intervalle_commun",
     "Écris `intervalle_commun(a, b)` où a et b sont des tuples (début, fin) : "
     "renvoie le tuple de leur intersection, ou None si elle est vide.",
     "assert intervalle_commun((1, 5), (3, 8)) == (3, 5)\n"
     "assert intervalle_commun((1, 2), (3, 4)) is None\n"
     "assert intervalle_commun((1, 3), (3, 5)) == (3, 3)\n"),
    ("mots_frequents",
     "Écris `mots_frequents(texte, k)` qui renvoie les k mots les plus "
     "fréquents (casse ignorée), triés par fréquence décroissante puis ordre "
     "alphabétique.",
     'assert mots_frequents("le chat et le chien et le rat", 2) == ["le", "et"]\n'
     'assert mots_frequents("a b b a c", 3) == ["a", "b", "c"]\n'),
    ("code_cesar",
     "Écris `code_cesar(texte, decalage)` qui décale chaque lettre a-z/A-Z de "
     "`decalage` positions (les autres caractères restent).",
     'assert code_cesar("abc", 2) == "cde"\n'
     'assert code_cesar("xyz", 3) == "abc"\n'
     'assert code_cesar("Ab-z", 1) == "Bc-a"\n'),
    ("pgcd",
     "Écris `pgcd(a, b)` qui calcule le plus grand commun diviseur de deux "
     "entiers positifs, sans importer math.",
     "assert pgcd(12, 18) == 6\n"
     "assert pgcd(7, 13) == 1\n"
     "assert pgcd(0, 5) == 5\n"),
    ("tri_selection",
     "Écris `tri_selection(nombres)` qui trie une liste par sélection, sans "
     "sort() ni sorted(), et renvoie une NOUVELLE liste (l'originale ne doit "
     "pas être modifiée).",
     "import inspect as _inspect, re as _re\n"
     "_orig = [3, 1, 2]\n"
     "assert tri_selection(_orig) == [1, 2, 3]\n"
     "assert _orig == [3, 1, 2], 'liste originale modifiée'\n"
     "assert tri_selection([]) == []\n"
     "_src = _inspect.getsource(tri_selection)\n"
     "assert not _re.search(r'\\bsorted?\\s*\\(', _src), 'tri interdit'\n"),
    ("balises_equilibrees",
     "Écris `balises_equilibrees(s)` qui vérifie que (), [] et {} sont "
     "correctement appariées et imbriquées dans la chaîne.",
     'assert balises_equilibrees("([]{})") is True\n'
     'assert balises_equilibrees("([)]") is False\n'
     'assert balises_equilibrees("(") is False\n'
     'assert balises_equilibrees("") is True\n'),
    ("compression",
     "Écris `compression(s)` qui remplace les répétitions consécutives par "
     "lettre+nombre (\"aaabb\" → \"a3b2\"), en gardant la lettre seule si elle "
     "n'apparaît qu'une fois.",
     'assert compression("aaabb") == "a3b2"\n'
     'assert compression("abc") == "abc"\n'
     'assert compression("") == ""\n'
     'assert compression("aab") == "a2b"\n'),
    ("moyenne_glissante",
     "Écris `moyenne_glissante(valeurs, k)` qui renvoie la liste des moyennes "
     "des fenêtres de k éléments consécutifs.",
     "assert moyenne_glissante([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]\n"
     "assert moyenne_glissante([1, 2], 3) == []\n"
     "assert moyenne_glissante([5], 1) == [5.0]\n"),
    ("nombre_en_lettres",
     "Écris `nombre_en_lettres(n)` qui écrit un entier de 0 à 99 en français "
     "simplifié : unités (\"trois\"), dizaines (\"vingt-trois\", \"soixante-dix\", "
     "\"quatre-vingt-onze\"). Utilise des tirets partout, sans « et ».",
     'assert nombre_en_lettres(0) == "zéro"\n'
     'assert nombre_en_lettres(23) == "vingt-trois"\n'
     'assert nombre_en_lettres(71) == "soixante-onze"\n'
     'assert nombre_en_lettres(80) == "quatre-vingts"\n'),
    ("chemin_simplifie",
     "Écris `chemin_simplifie(chemin)` qui normalise un chemin Unix : gère "
     "\".\", \"..\", et les \"//\" ; le résultat commence par \"/\".",
     'assert chemin_simplifie("/a/./b/../c") == "/a/c"\n'
     'assert chemin_simplifie("/../") == "/"\n'
     'assert chemin_simplifie("/a//b") == "/a/b"\n'),
    ("suite_conway",
     "Écris `suite_conway(depart, n)` qui applique n fois la transformation "
     "« lire et dire » (look-and-say) à la chaîne de chiffres `depart`.",
     'assert suite_conway("1", 1) == "11"\n'
     'assert suite_conway("1", 3) == "1211"\n'
     'assert suite_conway("22", 1) == "22"\n'),
    ("entiers_manquants",
     "Écris `entiers_manquants(nombres)` qui renvoie la liste triée des entiers "
     "absents entre le min et le max de la liste.",
     "assert entiers_manquants([1, 4, 2]) == [3]\n"
     "assert entiers_manquants([7, 7]) == []\n"
     "assert entiers_manquants([5, 1]) == [2, 3, 4]\n"),
]


def main() -> None:
    out = config.CODE_TASKS_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, (name, prompt, tests) in enumerate(TASKS):
            f.write(json.dumps({
                "task_id": f"code-{i:04d}-{name}",
                "kind": "code",
                "prompt": prompt,
                "tests": tests,
            }, ensure_ascii=False) + "\n")
    print(f"{len(TASKS)} tâches de code écrites dans {out}")


if __name__ == "__main__":
    main()
