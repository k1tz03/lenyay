# Mettre Lenyay en ligne — la soirée, pas la semaine

Pré-requis : un VPS Debian 12 / Ubuntu 22+ (2 vCPU, 2 Go de RAM suffisent —
le VPS ne fait AUCUNE inférence, ce sont les machines des membres qui
calculent) et un nom de domaine.

## Ce soir (10 minutes chez le registrar)

1. Achète le domaine et le VPS. Note l'IP du VPS.
2. Chez le registrar, crée deux enregistrements DNS :
   - `A  @    <IP-du-VPS>`
   - `A  www  <IP-du-VPS>`
   La propagation prend de quelques minutes à quelques heures.

## Demain (30 minutes sur le VPS)

```bash
ssh root@<IP-du-VPS>
git clone https://github.com/k1tz03/lenyay.git /opt/lenyay
sudo bash /opt/lenyay/deploy/install-vps.sh ton-domaine.org "UN-JETON-ADMIN-LONG-ET-ALEATOIRE"
```

Le script installe Caddy (HTTPS automatique), crée un utilisateur de service
sans droits, pose le service systemd (confiné : il ne peut écrire que dans
/var/lib/lenyay), et programme la sauvegarde quotidienne (base + traces,
14 jours de rétention).

Vérification :

```bash
curl -s https://ton-domaine.org/stats
```

## Ensuite (5 minutes en local)

Remplacer le domaine provisoire partout puis pousser :

```bash
grep -rl "lenyay.org" --include="*.py" --include="*.ps1" --include="*.sh" --include="*.md" . \
  | xargs sed -i "s/lenyay\.org/ton-domaine.org/g"
```

Et pointer tes workers vers la production :

```bash
LENYAY_COORDINATOR_URL=https://ton-domaine.org python -m worker.main
```

## Les points de sécurité déjà réglés par le kit

- coordinateur lié à 127.0.0.1, seul Caddy est exposé ;
- HTTPS automatique + HSTS, en-têtes durcis, corps limités à 1 Mo ;
- console /admin inerte tant que `LENYAY_ADMIN_TOKEN` n'est pas défini —
  le kit l'exige en argument ;
- service systemd confiné (`ProtectSystem=strict`, utilisateur dédié) :
  première couche d'isolation pour le sandbox des tâches code ;
- sauvegarde quotidienne automatique.

## À surveiller après l'ouverture

- `journalctl -u lenyay -f` : le journal du coordinateur ;
- la taille de `/var/lib/lenyay/backups` ;
- avant de monter le volume des tâches code : ajouter l'isolation conteneur
  (documenté dans FEUILLE-DE-ROUTE.md).
