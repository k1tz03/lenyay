# Feuille de route Lenyay

Ce qui est en place, ce qui est en chantier, et — surtout — **combien de temps**
chaque chantier demande vraiment. Le principe de la maison : on n'annonce jamais
comme disponible ce qui ne l'est pas.

## Livré (utilisable au lancement du 7 août)

- **Réseau** : coordinateur FastAPI + SQLite, worker autonome, preuve de travail,
  vérification exacte des réponses, protections anti-abus.
- **Chat** : conversations suivies avec mémoire du fil, **choix du modèle**
  (Rapide 1,5 B / Costaud 7 B) directement dans la barre du chat.
- **Comptes** : e-mail + mot de passe (haché PBKDF2), sessions révocables,
  relevé complet des crédits (gagnés / dépensés), machines rattachées.
- **Administration** : console `/admin` (jeton `LENYAY_ADMIN_TOKEN`) — liste des
  membres, ajustement de crédits tracé, suspension/rétablissement, vue d'ensemble.
- **Économie** : le contributeur ne paie jamais ; le non-contributeur reçoit un
  **plancher quotidien** (5 crédits/jour) puis doit contribuer ou, à terme, payer.
- **IA locale** : `lenyay --chat`, le modèle répond hors ligne, gratuitement.

## En chantier — calendrier honnête

| Chantier | Effort réel | État |
|---|---|---|
| **Module Lenyay Code** (chat) | — | ✅ **livré** — palier Code (Qwen2.5-Coder, 12 crédits, +25) |
| **Entraîner par le code** | — | ✅ **livré (v0)** — 24 tâches vérifiées par tests unitaires en sandbox |
| **Choix du modèle dans le chat** | — | ✅ livré — sélecteur (les modèles sans machine en ligne sont grisés) |
| **Grand modèle : palier Géant 14B** | — | ✅ livré — attend ses premières machines (voir GRAND-MODELE.md) |
| **Grand modèle réparti sur N foyers** | plusieurs mois (R&D) | ❌ recherche — chemin par étapes dans GRAND-MODELE.md |
| **Abonnement payant** | 1–2 sem. + société + Stripe + CGV | ❌ décision juridique, pas du code |
| **Application Android** | 4–6 semaines | ❌ hors fenêtre du 7/8 |
| **Application iOS** | +3–4 sem. après Android | ❌ consommation seule (voir plus bas) |
| **Mise en ligne (VPS + domaine)** | 1 soirée + DNS | ✅ **kit prêt** — deploy/DEPLOIEMENT.md |

**Sandbox code — condition d'exploitation** : le vérificateur exécute le code
soumis en sous-processus isolé (`python -I`, délai strict, filtrage statique,
limites mémoire/CPU sur Linux). C'est suffisant pour la fenêtre de lancement,
mais le VPS devra ajouter une isolation système (conteneur ou utilisateur
dédié sans droits) avant d'augmenter le volume de tâches code — c'est noté
comme pré-requis de déploiement.

### Abonnement — ce qui manque n'est pas technique

La plomberie est prête : plancher quotidien, mur de crédits, message qui oriente
vers l'abonnement. Ce qui manque relève de **toi**, pas du code :

1. une structure qui encaisse (auto-entreprise suffit pour commencer) ;
2. un compte Stripe (ou Lemon Squeezy, qui gère la TVA à ta place) ;
3. des CGV et une politique de remboursement.

Le jour où ces trois éléments existent, brancher Stripe Checkout + le webhook qui
crédite le compte se fait en 1 à 2 jours. **Stratégie de prix** (voir plus bas).

### Le très grand modèle réparti — pourquoi c'est dur

Découper un modèle de 70 B sur des ordinateurs grand public reliés par Internet,
c'est ce que fait le projet **Petals** (BigScience) : chaque machine tient
quelques couches, l'inférence circule de l'une à l'autre. Sur un réseau
domestique (latence, machines qui s'éteignent, débit asymétrique) c'est un
sujet de recherche, pas une semaine de code. **Le chemin réaliste** : un modèle
plus gros servi *en entier* par une machine capable (déjà possible via le palier
Costaud), et on monte en taille à mesure que des machines puissantes rejoignent.

### Entraîner sur autre chose que les maths — le vrai levier

L'architecture ne dépend **pas** des mathématiques : elle exige seulement des
tâches **vérifiables**. Extensions atteignables par ordre de difficulté :

1. **Code** — exécuter des tests unitaires : réponse juste = tests au vert.
   Vérification objective, comme les maths. **C'est aussi ta clientèle payante.**
2. **Questions à réponse courte** (factuel, unités, dates) — vérifiables.
3. **Rédaction, résumé, style** — pas de vérité unique : demande un modèle-juge
   ou un vote, donc plus fragile. À garder pour plus tard.

## Mobile — Android d'abord, iOS à part

- **Desktop (novices)** : application fenêtrée `Lenyay.exe` — chat, compte,
  FAQ et interrupteur « Contribuer », rien du site. Distribuée par
  `Lenyay-Setup.exe` (double-clic, raccourcis Bureau + menu Démarrer,
  désinstallation propre ; les crédits restent sur le compte en ligne).
  Construction : `scripts/build_desktop.ps1`. La ligne de commande reste
  disponible pour les techniciens (install.ps1 / install.sh).
- **Android (4–6 sem.)** : le seul mobile qui peut vraiment CONTRIBUER. Un
  service de premier plan pendant la charge nocturne peut faire tourner le
  1,5 B (les téléphones récents le portent) : le téléphone gagne des crédits
  la nuit comme un PC. Compte Play Store : 25 $ une fois, validation en jours.
- **iOS (+3–4 sem. après)** : Apple interdit de fait le calcul long en
  arrière-plan — une app iOS ne PEUT PAS travailler la nuit. L'utilisateur
  iOS est donc consommateur pur : **il paie l'abonnement, sans alternative de
  contribution**. C'est une contrainte d'Apple, pas un choix commercial — et
  on l'affichera tel quel. S'ajoutent 99 $/an de compte développeur et
  15–30 % de commission d'Apple sur l'abonnement : le prix iOS doit couvrir
  cette commission (donc légèrement supérieur, à commission égale de marge).

## Stratégie de revenus (ta consigne)

> « Ce qui fait gagner de l'argent, c'est la personne lambda pour une question
> simple, et les personnes qui font du code. »

Traduit en mécanique déjà en place :

- **La personne lambda** consomme peu : le plancher quotidien la laisse essayer,
  et si elle prend goût sans jamais prêter sa machine, un abonnement **minime**
  (l'ordre de 2–3 €/mois, à caler) couvre son usage. Comme il n'y a aucun
  datacenter, le point mort est très bas — l'abonnement peut rester symbolique.
- **Le développeur** consomme le palier Costaud (×5 en coût, ×12 en récompense) :
  c'est le gros poste de calcul, donc là que se concentre la valeur. Deux façons
  d'en capter la juste part : soit il **contribue** (sa machine sert le 7 B la
  nuit et il s'auto-finance), soit il **s'abonne** à un palier « pro » qui reflète
  sa consommation réelle. Le prix suit le coût en crédits, pas un forfait unique.

Le principe cardinal : **contribuer doit toujours être plus avantageux que
payer**. L'abonnement n'est pas la voie royale, c'est la sortie pour qui ne veut
ou ne peut pas prêter de machine.
