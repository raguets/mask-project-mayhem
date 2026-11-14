from pathlib import Path
P=Path(__file__).resolve().parents[2];A=P/'art_source/Manta'
(A/'README.md').write_text('''# Manta / Vanessa Warfield / Whip

Source assemblée courante : `Manta_V23_Assembly.blend`. Production et inspection via Blender MCP installé (port9876). Sources indépendantes réellement rouvertes : `Manta_V23_Vehicle.blend`, `../Vanessa_Warfield/VanessaWarfield_V1.blend`, `../Vanessa_Warfield/Whip_V1.blend`. Anciennes itérations conservées.

## Contrôles éditables

`Manta_Control["transform"]` : 0 route, 1 avion. Timeline1–121 aller,121–161 maintien,161–281 retour. Pour un réglage manuel, détacher la courbe de cette propriété avant de changer de frame. `VanessaWarfield_Rig` : `driving_pose`, `in_vehicle` (0/1), `mask_on` booléen. Un seul corps/visage/rig et Whip séparé. Forme `DrivingGrip` éditable. `door_open` reste un contrôle de travail partiel, non validé ; livraison portes fermées.

## Corrections consolidées

Liste complète dans `CORRECTIONS_UTILISATEUR.md`. V23 conserve l'habitacle raccourci, l'arrière réduit de10%, les roues rondes centrées, les ailes élargies rangées sous la caisse, le pare-brise trapézoïdal galbé et les trois vitres arrière courbes. Leurs contours sont des bandes larges et plates. La planche de feux masque les jets en route ; ses deux supports pivotent depuis l'horizontale, sans dépasser les feux. Capot continûment convexe, joints serrés, canons fixes indépendants à course courte, marteau seulement25mm au-delà des canons déployés. Trois missiles à30°, lanceur réduit et sortie tardive après dégagement.

La dernière demande de raccourcissement de l'habitacle puis de l'arrière prime sur le ratio initial40/30/30 ; ne pas présenter ce ratio initial comme une mesure finale exacte.

## Preuves et limites

Vues de la même source : `renders/v23` (11 vues, caméras évaluées vérifiées). `validation_full_v23.json` et `hood_trim_validation_v23.json` :241 phases, aucun croisement dans les paires contrôlées, aucun échantillon de missile contenu dans le capot. `semantic_qa_v23.json` :31 contrôles géométriques réussis. `standalone_validation_v23.json` :3 sources rouvertes, dépendances valides, même personnage dans les4 états. Ce sont des contrôles finis, pas une preuve d'absence universelle de collisions.

Références, catégories et interprétations dans `REFERENCE_NOTES.md`. Anatomie/cockpit autorisés, dimensions et mécanismes cachés estimés. Finesse du visage, mèches de cheveux et prise fine des doigts restent perfectibles ; ne pas prétendre à une fidélité photographique. Base féminine continue CC0 Blender Human Base Meshes dans `../AnatomyBase`.

## Intégration Unreal

Export V23 : `VehicularCombat/Tools/Art/prepare_manta_game.py`,97 échantillons et20 groupes rigides,4 pneus persistants. Assets dans `/Game/MASK/Manta`, Vanessa/Whip sur le même squelette. Classe `AMantaPawn` dérive du pilotage Thunderhawk ; réglages de dynamique copiés de Thunderhawk comme Raven. Faction VENOM, route/avion sans stationnaire. Pinewoods utilise un site extérieur hors Boulder Hill pour joueurs, IA et réapparitions Manta ; aucun repli au garage. Voir le handoff racine et les rapports Unreal pour l'état réel des tests, distinct de la validation Blender.
''',encoding='utf-8')
with (A/'REFERENCE_NOTES.md').open('a',encoding='utf-8') as f:f.write('''

## Source consolidée V23 —14 novembre

Les dernières corrections priment : habitacle raccourci puis ensemble arrière réduit de10%, avec essieu/arches et détails préservés ; contours des4 vitrages doublés, plats, continus. Pare-brise courbé55mm et trapézoïdal. Capot convexe partout, bande centrale à course195mm ; extrémité25mm devant les canons. Les3 projectiles et guides s'inclinent30°, base horizontale. Planche de feux fermée au niveau de la caisse, cache les jets ; supports rigides horizontaux puis verticaux, trajectoire gardée en arrière de la lunette. V23 corrige aussi les petits conflits de moulures de roues et de raccord capot par des points de rupture géométriques exacts.

Vues finales et rapports listés dans README ; sources indépendantes rouvertes. V1–V22 historiques uniquement. Le ratio initial40/30/30 est remplacé par les demandes ultérieures de raccourcissement ; pas un plan coté officiel. L'adaptation Unreal est autorisée : même dynamique fixe que Thunderhawk/Raven, faction VENOM et départ extérieur à la base MASK.
''')
# Record completed model evidence without marking subjective fidelity as exact.
f=A/'CORRECTIONS_UTILISATEUR.md';c=f.read_text(encoding='utf-8')
for line in c.splitlines():
 if line.startswith('- [ ]') and not any(s in line for s in ['Silhouette plus fidèle','40 % avant','Quatre états Vanessa','HANDOFF.md','Vérification sur maillages']):c=c.replace(line,line.replace('- [ ]','- [x]',1))
c+='''

État V23 : critères mécaniques cochés d'après les rendus et contrôles référencés dans README. Fidélité artistique encore soumise à appréciation ; détails du visage/coiffure/doigts perfectibles. Ratio initial remplacé par les dernières demandes de raccourcissement, pas revendiqué comme exact. Les quatre états ont déjà passé le contrôle de dépendances ; leur dernière revue visuelle est en cours. L'intégration Unreal est maintenant demandée, donc son absence n'est plus un état de livraison acceptable.
''';f.write_text(c,encoding='utf-8')
(P/'HANDOFF.md').write_text('''# Handoff — Manta / Pinewoods —14 novembre2026

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
''',encoding='utf-8')
