# M.A.S.K. — PROJECT MAYHEM
## Spécification maître de développement (GDD + TDD + plan d'exécution IA)
**Version :** 2.0 — 1er novembre 2026  
**Destinataires :** Claude Code, OpenAI Codex, développeurs Unreal Engine, artistes 3D  
**Statut :** spécification initiale, à confirmer par audit de code et prototypes mesurés  
**Langue de référence :** français ; noms de classes, identifiants et commits en anglais.

---

## 0. Directive fondamentale aux agents

Vous intervenez sur un projet de jeu vidéo d'action en véhicules transformables, inspiré de M.A.S.K. et conçu pour évoluer vers une expérience coopérative en ligne. **Ne prétendez jamais avoir compilé, exécuté, testé, ouvert un asset, ni validé une animation si ce n'est pas réellement le cas.** Identifiez chaque fait comme `VÉRIFIÉ`, `SUPPOSÉ`, `À TESTER` ou `BLOQUÉ`.

**Priorité absolue :** disposer d'un prototype de Thunderhawk transformable, pilotable et synchronisé sur deux clients, avant d'investir dans des assets finaux coûteux. L'art final et le gameplay sont deux flux de travail parallèles, reliés par un contrat d'asset versionné.

**Ne jamais** : supprimer les projets de référence, réécrire massivement sans test, changer de moteur sans décision documentée, copier des assets protégés provenant de jeux ou de sites tiers, intégrer des dépendances à licence incertaine, mettre des secrets en dépôt, déclarer qu'un screenshot équivaut à un test multijoueur.

## 1. Vision du produit

### 1.1 Pitch
Jeu d'action cinématique en 3D avec conduite, vol, transformations mécaniques et combats tactiques entre M.A.S.K. et V.E.N.O.M. À terme, chaque conducteur d'une équipe en mission est un joueur humain ; agents et véhicules ont des rôles complémentaires. Le jeu comporte un quartier général interactif à Boulder Hill, un garage de collection, des missions narratives coopératives et une progression non pay-to-win.

### 1.2 Direction artistique non négociable
- Reconnaissance immédiate des silhouettes, couleurs, masques et mécanismes du dessin animé M.A.S.K. des années 1980 ; les jouets sont des références secondaires pour les mécanismes.
- Rendu réaliste/cinématique : PBR, éclairage dynamique, détails d'habitacle, surfaces métalliques et vitrées, météo, VFX, sons mécaniques ; pas d'esthétique générique de supercar moderne.
- Deux niveaux de fidélité : `Hero` (showroom/cinématique) et `Gameplay` (optimisé temps réel). Même géométrie fonctionnelle et mêmes pivots.
- Transformation **physiquement lisible** : aucune substitution instantanée du véhicule par un deuxième mesh sans animation. Les segments disposent de pivots, contraintes et ordre temporel explicites.
- Les références externes sont utilisées pour recherche/observation uniquement ; aucune image ou géométrie de tiers ne doit être réutilisée sans droits adéquats.

### 1.3 Cadre juridique
M.A.S.K., V.E.N.O.M., noms, designs et personnages sont susceptibles d'être protégés. Le prototypage et une éventuelle commercialisation doivent faire l'objet d'une validation de propriété intellectuelle et de licences. Prévoir un mode de développement avec assets placeholder originaux, et documenter la provenance/les droits de chaque asset. L'absence de licence interdit de présumer une liberté de distribution commerciale.

### 1.4 Cibles et non-objectifs
**MVP artistique préalable :** Thunderhawk `.blend` transformable, test d’import dans un projet Unreal vierge, showroom autonome. **MVP technique suivant :** PC Windows, clavier/souris + manette, version UE stable vérifiée, conduite, transformation, vol, armes et réseau 2 joueurs avec logs reproductibles.
**MVP vertical slice :** zone Boulder Hill showroom, Matt Trakker, Spectrum, un adversaire (Switchblade en placeholder ou modèle propre), première mission courte, récompense et garage local.
**Vision long terme :** 1–6 joueurs PvE, PvP asymétrique M.A.S.K. vs V.E.N.O.M., monde ouvert, véhicules/masques collectionnables, progression persistante, événements.
**Hors périmètre MVP :** carte façon GTA entière, 6 joueurs garantis, économie en ligne, saisons live, captures de mouvements AAA, multiples plateformes, crossplay, véhicules entièrement destructibles.

