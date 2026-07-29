"""Tests de l'accueil des nouveaux contributeurs (onboarding) — TDD.

Contrats :
- le mode mock ne peut JAMAIS viser un coordinateur distant (des traces
  simulées dans le corpus public le rendraient inutilisable) ;
- un diagnostic préalable dit clairement ce qui manque avant de lancer
  quoi que ce soit, plutôt que d'échouer au milieu d'un téléchargement.
"""

import pytest

from worker.preflight import (
    check_disk_space,
    check_python_version,
    check_coordinator,
    is_local_coordinator,
    format_report,
)


class TestCoordinateurLocal:
    @pytest.mark.parametrize("url", [
        "http://127.0.0.1:8000", "http://localhost:8000",
        "https://LOCALHOST:9000", "http://[::1]:8000", "http://0.0.0.0:8000",
    ])
    def test_local_reconnu(self, url):
        assert is_local_coordinator(url) is True

    @pytest.mark.parametrize("url", [
        "https://lenyay.example", "http://192.168.1.20:8000",
        "https://coord.lenyay.org:8443", "http://127.0.0.1.evil.com",
    ])
    def test_distant_reconnu(self, url):
        assert is_local_coordinator(url) is False


class TestDiagnostics:
    def test_python_version(self):
        ok, message = check_python_version()
        assert ok is True and "3." in message

    def test_espace_disque(self, tmp_path):
        ok, message = check_disk_space(tmp_path, needed_gb=0.001)
        assert ok is True and "Go" in message
        ok, message = check_disk_space(tmp_path, needed_gb=10**6)
        assert ok is False

    def test_coordinateur_injoignable_est_signale(self):
        ok, message = check_coordinator("http://127.0.0.1:9", timeout=0.5)
        assert ok is False and "injoignable" in message.lower()

    def test_rapport_lisible(self):
        report = format_report([("Python", True, "3.13"), ("Disque", False, "plein")])
        assert "OK" in report and "Python" in report
        assert "ÉCHEC" in report and "plein" in report
