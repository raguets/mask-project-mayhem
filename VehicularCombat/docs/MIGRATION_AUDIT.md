# Audit de migration UE 5.1 → 5.8

Audit initial du 6 novembre 2026. État de validation mis à jour dans `MIGRATION_LOG.md`.

## Environnement et sécurisation

- Windows 11 Professionnel x64, build 26200 ; 32 Go de RAM, 8 processeurs logiques.
- Le dépôt Git réel est `G:/DEV/mask-project-mayhem/VehicularCombat`, et non le dossier parent qui contient les créations Blender.
- Origine : `https://github.com/DanialKama/VehicularCombat`, commit initial `8d56e16`, branche initiale `main`, arbre propre. Branche de migration créée : `migration/ue58`.
- Moteur installé : `G:/Program Files/Epic Games/UE_5.8`, **5.8.2**, changelist 56702186. Aucune installation de moteur nécessaire.
- Visual Studio Community 2026 18.9.2 ; MSVC 14.51.36231 x64 présent. Cette famille n'est pas dans les versions préférées du fichier local `Windows_SDK.json` du moteur (14.50 et 14.44), sans être dans sa liste d'interdiction. Le verdict réel appartient à UBT.
- SDK Windows : le premier chemin registre était incomplet. UBT confirme le SDK **10.0.26100.0**, sous `C:/Program Files (x86)/Windows Kits/10`. Aucune installation nécessaire.
- .NET 10 fourni par le moteur. Aucun `cl`, `msbuild` ou `dotnet` global requis si les outils du moteur et de Visual Studio sont utilisables.

## Projet et contenu

`VehicularCombat.uproject` : association 5.1, module Runtime unique `VehicularCombat`, cibles Game et Editor, `BuildSettingsVersion.V2`. Ne pas renommer le module : les Blueprints référencent ses classes natives.

Dépendances déclarées : Core, CoreUObject, Engine, InputCore, ChaosVehicles, HeadMountedDisplay, PhysicsCore, NavigationSystem, OnlineSubsystem, OnlineSubsystemSteam, OnlineSubsystemUtils. UMG est utilisé par les classes UI mais n'est pas explicitement déclaré dans Build.cs : vérifier avec la compilation sans dépendre des inclusions transitives.

Plugins activés présents dans le moteur : ChaosVehiclesPlugin, RawInput, OnlineSubsystem, Null, Steam, Utils, Bridge. Aucun plugin propre au projet. PhysXVehicles et les sous-systèmes mobiles sont déclarés désactivés. Bridge est un outil de contenu existant, pas une raison de supprimer des assets.

Contenu initial : **542 `.uasset`, 2 `.umap`**, environ 250 Mio, plus film de démarrage et images. Cartes : `/Game/Maps/MainMenu` et `/Game/Maps/TestMaps/Test`. Les cartes de menu/démarrage et le GameInstance sont configurés dans DefaultEngine.ini. La carte de test est la destination de création de session. Aucun test automatisé propre au projet trouvé initialement.

## Systèmes identifiés

| Domaine | Classes / éléments |
|---|---|
| Véhicule Chaos | `ABaseWheeledVehiclePawn`, `APlayerWheeledVehiclePawn`, `UChaosWheeledVehicleMovementComponent`, BP_PlayerVehicle, WheelFront, WheelRear, courbes couple/direction |
| Entrées / caméra | Axis/Action historiques, caméras extérieure/intérieure, bras, retour de rotation, tableau de bord |
| Armes | AWeaponPickupActor, armes fusil/lance-roquettes, munitions, états répliqués, RPC serveur et effets multicast |
| Projectiles / impacts | AProjectileActor, UProjectileMovementComponent, tables de dégâts ponctuels/explosifs, matériaux physiques, particules et décalcomanies |
| Santé / mort | UHealthComponent, santé répliquée, dégâts autoritaires, restauration, mort, ACustomGameMode et réapparition |
| État joueur | ACustomPlayerState, armes primaire/secondaire répliquées |
| Collectibles | APickupActor, santé, munitions, accélération, armes et ASpawnManagerActor |
| Sessions | UOnlineGameInstance, API OnlineSubsystem classique ; Steam AppId 480 et repli IpNetDriver/Null |
| Interface Blueprint | APlayerHUD, UInCarWidget et contenu UI ; événements natifs complétés par Blueprints |

## Risques à vérifier et défauts statiques

1. Defaults UBT 5.1 obsolètes : paramètres de compilation partagés avec UnrealEditor, niveau C++, ordre des inclusions et en-têtes transitifs. Migrer depuis les erreurs réelles, conserver les avertissements motivés.
2. Déplacement/suppression de modules, notamment HeadMountedDisplay/XRBase, et propriétés UObject désormais privées. Vérifier les headers du moteur installé avant correction.
3. API OnlineSubsystem : constantes de recherche de présence et compatibilité Steam/lobbies. Sessions locales à tester avec Null sans prétendre valider Steam par un test LAN.
4. `OnlineGameInstance` contient deux implémentations de recherche/gestion partiellement raccordées : noms `My Session` et `NAME_GameSession` incohérents, delegates non initialisés, pointeurs/recherche/index non protégés, comptage des places erroné. Risques antérieurs à la migration.
5. Projectiles créés par multicast sur chaque machine, dégâts limités au serveur : vérifier doublons, autorité et effets avant de modifier ce comportement.
6. Caméra et initialisation conditionnées parfois au rôle AutonomousProxy : vérifier aussi l'hôte listen-server, qui est autoritaire et local.
7. Conserver les profils de collision personnalisés, sockets d'armes, canaux et tables ; une compilation C++ ne valide ni roues/suspension ni graphe Blueprint.
8. Dépréciations de rendu/physique et sérialisation des assets : charger et compiler les Blueprints avec UE 5.8 avant toute conversion en masse. Ne supprimer aucun `.uasset` ou `.umap` pour faire disparaître une erreur.

## Licences et dépendances de contenu

Le dépôt fournit une licence MIT (Danial Kamali, 2022). Son README crédite **Military Weapons Silver**, **FPS Weapon Bundle** et **FlatIcon**. Ces crédits ne prouvent pas les droits de redistribution de tous les fichiers tiers : vérifier la provenance et les licences de chaque lot avant publication. L'AppId Steam 480 correspond à une configuration de développement ; aucun accès à un service commercial n'est considéré acquis.

Les sources Blender et le laboratoire `../unreal/MASK_AssetLab` restent hors périmètre. Aucun asset M.A.S.K. ne sera intégré dans cette migration.

## Clôture de l'audit initial

Les incompatibilités effectivement corrigées et leurs commandes sont détaillées dans `MIGRATION_LOG.md`. Editor/Game compilent avec les outils installés ; aucun module n'a été renommé. Les profils de collision absents et le cache de scène manquant ont été traités sans supprimer les assets. Le bilan final, les fichiers modifiés et les limites des tests sont dans `MIGRATION_RESULTS.md`. Une proposition d'architecture M.A.S.K. séparée reste à valider avant toute intégration.

## Références techniques

Priorité aux sources du moteur installé : `Engine/Build/Build.version`, `Engine/Config/Windows/Windows_SDK.json`, UnrealBuildTool, headers Chaos et OnlineSubsystem. Référence publique : [notes Epic UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes). Les incompatibilités ci-dessus sont des risques ou constats statiques ; les résultats exécutés sont consignés séparément dans le journal.