## 2. Références et hypothèses

- Référence initiale : https://github.com/DanialKama/VehicularCombat — prototype UE Chaos Vehicles multijoueur, code sous licence MIT selon dépôt public ; l'auteur précise qu'il n'est pas prêt pour la production.
- Références de la série : https://maskforce.com/ et playlist fournie par le porteur de projet ; examiner les conditions de réutilisation des images.
- UE 5.8 : https://www.unrealengine.com/news/unreal-engine-5-8-is-now-available
- Chaos Modular Vehicles : https://dev.epicgames.com/documentation/unreal-engine/chaos-modular-vehicles-overview
- Chaos Modular Vehicles Quickstart : https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-modular-vehicles-quickstart

**Hypothèses à valider :** code original compilable ; gestion réseau réellement fonctionnelle ; ressources présentes et utilisables ; compatibilité 5.8.4 ; possibilité de réutiliser/étendre le Pawn ; comportement d'armes et dégâts. Aucun de ces points n'est considéré confirmé par la simple existence d'un fichier de configuration.

## 3. Stratégie de réalisation — ART FIRST, ENGINE INDEPENDENT

**Décision produit formelle :** priorité à la création de Thunderhawk, puis Matt Trakker et Spectrum ; aucune migration de VehicularCombat n'est requise avant la première démonstration Blender. Le moteur final n'est pas encore choisi. Le contrat d'assets doit être indépendant du code VehicularCombat.

### Volet A — Production 3D (chemin critique initial)

