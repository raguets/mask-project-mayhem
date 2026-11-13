# Handoff — Switchblade dans Pinewoods — 13 novembre 2026

## Objectif et demande préalable

Intégrer Switchblade, Miles Mayhem et Viper dans Pinewoods (`/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout`). Premier véhicule hélicoptère / avion : départ hélicoptère, stationnaire et atterrissage possibles ; avion transformé avec avance obligatoire. Départ extérieur à Boulder Hill, véhicule VENOM avec espace de décollage.

Dernière demande : vérifier d’abord si l’agent peut lancer Unreal. Réussi : UE5.8 ouvert par l’agent avec le projet `VehicularCombat/VehicularCombat.uproject`, PID 23864, fenêtre « VehicularCombat - Unreal Editor », Responding=True revérifié. L’utilisateur n’a pas besoin de le lancer. Log `VehicularCombat/Saved/Art/switchblade-editor-startup.log`, manifeste `switchblade-editor-startup-launch.json`. Carte chargée, MapCheck sans erreur/avertissement ; des textures Baltic/Aleppo manquent et des messages de tests internes moteur existent : le démarrage ne valide pas le gameplay. Laisser l’éditeur ouvert pour cette vérification ; avant compilation, fermer proprement cette session créée par l’agent en préservant tout changement éventuel.

## Sources artistiques et export vérifiés

Source canonique `art_source/Switchblade/Switchblade_V22_Assembly.blend`, anciennes versions conservées. V22 corrige la hauteur réelle du plancher fixe (dessus 0,94 m) après V21 ; pieds/palonnier relevés de 16 cm. Dernières corrections V21 : supports de patins descendant d’avant en arrière avec seule convexité vers l’avant ; petites ailes prolongées à X0,30 pour rejoindre les principales, deux canons avant télescopiques ; nez continuant les plans vitre/quille, prises d’air métalliques et peintures d’ailes, pales élargies avec base abaissée après repli.

Sources indépendantes sauvegardées et réellement rouvertes : `Switchblade_V22_Vehicle.blend`, `art_source/Miles_Mayhem/MilesMayhem_V3.blend` et `Viper_V3.blend`. Rapport `art_source/Switchblade/standalone_validation_v22.json` : dépendances valides, un rig, même personnage dans les quatre états pose/masque. Réalisme personnages/cockpits autorisé sans nouvelle confirmation. Visage, cheveux, doigts et contacts fins restent perfectibles.

Rendus V16/V18/V21 terminés, plusieurs angles réellement inspectés. `motion_validation_v21.json` : 121 phases sur paires sélectionnées, 120 angles rotor, pilote/verrière avec/sans masque sans intersection détectée ; limite : pas une preuve volumique exhaustive. Attention : l’ancien rapport V21 donne le plancher avant correction V22 et son écart rotor ne représente que la pale haute.

Export jeu terminé via Blender MCP9876, scripts `VehicularCombat/Tools/Art/prepare_switchblade_game.py` et `author_miles_motion.py`. `SourceArt/MASK/Switchblade/progress.json` COMPLETE : 17 groupes, zéro roue, FBX visuel/physique/personnage/masque/animations et textures. `SourceArt/MASK/OnFoot/progress.json` COMPLETE pour Miles. Source `art_source/GameReady/Switchblade/Switchblade_GameReady.blend`. Aucun import Unreal effectué ni gameplay validé.

## Code en cours, non compilé

Modifications natives sauvegardées : catégorie HelicopterAirplane et faction VENOM, nouveau `Private/MASK/SwitchbladePawn.*`, dynamique hélico en état de base et avion en Flight, conversion inverse sans atterrissage imposé, rotor tournant seulement en hélico, châssis sans roues et collisions patins, sortie pilote adaptée au sol. Spawn extérieur recherché sur route hors enveloppe Boulder Hill dans `SilentValleyGameMode`, ajout famille aux menus/flotte/IA, textes HUD et faction mission. Ces changements ne sont PAS compilés/testés ; inspecter les diffs avant de poursuivre. Points ouverts : cohérence équipe ennemie lorsque joueur VENOM, textes de pause génériques, validation Chaos sans roues, stabilité au sol et transitions aériennes.

## État Git et suite

Dépôt à la racine workspace (code sous VehicularCombat), branche main, HEAD `837f48c Added condor`. Aucun commit/indexation. Diff suivi : AGENTS, HANDOFF, Jouer-MASK et 16 fichiers C++/headers ; non suivis : SwitchbladePawn, scripts export, SourceArt Switchblade/Miles, sources Blender, archive `docs/progress/2026-11-13-handoff-before-switchblade.md`. Préserver ces changements et anciennes sources. Pas de compilation/import en cours ; éditeur PID23864 seul processus Unreal confirmé.

Suite : inspecter les modifications ; créer import Switchblade/Miles depuis les outils Condor/Raven, avec catégorie et faction correctes, verre magenta et rotor_base_mode. Fermer proprement l’éditeur puis compiler via `VehicularCombat/Tools/Migration/Invoke-UE58.ps1 -Task Build`, importer et valider réellement dans Pinewoods : départ extérieur, décollage, stationnaire, conversion avion sans stationnaire, retour hélico en vol, atterrissage, sortie/retour Miles et régression Condor. Rendre et inspecter le résultat avant d’annoncer l’intégration terminée.

## Première action recommandée

Exécuter `git diff -- VehicularCombat/Source/VehicularCombat/Private/SilentValley/SilentValleyGameMode.cpp VehicularCombat/Source/VehicularCombat/Private/MASK/MaskDynamicsComponent.cpp` pour revoir les deux adaptations principales avant compilation/import.
