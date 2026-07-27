"""Compare deux résultats d'éval : delta de score, problèmes gagnés/perdus.

    .venv/Scripts/python.exe scripts/compare_evals.py results/eval_A.json results/eval_B.json

Refuse de comparer deux évals qui ne portent pas sur le même jeu figé
(hash différent) : la comparaison n'aurait aucun sens.
"""

import argparse
import json
import sys
from pathlib import Path


def compare(res_a: dict, res_b: dict) -> dict:
    if res_a["eval_set_hash"] != res_b["eval_set_hash"]:
        raise ValueError(
            "Les deux évals ne portent pas sur le même jeu figé "
            f"({res_a['eval_set_hash'][:12]}… vs {res_b['eval_set_hash'][:12]}…) : "
            "comparaison refusée."
        )
    by_id_a = {d["task_id"]: d for d in res_a["details"]}
    by_id_b = {d["task_id"]: d for d in res_b["details"]}
    if set(by_id_a) != set(by_id_b):
        raise ValueError(
            "Les deux évals ne couvrent pas les mêmes problèmes "
            f"({len(by_id_a)} vs {len(by_id_b)}) — l'une est probablement une "
            "éval partielle (--limit) : comparaison refusée."
        )
    common = [tid for tid in by_id_a if tid in by_id_b]

    gained, lost = [], []
    for tid in common:
        a, b = by_id_a[tid], by_id_b[tid]
        entry = {
            "task_id": tid,
            "expected": b["expected"],
            "extracted_before": a["extracted"],
            "extracted_after": b["extracted"],
        }
        if not a["correct"] and b["correct"]:
            gained.append(entry)
        elif a["correct"] and not b["correct"]:
            lost.append(entry)

    return {
        "accuracy_a": res_a["score"]["accuracy"],
        "accuracy_b": res_b["score"]["accuracy"],
        "delta": res_b["score"]["accuracy"] - res_a["score"]["accuracy"],
        "common": len(common),
        "gained": gained,
        "lost": lost,
    }


def render_markdown(cmp: dict, label_a: str, label_b: str) -> str:
    lines = [
        f"# Comparaison : {label_a} → {label_b}",
        "",
        f"**{cmp['accuracy_a']:.1%} → {cmp['accuracy_b']:.1%} "
        f"(delta : {cmp['delta']:+.1%} sur {cmp['common']} problèmes communs)**",
        "",
        f"## Gagnés ({len(cmp['gained'])})",
        "",
    ]
    for g in cmp["gained"]:
        lines.append(f"- `{g['task_id']}` : {g['extracted_before']} → "
                     f"{g['extracted_after']} (attendu {g['expected']})")
    lines += ["", f"## Perdus ({len(cmp['lost'])})", ""]
    for l in cmp["lost"]:
        lines.append(f"- `{l['task_id']}` : {l['extracted_before']} → "
                     f"{l['extracted_after']} (attendu {l['expected']})")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare deux résultats d'éval")
    parser.add_argument("baseline", type=Path, help="JSON de l'éval de référence")
    parser.add_argument("candidate", type=Path, help="JSON de l'éval à comparer")
    parser.add_argument("--out", type=Path, default=None,
                        help="écrire aussi le rapport markdown dans ce fichier (UTF-8)")
    args = parser.parse_args()

    # Windows : stdout redirigé vers un fichier est en cp1252 par défaut, qui
    # ne connaît pas « → » ; on force l'UTF-8 pour que « > rapport.md » marche.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    res_a = json.loads(args.baseline.read_text(encoding="utf-8"))
    res_b = json.loads(args.candidate.read_text(encoding="utf-8"))
    try:
        result = compare(res_a, res_b)
    except ValueError as exc:
        sys.exit(str(exc))
    report = render_markdown(result, res_a.get("label", args.baseline.stem),
                             res_b.get("label", args.candidate.stem))
    if args.out is not None:
        args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
