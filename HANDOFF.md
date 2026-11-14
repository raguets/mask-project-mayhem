# Handoff — Manta / Pinewoods —14 novembre2026

## Objectif et état

Modèle Manta/Vanessa/Whip consolidé après toutes les corrections ; puis intégration Pinewoods demandée explicitement : même dynamique route/avion que Thunderhawk/Raven, faction VENOM, départ hors base MASK. Compétence projet mask-asset-production lue et appliquée, fiche lue avant images. Anatomie/cockpit interprétés avec autorisation générale ; catégories de références distinctes.

## Modèle vérifié

Source canonique `art_source/Manta/Manta_V23_Assembly.blend`. Sources indépendantes `Manta_V23_Vehicle.blend`, `art_source/Vanessa_Warfield/VanessaWarfield_V1.blend`, `Whip_V1.blend` réellement rouvertes :3 réussites,0 dépendance invalide, même corps/tête/rig dans4 états. Détails et commandes : `art_source/Manta/README.md`, liste complète `CORRECTIONS_UTILISATEUR.md`.

V23 garde l'habitacle raccourci, l'arrière réduit10%, contours larges plats des4 vitrages galbés, roues rondes centrées et ailes sous caisse. Capot convexe avec courses courtes indépendantes, marteau25mm devant les canons, missiles30°. Planche porte-feux au niveau carrosserie en route, horizontale juste au-dessus des jets en avion, supports horizontaux puis pivotants. Les demandes récentes remplacent le ratio initial40/30/30 ; ne pas affirmer qu'il reste exact.

Rendus11 vues terminés/inspectés dans `art_source/Manta/renders/v23`. Contrôles `validation_full_v23.json` et `hood_trim_validation_v23.json` :241 phases, paires de surfaces sans croisements ni containment missile détecté. `semantic_qa_v23.json` :31 réussites. Limite : paires/échantillons finis, pas toutes collisions ni suspension/physique du jeu. Coiffure, visage, prise fine des doigts encore perfectibles. Revue4 états en cours via MCP : `renders/v23_character`, restaurée automatiquement au terme. Ne pas muter Blender tant que lock `_mask_asset_review_active` présent.

## Intégration en cours

Export MCP terminé : `VehicularCombat/SourceArt/MASK/Manta`,20 groupes rigides,97 échantillons,4 roues. Source game-ready `art_source/GameReady/Manta/Manta_GameReady.blend`. Animations Vanessa terminées dans `SourceArt/MASK/OnFoot/Vanessa` ; même squelette. Scripts `Tools/Art/prepare_manta_game.py`, `author_vanessa_motion.py`, `import_manta_all.py`, `finalize_manta.py`.

Classe native `MantaPawn.h/.cpp` dérive Thunderhawk, roues29.6cm et suspension visuelle coupée pendant déploiement comme Raven. Ajouts dans menu, registre flotte (7 familles), ordre sélection60 et retry mission. Pinewoods `SilentValleyGameMode` traite Switchblade ET Manta par site extérieur routier hors bounds Boulder Hill élargis10m, joueurs/IA/réapparitions. Échec de recherche interdit retour garage. Réglages dynamiques copiés de Thunderhawk à l'import, faction VENOM.

Compilation UE5.8 réussie : `Saved/Migration/VehicularCombatEditor-20261114-193742.log` (avertissements moteur préexistants). Commande `powershell.exe -NoProfile -ExecutionPolicy Bypass -File VehicularCombat/Tools/Migration/Invoke-UE58.ps1 -Task Build`. Import Unreal lancé, session exec73632, script `Import-Manta.ps1 -RunName manta-import-r1`, log `VehicularCombat/Saved/Art/manta-import-r1/editor.log` et launch.json avecPID. NE PAS affirmer l'import/test passé avant lecture rapports. Tests prévus `Test-Manta.ps1`, console `MASK.MantaSmoke` : spawn naturel extérieur AVANT placement explicite sur route800m ; fixture altitude40m ensuite pour frein, avance minimale, virage et retour route. Tests injectés, pas pilotage manuel.

## État Git et conservation

Repo racine effectif `G:/DEV/mask-project-mayhem`, branchemain, HEADbae5272 Added switchblade ; Unreal sous `VehicularCombat`. Noncommitté : nouveaux assets/scripts Manta/Vanessa/GameReady,7 fichiers C++ communs modifiés plus classe/test Manta, documentation/handoff. Aucun commit créé. Changements utilisateur conservés : fiche Manta modifiée, références Switchblade déplacées vers `Images de reference/Terminés`, nouveau dossier Firefly. Ne pas restaurer/supprimer ces changements. Historique handoff antérieur dans `docs/progress/2026-11-14-handoff-before-manta.md`.

## Première action recommandée

Lire `VehicularCombat/Saved/Art/manta-import-r1/editor.log` et `Saved/Art/manta-import.json`, puis reprendre session73632 ; corriger tout échec d'import avant `powershell.exe -NoProfile -ExecutionPolicy Bypass -File VehicularCombat/Tools/Migration/Test-Manta.ps1 -RunName manta-r1`.
