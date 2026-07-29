# Comment Lenyay apprend — et pourquoi pas « de tout »

Objectif visé : que le modèle s'améliore en continu à partir de l'usage réel,
sans jamais se dégrader ni trahir la vie privée des membres. Ce document
explique la mécanique et, surtout, ce qu'on refuse de faire.

## Ce qu'on NE fait pas : imiter le chat brut

Réentraîner un modèle sur ses propres réponses **non vérifiées** le fait
**régresser** — c'est l'effondrement de modèle (Shumailov et al., 2023). Il
réapprend et amplifie ses erreurs. On l'a déjà mesuré ici : v0.2, entraînée
sur des problèmes qu'elle savait déjà résoudre, est passée de 71,5 % à 71,0 %.
Sur des conversations libres, sans vérité de référence, ce serait bien pire.

Donc : **aucune réponse n'entre dans l'entraînement du seul fait qu'elle a été
produite.**

## Les deux sources propres

### 1. Le vérifié — vrai par construction

Maths (réponse exacte) et code (tests unitaires au vert). Le serveur sait si
c'est juste ; ce corpus n'a besoin ni de consentement ni de note, il est
correct par définition. C'est le cœur, déjà en production.

### 2. Le consenti et apprécié — de la préférence humaine

Une conversation ne devient donnée d'entraînement que si elle franchit
**trois portes**, dans cet ordre :

1. **Consentement** — le membre a explicitement coché « aider à améliorer
   Lenyay » (désactivé par défaut, révocable à tout moment). Techniquement :
   `accounts.learn_opt_in`.
2. **Retour positif** — la réponse a reçu un 👍 du membre. Un humain a validé
   que la réponse est bonne. Techniquement : table `feedback`, `rating='up'`.
3. **Nettoyage** — e-mails, téléphones, IBAN, longues suites de chiffres sont
   retirés avant toute conservation (`coordinator/scrub.py`). Barrière large :
   on préfère effacer un peu trop que laisser fuir un identifiant.

Le tout est de la **donnée de préférence** (« cette réponse-là est bonne »),
pas de l'imitation aveugle. Export : `python scripts/export_dataset.py
--with-conversations` — les exemples issus du chat sont marqués
`"source": "conversation"` pour rester distincts du vérifié.

## Ce que « grandir » veut vraiment dire

- **Le corpus grandit** en continu (vérifié + consenti).
- **Le modèle s'améliore** à chaque cycle d'entraînement (il ne « grossit »
  pas en paramètres).
- **Le palier de base monte** — 1,5 B → 7 B → 14 B → 32 B → 70 B — à mesure que
  des machines capables rejoignent (déjà en place, voir GRAND-MODELE.md). C'est
  le vrai « grossir, grossir ».
- **Distillation** (à venir) : les bonnes réponses du grand modèle servent à
  entraîner les petits — le réseau se tire vers le haut tout seul.

## Boucle continue, pas magie continue

« En continu » ne veut pas dire « à chaque message ». Le rythme sain :
accumuler les signaux, puis entraîner par lots (nuits GPU), évaluer sur les
200 problèmes tenus à l'écart, et **ne publier la nouvelle version que si elle
progresse**. Une régression est rejetée, pas déployée. C'est cette discipline
qui transforme l'usage en progrès plutôt qu'en dérive.

## Garanties affichées aux membres

- consentement désactivé par défaut, révocable en un clic ;
- seules les réponses **notées 👍** par leur auteur sont éligibles ;
- données personnelles retirées avant conservation ;
- rien de tout cela ne concerne les visiteurs qui n'ont pas de compte.
