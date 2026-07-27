# Essaim — Feuille de route & prompt de démarrage

**Nom de code : Leny's life**

## La vision en trois lignes

Un réseau coopératif où les PC et téléphones des membres améliorent un modèle IA
commun la nuit (rollouts vérifiés + fine-tuning fédéré), gagnent des crédits
d'usage non transférables, et où l'inférence locale reste gratuite à vie.
Preuve de légitimité visée : « N appareils ont produit une amélioration mesurable
entre v0.1 et v0.2, évals publiques à l'appui. »

## Décisions déjà actées (ne pas rouvrir pendant le dev)

* Desktop d'abord (Windows/Linux/macOS), Android ensuite, iOS en dernier
* On hérite d'un modèle ouvert, on ne pré-entraîne jamais ; v0 : un 1-3B instruct en GGUF via llama.cpp
* Première tâche de l'essaim : rollouts mathématiques vérifiables (GSM8K) — pure inférence, vérification par réponse exacte
* Crédits non transférables, jamais convertibles en cash — une simple table en base
* Coordination minuscule : FastAPI + SQLite (Postgres en phase 2), poids signés en phase 2
* Python partout en v0 : la vitesse d'itération prime, l'optimisation viendra après la preuve

## Feuille de route (rythme : soirées)

### Phase 0 — L'essaim minimal (semaines 1-3) ← ON COMMENCE ICI

Objectif : 2 machines qui produisent des rollouts vérifiés pendant une nuit,
crédits comptés, dashboard qui l'affiche.
Livrables : coordinateur (API + base), worker desktop, vérificateur GSM8K, page de stats.
Critère de succès : coordinateur + worker lancés en 2 commandes → 100 rollouts
vérifiés sans intervention. Budget : 0 CHF.

### Phase 1 — La boucle d'apprentissage (semaines 4-8)

Objectif : transformer les traces acceptées en amélioration mesurable — c'est LA
démo fondatrice. Livrables : export du dataset filtré, fine-tuning LoRA sur GPU
loué (50-150 CHF), suite d'évals sur jeu de test tenu à l'écart, publication
v0.2, comparatif public v0.1 vs v0.2. Critère de succès : delta positif
reproductible → matériau du writeup et du dossier NLnet.
En parallèle : recruter 4-5 copains avec un PC.

### Phase 2 — Confiance & distribution (semaines 9-14)

Poids signés (les workers refusent tout modèle non signé), auto-update des
workers, clé API par appareil, re-vérification aléatoire d'un échantillon de
rollouts (anti-triche v1), passage SQLite → Postgres, premier VPS.

### Phase 3 — Android & ouverture (mois 4-6)

Worker Android (service de premier plan : uniquement en charge + WiFi + inactif),
onboarding simple, repo public + writeup soigné, candidatures NLnet + crédits
cloud (Microsoft for Startups, AWS Activate).

### Phase 4 — L'économie (mois 6+)

Compteur/quota façon autoconsommation, requêtes « gros modèle » servies par les
PC des membres, abonnement au-delà du quota, structure association (le commun) +
société opératrice.

## Prompt de démarrage pour Claude Code — Session 1

```
# Projet Essaim — Session 1 : le squelette de l'essaim

## Contexte
Je construis un réseau de calcul coopératif : les ordinateurs des membres
génèrent la nuit des "rollouts" (résolutions de problèmes par un petit LLM
local), un coordinateur central vérifie les réponses, crédite les contributeurs
et archive les traces correctes, qui serviront plus tard de données de
fine-tuning. Aujourd'hui on construit le squelette local de bout en bout :
coordinateur + worker + vérification + crédits + mini-dashboard, le tout
exécutable sur ma seule machine.

## Stack imposée
- Python 3.11+, un seul repo, dépendances gérées avec uv (sinon pip + requirements.txt)
- Coordinateur : FastAPI + SQLite
- Worker : script Python autonome qui parle au coordinateur en HTTP
- Inférence : llama-cpp-python avec un modèle GGUF instruct de 1 à 3B téléchargé
  depuis Hugging Face (modèle récent, petit, licence permissive, ex. famille
  Qwen ou Llama 3.2 ; téléchargement automatique au premier lancement)
- Mode mock : variable d'env ESSAIM_MOCK=1 → le worker renvoie des réponses
  simulées (dont ~30 % correctes) sans charger de modèle
- Tâches : 200 problèmes issus de GSM8K — chargés une fois via le package
  `datasets` et figés dans data/tasks.jsonl avec la réponse attendue

## Architecture attendue
essaim/
  coordinator/   # FastAPI : endpoints + logique
  worker/        # boucle du client
  common/        # schémas partagés (pydantic)
  data/          # tasks.jsonl généré, traces acceptées
  scripts/       # seed_tasks.py, etc.
  README.md

## Fonctionnalités de la session
1. Coordinateur :
   - POST /devices/register → device_id + api_key
   - GET /work → lot de N tâches (prompt + task_id, JAMAIS la réponse attendue)
   - POST /results → traces soumises ; vérification : extraction du nombre final
     de la trace et comparaison à la réponse attendue (tolérance : espaces,
     virgules, format "#### N" de GSM8K)
   - Crédits : +1 par trace correcte ; tout est journalisé (device, task, trace,
     verdict, timestamp)
   - Les traces CORRECTES sont archivées en JSONL dans data/accepted/
   - GET /stats + une page HTML minimaliste sur "/" : appareils vus, rollouts
     totaux, taux d'acceptation, top contributeurs
2. Worker :
   - S'enregistre au premier lancement et persiste sa clé en local
   - Boucle : demande du travail → génère (température 0.8, 2 tentatives par
     problème) → soumet → recommence
   - S'arrête proprement sur Ctrl+C ; log lisible de sa production
3. Qualité :
   - Tests pytest sur le vérificateur (cas piégeux : "1,000", "42.", réponse
     noyée dans une phrase)
   - README : installation, lancement en 2 terminaux, mode mock, schéma ASCII

## Hors périmètre (ne pas construire aujourd'hui)
Pas d'entraînement, pas de mobile, pas de blockchain, pas d'auth avancée,
pas de Docker, pas de file distribuée, pas d'optimisation de perf.

## Definition of done
En 2 terminaux : le coordinateur tourne, le worker s'enregistre, traite au moins
20 tâches en mode mock, les crédits s'incrémentent, la page "/" affiche les
stats — puis la même chose en mode réel avec le vrai modèle sur au moins 5 tâches.
```

## Conseils pour les sessions Claude Code

* Une session = un livrable de la phase, pas plus — résiste à l'envie d'ajouter
* Toujours proposer un plan d'abord, valider, puis exécuter
* Commits petits et README à jour à chaque session
* Fin de session : « comment je teste ça en 2 commandes ? »
* Garder ce fichier à la racine du repo : coller la section « Décisions déjà
  actées » en tête de chaque nouvelle session pour éviter de rouvrir les débats
