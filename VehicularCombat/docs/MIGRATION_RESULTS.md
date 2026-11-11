# Résultats de la migration

Réglage avion actuel : [plage de vitesse progressive de 50 à 300 km/h](AIRCRAFT_SPEED_RANGE.md).

Dernier correctif : [stabilité des roues arrière d'Hurricane et vitesse maximale de vol réduite](HANDLING_FIXES.md).

Dernière évolution : [transformations en mouvement et dynamique avion/hélicoptère](DYNAMICS_IMPLEMENTATION.md). La [livraison de la flotte du 7 novembre](FLEET_IMPLEMENTATION.md) reste documentée séparément ; son ancien stationnement Rhino est remplacé par le rappel immédiat demandé le 8 novembre.

Suite du 7 novembre : [distribution Windows, Thunderhawk, Matt masqué et commandes Xbox](THUNDERHAWK_IMPLEMENTATION.md). Les résultats ci-dessous conservent le périmètre de la migration initiale.

Mise à jour du parcours utilisateur : [menu Host/Join et entraînement solo contre trois bots](PLAYTEST_FIXES.md). Cette passe complète les essais d'API initiaux ci-dessous ; aucune intégration M.A.S.K. ajoutée.

Dépôt réel : `G:/DEV/mask-project-mayhem/VehicularCombat`, branche `migration/ue58`. Moteur installé : UE 5.8.2. Les sources Blender, le laboratoire d'assets et les créations M.A.S.K. sont hors périmètre et restent inchangés.

## Résultats exécutés

| Vérification | Résultat |
|---|---|
| Editor et Game Win64 Development, UBT | Réussis, cible UE 5.8, C++20 et génération UHT |
| Ouverture Editor automatisée | Initialisation et MapCheck 0/0 ; fermeture Slate, sortie 0 en NullRHI ; passe avec rendu initialisée puis fermée également |
| Autotests Smoke du moteur | **429 réussis, 0 échec**, avec `-culture=en` pour ce processus de test |
| CompileAllBlueprints du projet | **28 Blueprints, 0 erreur, 0 avertissement, 0 échec de chargement**, sortie 0 |
| DataValidation du projet | **545 ressources valides**, incluant les deux cartes et les données de scène reconstruites, sortie 0 |
| Deux processus de jeu, LAN Null / IpNetDriver | **Réussi**, `grounded-render`, 23 contrôles hôte et 19 client, deux sorties 0, scénario d'environ 47 s. Rapport archivé dans `docs/validation/ue58-validation.json` |
| Carte jouable et véhicule possédé | `/Game/Maps/TestMaps/Test`, BP_PlayerVehicle d'origine |
| Conduite / contacts | Entrées W et D injectées au PlayerController, déplacements constatés, quatre roues Chaos en contact au sol |
| Mouvements réseau | Mouvement de l'hôte observé côté client et mouvement du client observé côté serveur |
| Tir et munitions | Entrée de tir client traitée côté serveur ; projectiles visibles sur les deux instances ; consommation de munitions répliquée |
| Impact et dégâts | Vrai RPC de tir et collision du projectile du fusil ; santé serveur **1000 → 925**, baisse également observée sur le client ; hôte toujours au sol et droit après placement du scénario |
| Lance-roquettes | Projectile créé sur les deux instances, données explosives présentes et chargeur consommé ; effets locaux d'expiration journalisés |
| Mort / réapparition | Test distinct par injection de dégâts autoritaires ; ancien véhicule détruit, nouveau pawn possédé et santé restaurée sur le client |
| Interface / rendu | HUD original et widget dans le viewport sur les deux instances ; captures de l'hôte inspectées, véhicule droit sur la carte, fusil et munitions **30/120 puis 24/120** |

Les commandes, échecs intermédiaires et résultats détaillés sont consignés dans le journal. Les logs et captures de chaque exécution restent dans `Saved/Migration/` ; une synthèse des preuves est conservée dans Git sous `docs/validation/`.

Captures finales inspectées : [avant conduite](validation/ue58-host-ready.png), [après tir](validation/ue58-host-after-fire.png). Les impacts et l'expiration explosive ont chacun leur chemin local configuré exécuté sur les deux pairs ; le test utilise `-nosound`, donc l'écoute audio n'est pas validée.

## Méthode et limites

Les essais LAN sont des tests d'intégration automatisés avec deux vrais processus Unreal. Les marqueurs de fichiers synchronisent seulement le scénario ; les véhicules, tirs et dégâts passent par le réseau du jeu. Le test d'impact arrange la position de l'hôte autoritaire et la direction du canon puis appelle le vrai RPC de tir. Il ne valide pas une visée humaine au réticule. Les captures graphiques sont une inspection visuelle distincte ; aucun test manuel prolongé n'est revendiqué.

Steam/Internet, serveur dédié, latence/pertes de paquets, packaging distribué et plateformes mobiles ne sont pas validés par ces essais. Les quatre roues et leurs contacts ainsi que le mouvement physique sont contrôlés, sans certification exhaustive des suspensions ou de chaque obstacle. Le lance-roquettes est vérifié pour création, munitions, configuration et expiration ; son rayon de dégâts n'a pas de test dédié. Les collectibles, toutes les commandes de menu et les réglages graphiques ne font pas l'objet d'une recette manuelle exhaustive. La préparation M.A.S.K. reste une proposition dans `MASK_ARCHITECTURE_PROPOSAL.md`, sans import d'assets ni implantation de transformations.

## Avertissements et travaux restants

- MSVC 14.51 compile, mais UBT le signale plus récent que les familles préférées du moteur. Aucun compilateur supplémentaire installé.
- Trois autotests de formatage/localisation du moteur échouent en culture française et réussissent en anglais : détails dans le journal. La langue habituelle du projet/éditeur n'a pas été changée ; les tests anglais n'effacent pas les erreurs françaises consignées.
- RawInput est déprécié en 5.8 ; conservé pour préserver les entrées originales, à remplacer de façon explicite lors d'une future passe d'input.
- Le clone ne fournissait pas `Test_BuiltData`. Éclairage et réflexions ont été réellement reconstruits et la carte resauvegardée avec UE 5.8. Le registre résultant est conservé dans Git ; l'avertissement visible de réflexions non construites et l'erreur de chargement ont disparu. Qualité Preview à reprendre pour une carte de production.
- Deux anciens chemins de template subsistent dans les réglages : carte SimpleMap `/Game/VehicleAdv/Maps/VehicleAdvExampleMap` et interface tactile `/Game/Vehicle/Sedan/SedanVirtualJoysticks`. Ils ne sont pas les cartes de démarrage/jouables Windows testées. Leur remplacement devra préserver les usages concernés.
- Le Blueprint de réglages émet encore des commandes devenues inconnues (`r.PostProcessAAQuality`, `FoliageQuality`). Les réglages conservés demandent une revue ciblée de l'interface, sans remplacement arbitraire du contenu binaire.
- Les composants visuels de caméra en build Editor peuvent produire des avertissements NetGUID sur les frustums/proxies ; ils ne sont pas des preuves d'échec des mouvements répliqués, lesquels sont mesurés séparément.
- Vérifier les licences des lots tiers crédités dans le README avant distribution. La licence MIT du code ne constitue pas une preuve de licence de chaque fichier tiers.

## Fichiers modifiés ou ajoutés

- `VehicularCombat.uproject` : association 5.8.
- `Source/VehicularCombat.Target.cs`, `Source/VehicularCombatEditor.Target.cs` : defaults V7, ordre UE 5.8.
- `Source/VehicularCombat/VehicularCombat.Build.cs` : dépendances UMG, OnlineBase et Json pour les outils Development.
- `Private/Core/OnlineGameInstance.h/.cpp` : sessions et protection des opérations asynchrones, signatures Blueprint conservées.
- `Private/Core/CustomGameMode.cpp` : file de réapparition et sorties de session.
- `Private/Pawns/BaseWheeledVehiclePawn.cpp` : énumérations strictes, attache d'arme sans soudure, garde des demandes de tir.
- `Private/Pawns/PlayerWheeledVehiclePawn.h/.cpp` : initialisation locale de l'hôte/client et protections UI.
- `Private/Actors/AmmoPickupActor.cpp`, `HealthPickupActor.cpp`, `PickupActor.cpp`, `SpawnManagerActor.cpp`, `SpeedBoostPickupActor.cpp`, `WeaponPickupActor.cpp` : cases d'énumération explicites ; initialisation d'arme et accès au propriétaire.
- `Private/Actors/SpawnManagerActor.h` : déclaration explicite nécessaire à la cible Game.
- `Private/Actors/ProjectileActor.cpp` : table explosive, exclusion du tireur/accessoires, dégâts côté serveur et présentation locale des impacts sur chaque pair.
- `Config/DefaultEngine.ini` : anciennes clés de rendu et minimum iOS obsolètes adaptés, profils de collision manquants et journalisation de diagnostic.
- `Content/Maps/TestMaps/Test.umap`, `Test_BuiltData.uasset`, `.gitignore` : conversion de la carte et conservation de ses véritables données d'éclairage/réflexions reconstruites.
- `Private/Tests/MigrationSmoke.cpp` : sonde opt-in, exclue de Shipping, sans exécution dans un jeu normal.
- `Tools/Migration/Invoke-UE58.ps1`, `Test-TwoPlayers.ps1`, `project-assets.allowlist` : commandes reproductibles et tests.
- `README.md`, `docs/MIGRATION_AUDIT.md`, `MIGRATION_LOG.md`, `MIGRATION_RESULTS.md`, `MASK_ARCHITECTURE_PROPOSAL.md`, `validation/ue58-validation.json`, `validation/ue58-host-ready.png`, `validation/ue58-host-after-fire.png` : documentation et preuves synthétiques.

Les chemins `Private/...` ci-dessus sont relatifs à `Source/VehicularCombat/`. Les originaux sont conservés dans l'historique Git ; seule la carte Test est resauvegardée, sans suppression d'asset. Les autres logs/cache/binaries générés restent dans les dossiers ignorés par Git. Aucun fichier Blender ni asset M.A.S.K. modifié.

## Ouvrir et jouer

1. Ouvrir un terminal PowerShell dans le dépôt `VehicularCombat/`.
2. Compiler : `.\Tools\Migration\Invoke-UE58.ps1 -Task Build`.
3. Ouvrir l'éditeur : `.\Tools\Migration\Invoke-UE58.ps1 -Task Editor`, ou double-cliquer `VehicularCombat.uproject` avec UE 5.8 installé.
4. Démarrer Play depuis MainMenu, puis créer une session LAN. Un deuxième joueur rejoint la session depuis le menu. Pour jouer directement sans l'éditeur : `-Task Play`.
5. W/A/S/D ou flèches : conduire ; Espace : frein à main ; clic gauche : tirer ; 1/2 : changer d'arme ; V : caméra ; Maj gauche : saut.

Pour reproduire l'essai local à deux processus : `-Task Network`. Pour les captures avec rendu de l'hôte : `-Task NetworkRender`. Une seule tâche de test réseau par machine à la fois (port de jeu et recherche LAN partagés). Le premier démarrage graphique attend la compilation initiale des shaders.

## Prochaine étape Thunderhawk

Valider d'abord la proposition d'architecture. Préparer ensuite une copie d'export Blender avec échelle/axes, quatre roues, pivots et collisions simples ; importer dans un dossier isolé et un pawn dérivé, en conservant BP_PlayerVehicle comme référence. Valider conduite et réseau avant transformation/vol. Matt et Spectrum restent des assets indépendants avec un seul personnage pour ses poses. Aucun de ces imports n'est effectué dans cette migration.
