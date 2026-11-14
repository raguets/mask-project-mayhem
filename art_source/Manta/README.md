# Manta / Vanessa Warfield / Whip

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
