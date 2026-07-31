# L'application Android

Deux visages, un seul APK :
- **la coquille** — WebView du système, zéro dépendance, qui charge le chat
  (la page se met en mode application via le User-Agent `LenyayApp`) ;
- **le moteur** — llama.cpp compilé pour arm64, piloté par un service de
  premier plan qui résout des tâches du catalogue **uniquement pendant la
  charge** : la prise contribue, jamais la batterie.

## Construire

L'outillage est 100 % portable, rien d'installé dans le système :

| Outil | Emplacement |
|---|---|
| JDK 17 (Temurin) | `~/.lenyay-build/jdk17` |
| SDK Android 34 + NDK 26.3 + CMake 3.22 | `~/.lenyay-build/sdk` |
| Gradle 8.7 | `~/.lenyay-build/gradle-8.7` |
| llama.cpp (sources) | `~/.lenyay-build/llama.cpp` — **commit épinglé : `9d9a6d2`** |

`android/local.properties` (non commité) :

```properties
sdk.dir=C:/Users/<toi>/.lenyay-build/sdk
llama.dir=C:/Users/<toi>/.lenyay-build/llama.cpp
```

> Chemins **en barres obliques** : l'échappement backslash du format
> properties transforme `C\Users` en bouillie et produit une erreur
> trompeuse (« syntaxe du nom de fichier incorrecte »).

Compilation :

```bash
JAVA_HOME=~/.lenyay-build/jdk17 ~/.lenyay-build/gradle-8.7/bin/gradle.bat \
  assembleRelease -PlenyayUrl=https://<domaine>
```

Sans `llama.dir`, l'APK **léger** (coquille seule) se construit quand même :
`Llm.available()` renvoie faux et l'interrupteur Contribuer affiche que le
moteur est absent — la vérité, pas une promesse.

## Le contrat de contribution

- démarrée à la main (interrupteur « Contribuer » de la page) — jamais seule ;
- ne calcule **que branché** (débranché = pause immédiate, même en plein
  téléchargement du modèle) ;
- notification permanente pendant l'activité (service de premier plan) ;
- le modèle (1,1 Go) se télécharge une fois, avec reprise ;
- les gains vont sur le compte connecté dans la page (pont `setAccountKey`).

## Signature

Release signée avec la clé de debug : assumé pour la distribution directe
depuis le site. Une clé dédiée sera créée pour la soumission Play Store —
changer de clé après coup sur le Store étant impossible, ce moment-là
figera l'identité de l'application.