**Gate A0 — Bible visuelle et contrat technique de l'asset**
- Références dessin animé : captures obtenues légalement, différentes vues, couleurs, transformation et ambiguïtés identifiées ; jouet Kenner comme référence secondaire.
- Déterminer dimensions **estimées et étiquetées comme telles**, échelle, orientation, séparation des pièces, pivots, portes, roues, ailes, cockpit et zones de collision.
- Écrire `docs/art/THK_asset_contract.md` (noms, dimensions, repères, sockets, séquences, règles d'export, contrôles qualité). Pas de prétention à une géométrie exacte sans orthographies fiables.
- **Validation** : fiche visuelle + plan de transformation + contrat accepté ; aucune dépendance à VehicularCombat.

**Gate A1 — Thunderhawk mécanique V0 / Blender**
- Créer une silhouette immédiatement reconnaissable mais **non finale**, chassis, habitacle simplifié, roues distinctes, deux ailes et charnières cohérentes.
- Créer les animations road→flight et flight→road ; régler origines, contraintes, interférences et timing.
- Générer `.blend` natif, rendu turntable, séquence vidéo de transformation et rapport de dimensions. Proposer scripts `bpy` versionnés pour automatiser contrôles/export ; conserver `.blend` modifiable.
- **Validation** : inspection libre 360°, transformation réversible sans intersections majeures, aucun objet crucial fusionné, animation reproductible.

**Gate A2 — Test précoce d'import UE neutre**
- Créer un projet Unreal vierge minimal (`MASK_AssetLab`) avec version stable validée et **sans code VehicularCombat**.
- Exporter depuis Blender un FBX squelettique ou un ensemble de maillages articulés selon spike ; valider échelle, orientations, rig/pivots, animation, matériaux et physique simple.
- Tester une animation dans un viewer/plateforme Unreal. Consigner les problèmes ; ajuster le contrat Blender **avant** d'ajouter le détail ultra-réaliste.
- **Validation** : même modèle animé dans Blender et UE, transformations visuellement équivalentes, pas de réimport destructif.

**Gate A3 — Thunderhawk Hero + Gameplay**
- Finaliser proportions inspirées de l'animé, mécanique crédible, PBR, UV, LOD, matériaux, cockpit et géométrie de collision.
- Produire une version Hero pour le showroom et une version Gameplay légère **partageant les articulations**. Budget de performance mesuré, pas de chiffre inventé.
- **Validation** : turntable cinématique, animation, import UE, profil de performance documenté.

**Gate A4 — Matt Trakker + Spectrum**
- Créer un personnage à échelle cohérente avec cockpit ; rig humanoïde, maillage personnage + équipement, masque Spectrum **objet séparé** attachable, states masked/unmasked.
- Livrer animations idle, équipe masque, assis volant (prioritaires) ; marche et sortie véhicule ensuite.
- **Validation** : masque sans clipping majeur, silhouette reconnaissable, pilote correctement placé, import UE testable.

**Gate A5 — Showroom Boulder Hill**
- Construire dans `MASK_AssetLab` une zone showroom inspirée de Boulder Hill : caméra orbitale/zoom, sélection, transformation, choix masqué/démasqué, scène éclairée temps réel ; station-service/forteresse complète plus tard.
- **Validation** : démo autonome fonctionnelle **sans VehicularCombat** et sans serveur.

### Volet B — Évaluation indépendante du moteur (commence en parallèle dès A0/A1)

**Gate B0 — Audit de VehicularCombat, sans migration**
- Cloner/figer commit, identifier vraie version UE, C++, BP, assets, licences, plugins, physique, armes et sessions.
- Contrôler la capacité à compiler sur son moteur d'origine si environnement disponible ; ne pas inventer le résultat.
- **Livrable** : `docs/engine/vehicularcombat_audit.md` avec preuves par chemins/fichiers et risques.

**Gate B1 — Comparaison et décision sur prototype gris**
- Tester (si outils disponibles) 2 voies : (A) fork migré de VehicularCombat, (B) projet Unreal vierge basé sur APIs UE documentées ; comparer également Chaos Vehicles stable et Chaos Modular Vehicles expérimental.
- Critères : compilation, maintenance, licences, coût de migration, conduite, possibilité de basculer en vol, architecture réseau, stabilité et temps d'intégration **estimé et sourcé**.
- Rédiger `docs/decisions/ADR-001-engine-base.md` avec décision, preuves et plan de repli. **Ne pas migrer toute la base avant cette décision.**

**Gate B2 — Base gameplay retenue et intégration de l'asset A2/A3**
- Mettre en place pawn, conduite Chaos, transform state machine et mode Flight, collisions, tir ; réutiliser une licence tierce seulement après contrôle des assets.
- Test réseau client/serveur à deux instances et transformation autoritative après validation solo.

### Volet C — Jeu complet (après jonction A et B)

**Gate C0 — Vertical slice** : showroom avec Matt/Spectrum, Thunderhawk pilotable et transformable, adversaire mannequin/placeholder, combat + mission coop à 2, résultat et garage local.

**Gate C1 — Coop 4–6 joueurs** : lobby, sélection rôles, rejoin, hôte/serveur dédié selon tests, télémetrie et équilibrage.

**Gate C2 — Collection/loot/campagne/PvP** : nouveaux véhicules, factions M.A.S.K./V.E.N.O.M., mission génératrice, progression et persistance sécurisée, PvP testé séparément.

**Règle anti-retravail :** on commence l'art 3D **avant** le choix du moteur, mais on teste un import Unreal dès A2 et **avant** les finitions AAA. Le showroom ne doit pas dépendre du résultat de l'audit VehicularCombat.

## 4. Contrat 3D et pipeline artistique

### 4.1 Unit, axes, origine
- Unités Blender en mètres avec export vers UE en centimètres correctement configuré ; sens avant +X Unreal, haut +Z Unreal, convention coordonnée à valider par un asset-test.
- Nommer les objets sans espaces ni accents, par exemple `THK_Body`, `THK_Wing_L`, `THK_Wing_R`, `THK_Wheel_FL` ; matérialiser clairement origin/pivots.
- Centre de masse explicite et socket `SOCKET_DriverSeat`, `SOCKET_Muzzle_L`, `SOCKET_Muzzle_R`, `SOCKET_CameraCockpit`, `SOCKET_Exhaust`, `SOCKET_VFX_Transform`.
- Topologie compatible LOD et animation ; aucune aile qui traverse l'habitacle à cause d'un pivot approximatif.

### 4.2 Hiérarchie indicative
```
THK_Root
  THK_Chassis
  THK_Body
  THK_Hood
  THK_Wheel_FL
  THK_Wheel_FR
  THK_Wheel_RL
  THK_Wheel_RR
  THK_Wing_Hinge_L
    THK_Wing_L
  THK_Wing_Hinge_R
    THK_Wing_R
  THK_WeaponMounts
  THK_Cockpit
  THK_DriverSeat
```
L'architecture exacte des ailes sera corrigée après étude frame-by-frame d'images de référence licites. Livrer un mécanisme plausible fidèle à l'animation plutôt que deviner les articulations absentes.

### 4.3 Livrables 3D obligatoires
- `.blend` source avec collections propres, mesh intact, UVs, rig, timeline d'animation ; `.fbx` ou format d'import validé ; textures source et export ; manifest JSON/YAML.
- `THK_RoadIdle`, `THK_RoadToFlight`, `THK_FlightIdle`, `THK_FlightToRoad` ; transformation retour complète, interruptibilité définie.
- Maillage low/mid/high ou stratégie Nanite appropriée (attention aux parties animées), physics asset, collisions proxy, enveloppes LOD.
- Textures PBR base color, normal, roughness, metallic, emissive et éventuellement ORM ; conventions résolutions/lod explicites (par défaut 2K gameplay, 4K hero uniquement si le budget le permet).
- Pivot verification test : import sans décalage, ailes correctement orientées, suspension et roues avec rotation correcte, aucun clipping majeur.
- Fiche de sources : photos/épisodes consultés, mesures estimées, différences jouet/animé, décisions artistiques.

### 4.4 Matt Trakker et Spectrum
- Personnage `MattTrakker` : version sans masque et version masquée, silhouette reconnaissable, rig UE-compatible, animation idle/walk/enter/exit/fit-mask (les dernières peuvent rester hors scope G2-G4).
- `Spectrum` : mesh indépendant attaché par socket tête, activation VFX et état d'équipement ; capacités réelles définies ultérieurement par la bible de gameplay.
- Aucun pilote requis pour valider G2-G4 : prototype avec mannequin/placebo et caméra d'habitacle.

## 5. Architecture logicielle proposée (à adapter à l'audit)

```
Source/ProjectMayhem/
  Core/                // logging, gameplay tags, data assets
  Vehicles/            // base pawn, states, physics adapters
  Transformation/      // state machine, animation replication
  Combat/              // weapons, damage, targeting
  Characters/          // pilots and masks
  Multiplayer/         // sessions, replication tests, server authority
  Missions/            // objective graph and mission instances
  Progression/         // inventory, economy, persistence
  UI/                  // showroom, garage, HUD
  Tests/               // automation, network soak, asset validators
Content/ProjectMayhem/
  Vehicles/Thunderhawk/
  Characters/MattTrakker/
  Masks/Spectrum/
  Maps/VehicleTest/
  Maps/BoulderHill/
  Data/
  UI/
docs/
  architecture/
  audit/
  decisions/
  qa/
art_source/
  Thunderhawk/
```

**Composants proposés, non présumés présents dans VehicularCombat :**
- `AMASKVehicleBase` ou un Pawn dérivé du type validé par l'audit ; posséder l'Actor côté serveur.
- `UMASKTransformationComponent` : `EMASKVehicleMode` (`Road`, `TransformingToFlight`, `Flight`, `TransformingToRoad`, `Disabled`), timers et validation autoritative.
- `UMASKRoadMovementAdapter` : interop Chaos wheeled vehicle, surfaces et dégâts roulants.
- `UMASKFlightMovementComponent` : commandes pitch/roll/yaw/throttle, vitesses et limites, forces et corrections réseau.
- `UMASKCombatComponent` : armes modulaires serveur, munitions, cooldowns, projectiles et impact effects clients.
- `UMASKHealthComponent` : santé globale initiale puis dégâts localisés par zone.
- `UMASKPilotComponent` : sélection, capacités de masque, sièges et interactions.
- `UMASKVehicleDataAsset` : config data-driven (masses, physiques, sockets, états, armes, contraintes et UI).

### 5.1 Décision Chaos Vehicles vs Chaos Modular Vehicles
Préparer un spike comparatif de 1 à 2 véhicules graybox avec mêmes métriques. `Chaos Vehicles` classique = voie stable et probablement compatible avec le prototype original. `Chaos Modular Vehicles` = modules dynamiques, Geometry Collections, thrusters/aerofoils, réplication prédictive native, **plugin expérimental**. Critères : stabilité réseau, maintenance, qualité de mouvement, facilité de transformation, performance et facilité d'intégration des meshes artistiques. Ne pas choisir le nouveau framework uniquement parce qu'il est plus récent.

### 5.2 Synchronisation transformation
Client demande un changement via RPC serveur ; serveur valide vitesse, cooldown, dégâts et conditions ; serveur fixe état, temps de départ et durée, publie via propriétés répliquées/OnRep. Les clients dérivent une progression continue à partir du temps serveur estimé ; l'animation n'envoie pas chaque rotation de charnière par le réseau. La collision et le modèle de déplacement changent à des moments autoritatifs définis et testables. Prévoir reprise après perte de paquets et pour nouvel arrivant.

### 5.3 Autorité et anti-triche
Serveur arbitre position/collisions selon modèle réseau retenu, dégâts, missiles, inventaire, récompenses et cooldowns. Ne pas faire confiance aux scores ni aux récompenses envoyés par un client. Limitation du taux de RPC, validation des inputs et journaux serveur.

## 6. Spécification fonctionnelle du prototype Thunderhawk

### 6.1 Conduite Road
Accélérer, freiner, tourner, marche arrière, frein à main, changer caméra, tirer (si autorisé), voir l'état du véhicule, respawn. Sensation arcade réaliste plutôt que simulation punitive ; paramètres exposés DataAssets.

### 6.2 Transformation
Commande dédiée ; animation lisible ~2–5 secondes **paramétrable et à valider artistiquement** ; effets mécaniques/sons synchronisés ; gestion du rollback en cas d'interruption uniquement si scénario défini. Quand la vitesse ou la position empêchent la transformation, afficher la raison. Tester transformation à l'arrêt, en mouvement et proche d'un obstacle.

### 6.3 Vol Flight
Contrôles manette et clavier, assiette, roulis, lacet, accélération, montée/descente, décrochage simplifié facultatif. Caméra poursuivante stable, HUD de vitesse/altitude, collisions aériennes et dégâts. Ne pas annoncer une simulation aérodynamique réaliste avant calibrage.

### 6.4 Combat
Arme primaire initiale (projectile ou hitscan, à décider), effets d'impact, dégâts serveur, destruction ou immobilisation, cooldown, feedback visuel/audio, cible IA simple et un second véhicule piloté par humain.

### 6.5 Qualité réseau
Tests au minimum : 0 ms / 80 ms / 150 ms latence simulée, 0 % / 2 % perte, deux clients, transformation simultanée, collision, tir à pleine vitesse, entrée tardive, déconnexion et respawn. Seuils cibles initiaux : aucune divergence persistante d'état de transformation, aucune duplication de récompense, mouvements sans téléportations fréquentes ; thresholds chiffrés position/erreur à fixer après mesures de base.

## 7. Boulder Hill — showroom

- Première version = hangar limité, 1 podium interactif, 1 véhicule, éclairage cinématique ; base extérieure et souterraine extensibles.
- Interactions : rotation caméra libre 360°, zoom, points d'intérêt, ouvrir portes, activer/désactiver transformation, inspecter masques, fiche véhicule, entrer dans le cockpit, essai sur piste.
- Transitions : showroom → véhicule pilotable sans rechargement si réalisable ; sinon chargement explicite.
- Fonction sociale ultérieure : visiter le hangar d'un ami, regarder la transformation, sélectionner agents et préparer les opérations.

## 8. Mission coopérative verticale

**Nom :** Highway Phantom.  
**Taille :** 2 humains en prototype ; vision 1–6 joueurs.  
**Pitch :** V.E.N.O.M. transporte un prototype sur autoroute, protégé par Jackhammer et surveillé par Switchblade.

**Séquence :** briefing Boulder Hill → choix Thunderhawk + véhicule secondaire → déplacement → reconnaissance → interception du convoi → combat véhicule ennemi → récupération/escorte → extraction → débrief → attribution garantie de composants et récompense conditionnelle.

**Architecture missions :** objectifs data-driven avec états `Locked`, `Active`, `Completed`, `Failed`; événements serveur, sous-objectifs coop, points de réapparition, sauvegarde locale de progression, chronométrage facultatif, récompenses côté serveur. Un agent IA remplace les coéquipiers absents seulement plus tard.

**Critères de réussite :** deux humains peuvent terminer la mission dans la même instance, objectifs et résultat identiques côté clients, récompense enregistrée une fois, session relançable.

## 9. Collection, loot, progression et retention saine

### 9.1 Loop
Choisir agent/véhicule → construire équipe → mission avec objectifs variables → composants/plans/trophées → garage/labo → nouvelles spécialisations → missions de difficulté supérieure.

### 9.2 Collection
Familles `VehicleBlueprint`, `VehicleOwned`, `Mask`, `VehicleModule`, `Pilot`, `ArchiveCollectible`, `Cosmetic`, `MissionTrophy`. Un véhicule emblématique est débloqué par un jalon/scénario, pas seulement un loot ultra-rare.

### 9.3 Loot
Tiers `Common`, `Rare`, `Epic`, `Prototype`, `Legendary` pour les composants, mais les mods doivent apporter compromis tactiques et variantes de gameplay plutôt qu'inflation infinie. Chaque mission donne une récompense garantie. Rare drops ont une voie de fabrication avec ressources mesurées. Toutes tables versionnées et testées statistiquement. Aucun loot box payant ni avantage pay-to-win.

### 9.4 Progression et équilibrage
Profils pilotés par DataAssets : spécialisations Interceptor/Assault/Recon, capacités de masque, perks, ressources et recettes. PvP normalisé pour éviter l'avantage décisif d'un joueur vétéran. Les activités récurrentes restent optionnelles ; pas de punition majeure pour l'absence.

### 9.5 Persistence
Prototype : sauvegarde locale via `SaveGame` et identifiants stables. En production : profil serveur, version de schéma, transactions idempotentes, journal d'attribution, solution de back-end à sélectionner par ADR. Ne pas construire un service cloud complet dans la phase prototype.

## 10. Interfaces et UX
- Menu initial, garage de choix véhicule, panneau de pilote/masque, HUD Road/Flight, info de transformation, munitions et santé.
- UI avec manette, accessibilité couleurs/sous-titres, feedback de blocage de transformation, objectifs prioritaires.
- Le showroom ne doit pas nécessiter de réseau pour fonctionner en local ; mode connecté opt-in lors des premières étapes.

## 11. Performance et budgets initiaux
- Plateforme cible : Windows PC milieu/haut de gamme, configuration de référence à relever explicitement.
- Objectif visé gameplay : 60 fps en scène d'essai sur machine cible validée ; showroom `Epic/Cinematic` peut offrir un profil graphique distinct. Indiquer toujours résolution, DLSS/TSR, ray tracing, GPU/CPU et conditions de mesure.
- Prévoir profiler Unreal Insights, stat unit/gpu, budgets triangles, textures, draw calls et bandwidth. Aucun budget numérique fixe tant que cible matérielle n'est pas décidée ; proposer des seuils après baseline et renseigner le document performance.

## 12. Qualité, validation et preuves

### Tests automatisés minimum
- Tests unitaires C++ transformation : transitions autorisées/interdites, timer, réplication état et cooldown.
- Tests fonctionnels PIE : spawn du véhicule, entrées et sorties d'état, commandes.
- Test d'import des assets : pivots, sockets, noms, absence de références manquantes, limites maillage.
- Tests réseau : 2 clients + serveur, spawn, possession, mouvement, tir, santé, transformation simultanée et jonction tardive.
- Tests packaging Windows, smoke test d'exécution.

### Définition de « terminé » (DoD)
Une tâche n'est `DONE` que si : code/asset présents et versionnés, instructions de reproduction, build ou test effectué, résultat/logs disponibles, limites connues, pas de régression bloquante. Si l'agent ne dispose ni d'Unreal Editor ni de Windows/toolchain, il peut produire code, scripts et documentation, **mais marque le test Unreal `NON EXÉCUTÉ`**.

### Rapports obligatoires par itération
`docs/progress/YYYY-MM-DD.md` : changements, fichiers, commandes réellement exécutées, résultats, problèmes, étapes suivantes. Ajouter captures ou vidéo seulement si réellement produites. ADR pour chaque décision architecturale durable (`docs/decisions/ADR-XXX-*.md`).

## 13. Sécurité technique, gestion de versions et licences
- Git avec Git LFS pour `.uasset`, `.umap`, `.blend`, `.fbx`, textures lourdes ; `.gitignore` Unreal, DDC/Binaries/Intermediate/Saved exclus.
- Dépôt tiers préservé, sous-module ou copie attribuée, licence MIT incluse, références copyright et licences assets séparées.
- Pas de clés Steam/EOS/API dans Git. Éviter dépendances fermées inutiles et applications tierces incertaines.
- Fonctionnalités réseau exposées seulement après validation ; aucune donnée sensible de joueur dans logs.

## 14. Backlog initial réordonné — art d'abord

| ID | Ticket / résultat vérifiable | Dépendances | Priorité |
|---|---|---|---|
| ART-001 | Bible de références licites, captures, choix d'interprétation et nuances animé/jouet | aucune | P0 |
| ART-002 | Contrat Blender↔Unreal (mesures, noms, pivots, sockets, rig, export) | ART-001 | P0 |
| ART-003 | Thunderhawk graybox articulé `.blend` + road→flight→road | ART-002 | P0 |
| ART-004 | Rendu 360° + vidéo de transformation, revue de clipping | ART-003 | P0 |
| UE-ART-001 | Projet `MASK_AssetLab` vierge, import testé et animation fonctionnelle | ART-003 | P0 |
| ART-005 | Thunderhawk Hero détaillé + version Gameplay optimisée | UE-ART-001 | P1 |
| ART-006 | Matt Trakker riggé, Spectrum séparé, test dans cockpit | ART-002, UE-ART-001 | P1 |
| ENV-001 | Showroom Boulder Hill autonome avec commande transformation | UE-ART-001 | P1 |
| AUD-001 | Audit du dépôt VehicularCombat à commit SHA fixé | aucune ; **parallèle** | P0 |
| AUD-002 | Matrice licences et inventaire des assets tiers | AUD-001 | P0 |
| AUD-003 | Cartographie classes C++, Blueprints, réseau, dépendances | AUD-001 | P0 |
| ENG-001 | Baseline origine compilée ou échec documenté | AUD-001 | P1 |
| ENG-002 | Comparaison fork migré vs UE vierge, ADR base de jeu | AUD-002, AUD-003, ENG-001 | P1 |
| ENG-003 | Implémentation conduite + intégration Thunderhawk importable | ENG-002, UE-ART-001 | P1 |
| VEH-001 | Transformation intégrée gameplay solo puis autoritative réseau | ENG-003 | P1 |
| VEH-002 | Physique Flight, décollage et atterrissage | VEH-001 | P1 |
| COM-001 | Armes, projectiles, dégâts, collision répliqués | ENG-003 | P1 |
| NET-001 | Session serveur + 2 joueurs, mouvement et transformation visibles | VEH-001, COM-001 | P1 |
| MSN-001 | Mission coop courte briefing→récompense | VEH-002, NET-001 | P2 |
| PRG-001 | Garage local, sauvegarde et collection initiale | MSN-001 | P2 |
| NET-002 | Coop 4–6, persistance multiuser et tests de charge | MSN-001 | P3 |

Les statuts sont `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE (preuve)` ou `UNTESTED`. Une tâche artistique peut être `DONE` pour Blender et encore `UNTESTED` pour Unreal : mentionner les deux états séparément.

## 15. Conditions de bifurcation et dépendances

**VehicularCombat est optionnel** : si licence d'assets, dette technique, migration ou architecture réseau posent problème, créer un jeu Unreal neuf et ne reprendre que les modules autorisés. Cette décision n'interrompt **pas** Blender ni le showroom `MASK_AssetLab`.

**Interrompre provisoirement la finition du modèle Hero**, mais pas le travail sur le graybox, si l'import révèle pivots erronés, contraintes irréalisables, clipping systématique, dimensions incompatibles cockpit/pilote, ou performance très éloignée du budget. Corriger A2 puis reprendre A3.

**Ne jamais faire dépendre** `art_source/Thunderhawk/` du schéma interne de classes d'un dépôt tiers. Préférer interfaces/assets data-driven et adaptateurs Unreal.

## 16. Mode opératoire Claude Code / Codex

1. Lire cette spécification et construire la liste de tâches à partir du **Volet A**. **Commencer par ART-001 et ART-002**, puis ART-003 ; AUD-001 peut se faire parallèlement, sans bloquer la modélisation.
2. Vérifier les outils disponibles : `blender --version`, `python`, modules disponibles, Unreal Editor et compilateur, espace disque. S'ils sont absents, ne pas déclarer un `.blend`/`.uasset` valide sans l'avoir ouvert ; scripts `bpy` + instructions sont un livrable intermédiaire seulement.
3. Installer une arborescence de projet neutre, documenter provenances et licences, puis écrire des **scripts Blender idempotents** si applicable, avec sauvegarde source et exports versionnés.
4. Générer **d'abord la structure et transformation** ; inspecter turntable et séquences réellement rendues ; corriger pivots/échelle avant détails PBR.
5. Créer un projet UE vierge d'import et valider le parcours Blender→UE avant décision sur VehicularCombat. Ne pas attendre l'audit B0 pour effectuer A0–A2.
6. En parallèle, auditer le code tiers à SHA verrouillé et produire une matrice comparative ; **ne migrer VehicularCombat qu'après l'ADR B1**.
7. Documenter `COMPLETED`, `BLOCKED`, `NOT_RUN`, fichiers modifiés, commandes réellement exécutées et preuves (rendus, screenshots, logs), problèmes et prochaine tâche. Tests inexistants ne sont jamais supposés réussis.
8. Chaque changement important est petit, réversible, versionné et accompagné d'un contrat d'acceptation. Demander confirmation uniquement en cas de dépense, licence, ressource manquante indispensable ou décision irréversible.

### Prompt maître — à coller dans Claude Code ou Codex

> Tu es lead technical artist Blender et lead engineer Unreal du projet M.A.S.K. Project Mayhem. Lis intégralement `MASK_Project_Mayhem_SPEC_Claude_Code_Codex_v2.md`. **La première priorité est la création de Thunderhawk 3D sous Blender, indépendamment de VehicularCombat.** Commence par ART-001/ART-002 : bible de références, mécanisme transformable, conventions et contrat 3D. Puis livre ART-003 : graybox articulé de Thunderhawk dans un véritable `.blend`, si Blender est disponible, avec animation aller/retour, fichiers sources, renders de validation et contrôle des pivots. Prépare ensuite `MASK_AssetLab` sous Unreal vierge pour tester l'import rapidement. En parallèle seulement, lance AUD-001/AUD-003 sur VehicularCombat ; **ne migre pas le dépôt avant comparaison et ADR**. Ne déclare jamais l'art final ou les tests Unreal terminés sans preuves. Fournis tableau de fichiers, changements, commandes exécutées, tests, blocages et étape suivante.

## 16 bis. Arborescence maîtresse

```
ProjectMayhem/
  MASK_Project_Mayhem_SPEC_Claude_Code_Codex_v2.md
  README.md
  docs/
    art/THK_asset_contract.md
    art/reference_manifest.csv
    engine/vehicularcombat_audit.md
    decisions/ADR-001-engine-base.md
    qa/
    progress/
  art_source/
    Thunderhawk/
      reference_manifest.csv
      Thunderhawk_Master.blend
      Thunderhawk_Transformation.blend
      scripts/
      renders/
      textures/
      exports/
      asset_manifest.json
    MattTrakker/
    Spectrum/
  unreal/
    MASK_AssetLab/                  # Viewer UE autonome, dès A2
    MASK_Game/                      # Démarre après décision B1
  external/
    VehicularCombat/                # Référence externe, SHA fixé, licences
  tools/
    validate_art_assets.py
```

## 17. Critères de succès du programme

**Succès P0 :** deux joueurs conduisent deux véhicules en réseau, voient les transformations, échangent des tirs et subissent les mêmes conséquences sur serveur/clients.  
**Succès P1 :** Thunderhawk fidèle à l'animé avec transformation articulée fluide et vol ; Matt Trakker et Spectrum dans le showroom Boulder Hill.  
**Succès P2 :** mission coop rejouable à deux, récompense enregistrée, garage consultable, aucun avantage pay-to-win.  
**Succès P3 :** extension progressive à 4–6 joueurs, véhicules supplémentaires et contenu narratif, après test de charge et sécurité réseau.

---

**Règle de clôture :** une excellente démo isolée ne constitue pas une preuve de fonctionnement multijoueur. Un jeu visuellement fidèle mais impossible à intégrer n'est pas un asset livré. Un build sans démonstration de la transformation ne valide pas la direction de M.A.S.K. Les trois axes — **fidélité, gameplay, réseau** — doivent progresser avec preuves séparées.
