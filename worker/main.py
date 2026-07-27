"""Worker Essaim — boucle : demander du travail → générer → soumettre → recommencer.

Lancement :  python -m worker.main [--mock]
Mode mock :  ESSAIM_MOCK=1 (ou --mock) — traces simulées, ~30 % correctes.
Arrêt     :  Ctrl+C (résumé de session affiché).
"""

import argparse
import json
import logging
import os
import platform
import sys
import time

import httpx

log = logging.getLogger("essaim.worker")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Worker Essaim")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="équivalent de ESSAIM_MOCK=1 (pratique sous PowerShell)",
    )
    return parser.parse_args()


def _ensure_registered(client, device_file) -> dict:
    """Charge l'identité persistée, ou s'enregistre au premier lancement."""
    if device_file.exists():
        identity = json.loads(device_file.read_text(encoding="utf-8"))
        client.set_api_key(identity["api_key"])
        log.info("Identité chargée : %s (%s…)", identity["device_name"], identity["device_id"][:8])
        return identity
    device_name = f"worker-{platform.node() or 'inconnu'}"
    creds = client.register(device_name)
    identity = {
        "device_id": creds.device_id,
        "api_key": creds.api_key,
        "device_name": device_name,
    }
    device_file.write_text(json.dumps(identity, indent=2), encoding="utf-8")
    log.info("Appareil enregistré : %s (%s…) — clé persistée dans %s",
             device_name, creds.device_id[:8], device_file)
    return identity


def _submit_and_log(client, submissions, stats) -> list:
    """Soumet un lot, journalise chaque verdict, renvoie les tâches refusées."""
    response = client.submit(submissions)
    verdict_by_id = {v.task_id: v for v in response.verdicts}
    rejected = []
    for sub in submissions:
        verdict = verdict_by_id.get(sub.task_id)
        if verdict is not None and verdict.accepted:
            stats["accepted"] += 1
            log.info("  ✓ %s accepté (réponse : %s)", sub.task_id, verdict.extracted_answer)
        else:
            extracted = verdict.extracted_answer if verdict else None
            rejected.append(sub.task_id)
            log.info("  ✗ %s refusé (extrait : %s)", sub.task_id, extracted)
    stats["credits"] = response.total_credits
    return rejected


def _ensure_registered_with_retry(client, device_file) -> dict:
    """Comme _ensure_registered, mais survit à un coordinateur injoignable."""
    while True:
        try:
            return _ensure_registered(client, device_file)
        except httpx.RequestError as exc:
            log.warning(
                "Coordinateur injoignable (%s) — nouvel essai dans 5 s",
                type(exc).__name__,
            )
            time.sleep(5)


def run() -> None:
    args = _parse_args()
    if args.mock:
        os.environ["ESSAIM_MOCK"] = "1"

    # Import après le réglage éventuel de ESSAIM_MOCK par --mock.
    from common import config
    from common.schemas import ResultSubmission
    from worker.client import CoordinatorClient
    from worker.generation import make_generator

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                        datefmt="%H:%M:%S")

    client = CoordinatorClient(config.COORDINATOR_URL)
    generator = make_generator()
    mode = "MOCK" if config.MOCK_MODE else "RÉEL"

    stats = {"generated": 0, "accepted": 0, "credits": 0}
    tasks_processed = 0
    identity = {"device_name": "non enregistré"}
    try:
        identity = _ensure_registered_with_retry(client, config.DEVICE_FILE)
        log.info("Worker prêt — mode %s, coordinateur %s", mode, config.COORDINATOR_URL)

        # La boucle doit survivre à la nuit : toute erreur réseau ou HTTP se
        # solde par une pause puis un nouvel essai, jamais par un crash.
        while True:
            try:
                batch = client.get_work(config.BATCH_SIZE)

                if not batch.tasks:
                    log.info("Aucune tâche disponible — pause de 10 s")
                    time.sleep(10)
                    continue

                log.info("Lot de %d tâche(s) reçu", len(batch.tasks))

                # Tentative 1 pour tout le lot.
                submissions = []
                for task in batch.tasks:
                    trace = generator.generate(task)
                    stats["generated"] += 1
                    submissions.append(
                        ResultSubmission(task_id=task.task_id, trace=trace, attempt=1)
                    )
                rejected_ids = _submit_and_log(client, submissions, stats)

                # Tentatives suivantes uniquement pour les refusées (le verdict
                # vient du coordinateur : le worker ne peut pas vérifier seul).
                task_by_id = {t.task_id: t for t in batch.tasks}
                attempt = 2
                while rejected_ids and attempt <= config.MAX_ATTEMPTS:
                    retries = []
                    for task_id in rejected_ids:
                        trace = generator.generate(task_by_id[task_id])
                        stats["generated"] += 1
                        retries.append(
                            ResultSubmission(task_id=task_id, trace=trace, attempt=attempt)
                        )
                    log.info("Tentative %d pour %d tâche(s)", attempt, len(retries))
                    rejected_ids = _submit_and_log(client, retries, stats)
                    attempt += 1

                tasks_processed += len(batch.tasks)
                if config.MAX_TASKS and tasks_processed >= config.MAX_TASKS:
                    log.info("Limite ESSAIM_MAX_TASKS atteinte (%d tâches)", tasks_processed)
                    break

            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 401:
                    log.warning("Clé API refusée — ré-enregistrement de l'appareil")
                    config.DEVICE_FILE.unlink(missing_ok=True)
                    identity = _ensure_registered_with_retry(client, config.DEVICE_FILE)
                else:
                    log.warning(
                        "Erreur HTTP %d du coordinateur — nouvel essai dans 5 s",
                        exc.response.status_code,
                    )
                    time.sleep(5)
            except httpx.RequestError as exc:
                log.warning(
                    "Coordinateur injoignable (%s) — nouvel essai dans 5 s",
                    type(exc).__name__,
                )
                time.sleep(5)
    except KeyboardInterrupt:
        log.info("Arrêt demandé (Ctrl+C)")
    finally:
        client.close()
        log.info(
            "— Résumé de session : %d trace(s) générée(s), %d acceptée(s), "
            "%d crédit(s) au total pour %s —",
            stats["generated"], stats["accepted"], stats["credits"],
            identity["device_name"],
        )


if __name__ == "__main__":
    run()
