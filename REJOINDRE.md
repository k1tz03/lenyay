# Rejoindre l'essaim Lenyay

Ta machine résout des problèmes de mathématiques pendant que tu ne t'en sers
pas. Les solutions vérifiées servent à améliorer un modèle d'IA commun, que
tout le monde peut ensuite utiliser librement.

## Installer (une commande)

**Windows** — ouvre PowerShell et colle :

```powershell
irm https://lenyay.org/install.ps1 | iex
```

**Linux / macOS** — ouvre un terminal et colle :

```bash
curl -fsSL https://lenyay.org/install.sh | bash
```

L'installation prend 2 à 5 minutes : environnement Python isolé, dépendances,
et un diagnostic qui te dit si tout est prêt. Rien n'est installé en dehors du
dossier de Lenyay, aucun droit administrateur n'est demandé.

## Contribuer

**Windows** : double-clique sur le raccourci **Lenyay** posé sur ton Bureau.
**Linux / macOS** : lance `~/.lenyay/lenyay`.

Au premier lancement, le modèle se télécharge (~1,1 Go, une seule fois). Puis
ta machine commence à travailler : tu vois défiler les problèmes résolus (✓)
et ratés (✗). `Ctrl+C` arrête proprement, avec un résumé de ta session.

Suis la progression de l'essaim et ton classement sur **https://lenyay.org**.

## Questions fréquentes

**Ça consomme quoi ?** Un cœur de processeur et ~2 Go de mémoire pendant que
ça tourne. Lance-le quand tu n'utilises pas ta machine — la nuit, par exemple.
Ça n'accède qu'au coordinateur Lenyay, à rien d'autre sur ton ordinateur.

**Mes données ?** Aucune donnée personnelle n'est envoyée. Ta machine reçoit
des énoncés de maths publics (le jeu GSM8K) et renvoie ses raisonnements. Ton
appareil est identifié par un numéro aléatoire, pas par ton nom.

**À quoi servent les crédits ?** Ils comptent ta contribution. Ils ne sont ni
transférables ni convertibles en argent — c'est un compteur de participation,
pas une monnaie.

**Comment j'arrête ?** `Ctrl+C`. Pour désinstaller : supprime le dossier
`%LOCALAPPDATA%\Lenyay` (Windows) ou `~/.lenyay` (Linux/macOS), et le
raccourci sur le Bureau. Rien d'autre n'a été installé.

**Ça marche sur ma machine ?** Il faut Python 3.11+, ~2 Go de disque et
4 Go de mémoire. Lance le diagnostic pour vérifier :

```bash
~/.lenyay/lenyay --check
```

**Une erreur au lancement ?** Le worker encaisse les coupures réseau et les
redémarrages du serveur tout seul (il attend et réessaie). Si le problème
persiste, ouvre un ticket sur le dépôt avec la sortie de `--check`.

## Ce que Lenyay ne fait pas

Pas de minage de cryptomonnaie, pas de publicité, pas de collecte de données,
pas de démarrage automatique dans ton dos : tu lances et tu arrêtes quand tu
veux. Le code est ouvert, tu peux tout lire.
