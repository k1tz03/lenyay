# Plan de lancement — en ligne vendredi 7 août, vacances samedi 8

**Objectif :** tout en ligne vendredi 7/8 en **version gratuite avec garde-fous**,
mention claire « les abonnements viendront dans un second temps », puis
**deux semaines en autonomie** pendant les vacances de Julien.

**Périmètre du vendredi :**
- ✅ le site (chat 6 langues, comptes, /decouvrir, admin) sur le domaine, en HTTPS ;
- ✅ la version PC : `Lenyay-Setup.exe` téléchargeable depuis le site ;
- ✅ Android : **application native (APK)** téléchargeable depuis le site —
  chat, compte, FAQ, 6 langues (la PWA reste en secours pour iOS).
  **La contribution mobile (calcul nocturne) passe par une porte** : llama.cpp
  compilé pour Android et testé sur LE téléphone de Julien au plus tard
  mercredi 5/8. Ça tourne → elle est dans l'APK du lancement. Ça ne tourne
  pas → l'APK sort sans elle et la mise à jour arrive pendant les vacances.
  Pas de Play Store vendredi (validation Google = des jours, hors de notre
  contrôle) : APK distribué par le site, soumission Store ensuite.

**Ce qui dépend de Julien (1 h au total) :** le domaine + le VPS (ce soir ou
demain), un compte UptimeRobot gratuit (5 min), le test final de l'exe, le GO.

---

## Les garde-fous du lancement gratuit (déjà en place, à VÉRIFIER J-2)

| Garde-fou | Réglage | Rôle pendant l'absence |
|---|---|---|
| Plancher quotidien | `DAILY_FREE_CREDITS=5` | personne ne consomme à l'infini |
| Enregistrements/IP | `REGISTER_LIMIT=20`/h | pas d'usine à faux comptes |
| Requêtes/appareil | `RATE_LIMIT=120`/min | pas de matraquage |
| Soumissions/jour | `DAILY_SUBMISSION_CAP=6000` | pas de remplissage disque |
| Crédits/jour/appareil | `DAILY_CREDIT_CAP=2000` | pas de ferme à crédits |
| Tentatives connexion | `LOGIN_LIMIT=10`/15 min | pas de force brute |
| Console /admin | jeton + ban/dé-ban à distance | intervention depuis le téléphone |
| Sauvegardes | quotidiennes, 14 j | rien d'irréversible |
| Service confiné | systemd `ProtectSystem=strict` | le sandbox code ne sort pas |

---

## Jour par jour

### J-8 · mercredi 30/7 — messages du lancement + Android installable  *(moi)*
- [ ] Bannière « 🎉 Lancement : tout est gratuit — les abonnements viendront
      plus tard » sur le chat, traduite dans les 6 langues, et encart équivalent
      sur /decouvrir.
- [ ] PWA : `manifest.webmanifest`, icônes 192/512 (+maskable), service worker,
      balises head — Lenyay devient installable sur Android (et iOS Safari).
- [ ] Tests (manifest servi, bannière présente, i18n complète) ; commit.

### J-8 (suite) → J-4 — l'application Android native  *(moi, en parallèle de tout)*
- [ ] J-8 soir : outillage (JDK + SDK Android portables, sans installation
      système) + squelette de l'app (Kotlin, WebView + coquille native).
- [ ] J-7 : APK v1 qui compile — chat/compte/FAQ, icône, retour matériel,
      liens externes vers le navigateur.
- [ ] J-6 : **test sur le téléphone de Julien** (installation « sources
      inconnues », parcours complet). Bouton « Télécharger pour Android »
      sur /decouvrir.
- [ ] J-6 → J-4 : tentative contribution — compilation llama.cpp (NDK,
      arm64), service de premier plan « pendant la charge », worker HTTP.
- [ ] **J-2 mercredi 5/8, LA PORTE** : le 1,5B répond-il sur le téléphone de
      Julien en un temps acceptable ? Oui → contribution dans l'APK.
      Non → APK sans contribution, chantier continué pendant les vacances.

### J-7 · jeudi 31/7 — domaine  *(Julien le soir, moi ensuite)*
- [ ] **Julien** : acheter domaine + VPS (Debian 12, 2 Go). Créer les DNS :
      `A @ <IP>` et `A www <IP>`. Me donner le nom du domaine.
