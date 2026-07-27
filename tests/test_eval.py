"""Tests de la suite d'évaluation — écrits AVANT l'implémentation (TDD).

Tout tourne sur répertoires temporaires : rien ne touche data/, la base
SQLite ni le coordinateur en marche.
"""

import json
from pathlib import Path

import pytest

import coordinator.verifier
from scripts.compare_evals import compare
from scripts.eval import (
    EVAL_CONFIG,
    append_partial,
    load_eval_set,
    render_markdown,
    run_eval,
    sanitize_name,
    sha256_file,
    summarize,
    verify,
    write_results,
)
from scripts.seed_eval import (
    check_contamination,
    normalize_prompt,
    pick_indices,
    write_eval_set,
)

# --- Aides -----------------------------------------------------------------


def _write_jsonl(path: Path, records: list[dict]) -> Path:
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )
    return path


def _fake_tasks(n: int) -> list[dict]:
    return [
        {"task_id": f"eval-{i:02d}", "prompt": f"probleme {i}", "expected_answer": str(i)}
        for i in range(n)
    ]


def _fake_result(eval_hash: str, corrects: dict[str, bool]) -> dict:
    details = [
        {"task_id": tid, "expected": "1", "extracted": "1" if ok else "9",
         "correct": ok, "trace": "#### x"}
        for tid, ok in corrects.items()
    ]
    n_ok = sum(corrects.values())
    return {
        "eval_set_hash": eval_hash,
        "score": {"correct": n_ok, "total": len(corrects),
                  "accuracy": n_ok / len(corrects)},
        "details": details,
    }


# --- Cœur de l'éval --------------------------------------------------------


class TestEvalCore:
    def test_verificateur_strictement_identique_au_coordinateur(self):
        # Pas de logique dupliquée : c'est LE même objet fonction.
        assert verify is coordinator.verifier.verify

    def test_config_deterministe(self):
        assert EVAL_CONFIG["temperature"] == 0.0
        assert EVAL_CONFIG["seed"] == 42

    def test_run_eval_score_et_details(self):
        tasks = _fake_tasks(4)

        def generate(prompt: str) -> str:
            i = int(prompt.rsplit(" ", 1)[1])
            return f"Raisonnement... #### {i if i % 2 == 0 else 999}"

        details = run_eval(tasks, generate)
        score = summarize(details)
        assert score == {"correct": 2, "total": 4, "accuracy": 0.5}
        assert details[0]["correct"] is True
        assert details[1]["correct"] is False
        assert details[1]["extracted"] == "999"
        assert details[1]["expected"] == "1"
        assert "####" in details[1]["trace"]

    def test_load_eval_set(self, tmp_path):
        path = _write_jsonl(tmp_path / "eval.jsonl", _fake_tasks(3))
        tasks = load_eval_set(path)
        assert len(tasks) == 3
        assert tasks[0]["task_id"] == "eval-00"

    def test_sha256_stable_et_sensible(self, tmp_path):
        a = tmp_path / "a.jsonl"
        b = tmp_path / "b.jsonl"
        a.write_text("contenu", encoding="utf-8")
        b.write_text("contenu", encoding="utf-8")
        assert sha256_file(a) == sha256_file(b)
        b.write_text("contenu!", encoding="utf-8")
        assert sha256_file(a) != sha256_file(b)

    def test_sanitize_name(self):
        assert sanitize_name("Qwen2.5 (q4_k_m).gguf") == "qwen2.5-q4_k_m-.gguf"
        assert "/" not in sanitize_name("a/b\\c")

    def test_write_results_fichiers_et_contenu(self, tmp_path):
        details = run_eval(_fake_tasks(2), lambda p: "#### 0")
        payload = {
            "model": "modele-test.gguf",
            "date": "2026-07-28",
            "eval_set_hash": "abc123",
            "config": EVAL_CONFIG,
            "score": summarize(details),
            "details": details,
        }
        json_path, md_path = write_results(
            tmp_path / "results", "modele-test", payload, date_str="2026-07-28"
        )
        assert json_path.name == "eval_modele-test_2026-07-28.json"
        assert md_path.name == "eval_modele-test_2026-07-28.md"
        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["score"]["correct"] == 1
        md = md_path.read_text(encoding="utf-8")
        assert "modele-test" in md and "1/2" in md

    def test_render_markdown_liste_les_echecs(self):
        details = run_eval(_fake_tasks(3), lambda p: "#### 0")
        payload = {
            "model": "m", "date": "d", "eval_set_hash": "h" * 64,
            "config": EVAL_CONFIG, "score": summarize(details), "details": details,
        }
        md = render_markdown(payload)
        assert "eval-01" in md and "eval-02" in md  # les deux échecs
        assert "1/3" in md


