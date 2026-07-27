"""Tests du vérificateur GSM8K — écrits AVANT l'implémentation (TDD).

Le vérificateur doit extraire le nombre final d'une trace de raisonnement et
le comparer à la réponse attendue, avec les tolérances du monde réel :
format "#### N" de GSM8K, virgules de milliers, point final, dollars,
réponse noyée dans une phrase, décimaux équivalents, négatifs.
"""

import pytest

from coordinator.verifier import extract_final_answer, verify


# --- Extraction ------------------------------------------------------------


class TestExtraction:
    def test_format_gsm8k_standard(self):
        assert extract_final_answer("Le calcul donne 8 * 9 = 72.\n#### 72") == "72"

    def test_virgule_de_milliers_apres_hash(self):
        assert extract_final_answer("#### 1,000") == "1000"

    def test_espace_de_milliers_apres_hash(self):
        assert extract_final_answer("#### 1 000") == "1000"

    def test_point_final_sans_hash(self):
        assert extract_final_answer("So the answer is 42.") == "42"

    def test_reponse_noyee_prend_le_dernier_nombre(self):
        trace = "He buys 12 apples and eats 5, so he has 7"
        assert extract_final_answer(trace) == "7"

    def test_dollars_et_virgules(self):
        assert extract_final_answer("The total cost is #### $5,250") == "5250"

    def test_hash_prioritaire_sur_le_reste_du_texte(self):
        trace = "12 + 6 = 18\n#### 18 out of 20 students"
        assert extract_final_answer(trace) == "18"

    def test_dernier_hash_gagne(self):
        trace = "#### 10\nNon, je corrige :\n#### 12"
        assert extract_final_answer(trace) == "12"

    def test_negatif(self):
        assert extract_final_answer("The temperature is #### -4") == "-4"

    def test_aucun_nombre(self):
        assert extract_final_answer("Je ne sais pas résoudre ce problème.") is None

    def test_trace_vide(self):
        assert extract_final_answer("") is None


# --- Verdict ---------------------------------------------------------------


class TestVerify:
    @pytest.mark.parametrize(
        "trace,expected",
        [
            ("Le résultat est 8 * 9 = 72.\n#### 72", "72"),
            ("#### 1,000", "1000"),
            ("So the answer is 42.", "42"),
            ("After the sale, Josh has $12 left.", "12"),
            ("#### 3.50", "3.5"),  # décimaux équivalents
            ("#### -4", "-4"),
            ("#### 20%", "20"),
        ],
    )
    def test_traces_correctes_acceptees(self, trace, expected):
        accepted, extracted = verify(trace, expected)
        assert accepted, f"extrait={extracted!r}, attendu={expected!r}"

    @pytest.mark.parametrize(
        "trace,expected",
        [
            ("He buys 12 apples and eats 5", "7"),  # mauvais dernier nombre
            ("#### 10", "12"),
            ("Je ne sais pas.", "10"),  # aucun nombre
            ("", "5"),
        ],
    )
    def test_traces_incorrectes_rejetees(self, trace, expected):
        accepted, _ = verify(trace, expected)
        assert not accepted

    def test_verdict_renvoie_le_nombre_extrait(self):
        accepted, extracted = verify("#### 1,000", "1000")
        assert accepted and extracted == "1000"

    def test_aucun_nombre_renvoie_none(self):
        accepted, extracted = verify("aucune idée", "3")
        assert not accepted and extracted is None