- [ ] **Moi** : remplacer `lenyay.org` partout (une commande, déjà écrite dans
      deploy/DEPLOIEMENT.md), recompiler `Lenyay-Setup.exe`, re-tester
      l'installation silencieuse + `--worker` contre le coordinateur local.

### J-6 · vendredi 1/8 — mise en ligne technique  *(moi, VPS via Julien)*
- [ ] Sur le VPS : `git clone` + `sudo bash deploy/install-vps.sh <domaine> <jeton>`.
- [ ] Vérifier : `curl https://<domaine>/stats`, /admin avec le jeton, HTTPS ok.
- [ ] Publier l'exe en GitHub Release (`gh release create v0.9.0 dist/Lenyay-Setup.exe`)
      et brancher le bouton « Télécharger pour Windows » de /decouvrir dessus.
- [ ] Basculer mes workers locaux sur la prod (`LENYAY_COORDINATOR_URL=https://<domaine>`)
      pour que le réseau ne soit jamais vide : 1 rapide + 1 costaud + 1 code.

### J-5 → J-4 · week-end 2–3/8 — essaim + tâches réelles  *(moi)*
- [ ] Laisser tourner l'essaim sur la prod ; contrôler /admin, journaux, backups.
- [ ] Éval v0.3 si le dataset chasse est prêt (décision plan B 7B au 2/8 — déjà actée).

### J-3 · lundi 4/8 — répétition générale  *(moi)*
- [ ] Parcours COMPLET en étranger : inscription (EN), question Rapide, question
      Code, 👍, régénérer, mur de crédits, recharge du lendemain (simulée),
      déconnexion/reconnexion — sur le domaine réel, depuis un téléphone Android
      (site + installation PWA) et un PC vierge (Setup.exe téléchargé du site).
- [ ] Test de charge doux : 200 inscriptions + 500 questions scriptées → vérifier
      les 429 et que rien ne tombe.

### J-2 · mardi 5/8 — garde-fous + autonomie vacances  *(moi + Julien 10 min)*
- [ ] Revue ligne à ligne du tableau des garde-fous ci-dessus sur la PROD
      (pas en local) ; test réel : ban depuis le téléphone de Julien.
- [ ] **Julien** : compte UptimeRobot (gratuit) → moniteur HTTPS sur
      `/stats`, alerte e-mail/app si le site tombe.
- [ ] RUNBOOK-VACANCES.md : les 6 pannes possibles et leur remède en une
      commande chacune (redémarrer, bannir, geler les inscriptions, restaurer
      une sauvegarde, couper le palier code, tout éteindre).

### J-1 · jeudi 6/8 — gel  *(moi)*
- [ ] Plus AUCUNE fonctionnalité. Uniquement : suite de tests complète,
      re-lecture des textes dans les 6 langues, sauvegarde manuelle de la base,
      étiquette git `v0.9.0-lancement`.

### J-0 · vendredi 7/8 — GO  *(Julien 30 min, moi le reste)*
- [ ] **Julien** : télécharger l'exe depuis le site comme un inconnu, installer,
      poser une question, activer Contribuer. Si tout est vert → GO public
      (partage du lien où il veut).
- [ ] **Moi** : surveillance active toute la journée, /admin ouvert.

### Pendant les vacances (8–22/8)  *(moi, en autonomie)*
- Surveiller (UptimeRobot + admin), bannir les abus, garder l'essaim vivant.
- **Développer l'app Android native** (contribution nocturne pendant la charge),
  objectif : bêta installable au retour.
- Écrire l'intégration Stripe à blanc (prête à brancher quand la société existe).
- Ne RIEN déployer de nouveau sur la prod sauf correctif de sécurité.

---

## Ce qu'on ne fait PAS vendredi (dit sur le site, pas caché)
- Abonnements : « viendront dans un second temps » — le mur de crédits le dit.
- App Android native (contribution) : « en construction » sur /decouvrir.
- iOS : après Android.
- Volume sur les tâches code : le palier reste ouvert mais le catalogue est
  petit (24) tant que l'isolation conteneur n'est pas posée sur le VPS.
