# Le très grand modèle — architecture et chemin réaliste

Objectif : que Lenyay serve un jour un modèle de classe 70 B, sans datacenter.
Ce document décrit le chemin par étapes — chaque étape est utile en soi, et on
ne promet publiquement que l'étape en production.

## Étape 1 — livrée : des paliers de plus en plus grands, servis en entier

Une machine capable sert un modèle *entier* ; le coordinateur route chaque
question vers le bon palier, et le chat n'affiche un modèle que si une machine
peut le servir en ce moment (`/tiers` expose `online`).

| Palier | Modèle | Quantisation | Poids | RAM nécessaire | État |
|---|---|---|---|---|---|
| Rapide | Qwen2.5-1.5B | q4_k_m | ~1,1 Go | 4 Go | en production |
| Costaud | Qwen2.5-7B | q4_k_m | ~4,4 Go | 8 Go | en production |
| Code | Qwen2.5-Coder-7B | q4_k_m | ~4,4 Go | 8 Go | en production |
| Géant | Qwen2.5-14B | q4_k_m | ~8,5 Go | 12–16 Go | **livré** — attend ses machines |
| (suite) | Qwen2.5-32B | q4_k_m | ~19 Go | 24–32 Go | dès qu'une machine existe |

C'est le levier le plus rentable : zéro R&D, et chaque nouveau membre bien
équipé élève le plafond du réseau. La récompense suit la rareté (+45 crédits
par réponse Géant) : le réseau paie mieux ce qui lui manque.

## Étape 2 — prototype : découper sur un réseau local

llama.cpp embarque un backend RPC (`rpc-server`) : un serveur d'inférence peut
déporter des couches vers d'autres machines. Sur un réseau local (latence
< 1 ms), c'est praticable dès aujourd'hui : deux PC de 16 Go côte à côte
peuvent tenir un 32B.

- **Cas d'usage** : un membre avec plusieurs machines chez lui (bureau + vieux
  PC) déclare un « groupe » qui compte comme UNE machine d'un grand palier.
- **Travail Lenyay** : orchestrer le lancement (`rpc-server` sur les
  secondaires, `--rpc host:port` sur la principale), santé du groupe,
  attribution des crédits au groupe.
- **Effort estimé** : 2–3 semaines, sans recherche — l'outillage existe.
- **Limite honnête** : ça ne marche PAS entre deux foyers — la latence
  d'Internet tue le pipeline à chaque couche.

## Étape 3 — R&D : découper entre foyers (la vraie promesse Petals)

Servir un 70B sur des machines reliées par Internet impose de traverser le
réseau à chaque bloc de couches. Les nombres qui commandent tout :

- une réponse de 200 jetons × 80 couches × ~20 ms d'aller-retour ≈ **minutes**
  de latence réseau seule, si chaque couche voyage naïvement ;
- Petals (BigScience) rend ça vivable en regroupant les couches par gros blocs
  contigus chez chaque hôte (moins de sauts), en gardant le cache d'attention
  chez l'hôte, et en re-routant quand un hôte disparaît ;
- il faut aussi décider quoi faire des hôtes menteurs (vérification par
  redondance : deux chemins, comparaison).

**Position Lenyay** : on ne s'y engage qu'après le lancement, avec la
communauté, et on n'annonce rien tant qu'un prototype ne répond pas à une
vraie question de bout en bout. Pré-requis : étape 2 en production, et assez
de machines Géant pour que la redondance soit possible.

## Ce que ça change pour l'abonnement

Le palier Géant (et demain 32B) est la matière première de l'offre payante :
« la personne lambda » n'en a pas besoin, « les personnes qui font du code »
et les usages intensifs si. Le prix en crédits est déjà étagé (1 / 5 / 12 / 20) ;
le prix en argent suivra le même étagement quand l'encaissement existera.