# --- Figeage du jeu d'éval -------------------------------------------------


class TestSeedEval:
    def test_pick_indices_deterministe_et_trie(self):
        a = pick_indices(5, 100, seed=42)
        assert a == pick_indices(5, 100, seed=42)
        assert a != pick_indices(5, 100, seed=43)
        assert a == sorted(a)
        assert len(set(a)) == 5

    def test_normalize_prompt_ignore_les_espaces(self):
        assert normalize_prompt("Alice  a\n3 pommes. ") == normalize_prompt("Alice a 3 pommes.")

    def test_contamination_detectee(self, tmp_path):
        tasks_path = _write_jsonl(tmp_path / "tasks.jsonl", [
            {"task_id": "gsm8k-train-0000", "prompt": "Alice a 3 pommes.", "expected_answer": "3"},
        ])
        records = [
            {"task_id": "gsm8k-test-0000", "prompt": "Bob a 5 poires.", "expected_answer": "5"},
            {"task_id": "gsm8k-test-0001", "prompt": "Alice  a 3 pommes.", "expected_answer": "3"},
        ]
        assert check_contamination(records, tasks_path) == ["gsm8k-test-0001"]

    def test_aucune_contamination(self, tmp_path):
        tasks_path = _write_jsonl(tmp_path / "tasks.jsonl", [
            {"task_id": "gsm8k-train-0000", "prompt": "Alice a 3 pommes.", "expected_answer": "3"},
        ])
        records = [{"task_id": "gsm8k-test-0000", "prompt": "Bob a 5 poires.", "expected_answer": "5"}]
        assert check_contamination(records, tasks_path) == []

    def test_write_eval_set_refuse_l_ecrasement(self, tmp_path):
        out = tmp_path / "eval_set.jsonl"
        records = _fake_tasks(2)
        write_eval_set(records, out)
        assert len(out.read_text(encoding="utf-8").splitlines()) == 2
        with pytest.raises(RuntimeError):
            write_eval_set(records, out)  # jeu figé UNE FOIS
        write_eval_set(_fake_tasks(3), out, force=True)
        assert len(out.read_text(encoding="utf-8").splitlines()) == 3


# --- Comparaison de deux évals ---------------------------------------------


class TestCompare:
    def test_delta_gagnes_perdus(self):
        res_a = _fake_result("h1", {"t1": True, "t2": False, "t3": False, "t4": True})
        res_b = _fake_result("h1", {"t1": True, "t2": True, "t3": False, "t4": False})
        cmp = compare(res_a, res_b)
        assert cmp["accuracy_a"] == 0.5 and cmp["accuracy_b"] == 0.5
        assert cmp["delta"] == 0.0
        assert [g["task_id"] for g in cmp["gained"]] == ["t2"]
        assert [l["task_id"] for l in cmp["lost"]] == ["t4"]

    def test_refus_si_jeux_differents(self):
        res_a = _fake_result("h1", {"t1": True})
        res_b = _fake_result("h2", {"t1": True})
        with pytest.raises(ValueError):
            compare(res_a, res_b)

    def test_refus_si_ensembles_de_problemes_differents(self):
        # Même jeu figé (même hash) mais une éval partielle (--limit) : le
        # delta comparerait des accuracies sur des ensembles différents.
        res_a = _fake_result("h1", {"t1": True, "t2": False, "t3": True})
        res_b = _fake_result("h1", {"t1": True})
        with pytest.raises(ValueError):
            compare(res_a, res_b)


class TestPartial:
    def test_append_partial_ecrit_du_jsonl_au_fil_de_l_eau(self, tmp_path):
        path = tmp_path / "eval.partial.jsonl"
        append_partial(path, {"task_id": "t1", "correct": True})
        append_partial(path, {"task_id": "t2", "correct": False})
        lines = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
        assert [l["task_id"] for l in lines] == ["t1", "t2"]
