# Fichiers de la livraison Rhino / Hurricane

Inventaire exact : [validation/fleet/files.json](validation/fleet/files.json) — 549 fichiers ajoutés ou modifiés par rapport à `cfab049`.

Les fichiers existants sont conservés. Les assets `.uasset` de Rhino et Hurricane, leurs atlas/FBX et les copies `.blend` indépendantes constituent la majorité des ajouts. Les exécutables et journaux complets dans `Saved` restent locaux.

## Code C++

- `Source/VehicularCombat/Private/AI/VehicleBotController.cpp`
- `Source/VehicularCombat/Private/AI/VehicleBotController.h`
- `Source/VehicularCombat/Private/Components/HealthComponent.cpp`
- `Source/VehicularCombat/Private/Core/CustomGameMode.cpp`
- `Source/VehicularCombat/Private/Core/CustomGameMode.h`
- `Source/VehicularCombat/Private/Core/OnlineGameInstance.cpp`
- `Source/VehicularCombat/Private/Core/OnlineGameInstance.h`
- `Source/VehicularCombat/Private/MASK/HurricanePawn.cpp`
- `Source/VehicularCombat/Private/MASK/HurricanePawn.h`
- `Source/VehicularCombat/Private/MASK/MaskAssetEditorLibrary.cpp`
- `Source/VehicularCombat/Private/MASK/MaskAssetEditorLibrary.h`
- `Source/VehicularCombat/Private/MASK/MaskVehicleDefinition.h`
- `Source/VehicularCombat/Private/MASK/MaskVehicleModeComponent.cpp`
- `Source/VehicularCombat/Private/MASK/MaskVehicleModeComponent.h`
- `Source/VehicularCombat/Private/MASK/RhinoPawn.cpp`
- `Source/VehicularCombat/Private/MASK/RhinoPawn.h`
- `Source/VehicularCombat/Private/MASK/ThunderhawkPawn.cpp`
- `Source/VehicularCombat/Private/MASK/ThunderhawkPawn.h`
- `Source/VehicularCombat/Private/Pawns/PlayerWheeledVehiclePawn.cpp`
- `Source/VehicularCombat/Private/Pawns/PlayerWheeledVehiclePawn.h`
- `Source/VehicularCombat/Private/Tests/FleetSmoke.cpp`
- `Source/VehicularCombat/Private/Tests/HurricaneSmoke.cpp`
- `Source/VehicularCombat/Private/Tests/MigrationSmoke.cpp`
- `Source/VehicularCombat/Private/Tests/ThunderhawkSmoke.cpp`
- `Source/VehicularCombat/Private/Tests/TrainingSmoke.cpp`
- `Source/VehicularCombat/Private/UI/MainMenuWidget.cpp`
- `Source/VehicularCombat/Private/UI/MainMenuWidget.h`
- `Source/VehicularCombat/Private/UI/PlayerHUD.cpp`

## Autres ensembles

- `Content/MASK/Rhino/`, `Content/MASK/Hurricane/` : véhicules, équipages, masques, poses, matériaux, Blueprints et étiquettes de cuisson.
- `Content/MASK/Thunderhawk/` : affectations des matériaux de Matt/cheveux/Spectrum et verre corrigé.
- `SourceArt/MASK/Rhino/`, `SourceArt/MASK/Hurricane/`, `SourceArt/MASK/Editable/` : exports et sources artistiques préservées, avec empreintes.
- `Tools/Art/` : export/revue MCP, import et finalisation Unreal.
- `Tools/Migration/` : essais Rhino/Hurricane, extension du réseau et liste des assets Blueprint contrôlés.
- `Jouer-MASK.cmd`, `.gitignore`, `docs/` : lancement de r2, documentation et preuves de validation.
