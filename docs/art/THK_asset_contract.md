# Thunderhawk — contrat Blender / Unreal V9

État : **SURFACING_REVIEW**, extérieur articulé, pas un asset Hero/AAA final. Source active : `art_source/Thunderhawk/Thunderhawk_V9.blend`. Contrat V8 conservé dans `THK_asset_contract_v8.md`. Aucun lien avec VehicularCombat.

## Références et échelle

Les douze photos fournies ont été examinées : dix images de jouets de plusieurs éditions et deux Camaro réelles. La fidélité au dessin animé reste **NON VALIDÉE** faute de captures identifiées exploitables. Les photos ne sont pas des plans orthographiques calibrés et ne sont pas employées comme textures du jeu.

Repère Blender : mètres, avant +X, haut +Z, gauche +Y. Conversion du laboratoire Unreal : `(X,Y,Z)m -> (100X,-100Y,100Z)cm`.

Empattement de référence réel : **2,5654 m**, soit 101 pouces, suivant le kit Camaro 1985 hébergé par GM : https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1985-Chevrolet-Camaro.pdf . Ce repère réel ne certifie pas une cote de Thunderhawk dans la série. Une calibration longitudinale monotone conserve les roues et passages de roues circulaires. Voir `dimensions_calibration_v9.json`.

Enveloppe mesurée avec accessoires : environ **4,857 × 2,004 × 1,309 m**. Les autres cotes restent estimées. Racine `THK_Root` au repère véhicule. Pas de cockpit : seuls plancher de masquage, cloisons extérieures et passages de roues sont présents.

## Surfaces et pièces

Carrosserie reconstruite en surfaces quadrangulaires distinctes, avec courbures de capot, épaules d'ailes et côtés. Subdivision et épaisseur restent modifiables. Le capot compte 144 quads de contrôle ; chaque coque de porte 184 quads avec une véritable ouverture de vitre. Les n-gones restants concernent surtout des embouts de primitives et pièces planes ; ils ne constituent pas une cage de subdivision générale.

- `THK_Wing_Hinge_L/R` : portes/ailes coudées, rotation autour de X, pivots proches du centre du toit à Y ±0,127 m et Z 1,300 m.
- `THK_DoorShell_L/R`, `THK_DoorAFrame_L/R`, vitrages, retours et accessoires : pièces séparées qui suivent les charnières.
- `THK_CannonDeploy_L/R` : déploiement des canons selon -Z local ; glissières et guides télescopiques séparés. Suffixes `_Front` / `_Rear`, sans points décimaux dans les noms.
- `THK_RearPanel_Lift` : translation verticale seule du pare-chocs/panneau arrière. Bandeau de feux supérieur fixe.
- `THK_Spoiler_Lift` : aileron cambré à commande indépendante, support télescopique central.
- `THK_Reactor_L/R` : bouches oblongues avec lèvre, gorge convergente, fond en retrait et ailettes.
- `THK_WheelPivot_FL/FR/RL/RR` : roues et jantes distinctes, cinq ouvertures réellement percées ; pas de suspension simulée.
- `SOCKET_Muzzle_L/R` : repères enfants des commandes de canons ; `SOCKET_Reactor_L/R` fixes. Leur création comme sockets UE n'est pas encore implémentée.

## Animation

24 i/s, frames 1–193. Ce sont des animations d'objets articulés ; aucun rig squelettique de production n'est livré.

| Commande | Aller | Maintien | Retour |
|---|---|---|---|
| Portes | 25–97, 0 à ±79° | 97–121 | 121–193 |
| Panneau arrière | 45–85, +0,215 m Z | 85–121 | 121–161 |
| Aileron | 25–55, +0,175 m Z | 55–165 | 165–193 |
| Canons et guides | 65–97, course 0,18 m | 97–121 | 121–151 |

Courses et timings sont des choix du prototype, pas une mesure d'une séquence originale du dessin animé.

## Exports et laboratoire Unreal

- `exports/THK_V9_Articulated.fbx` : hiérarchie et animation d'objets échantillonnée, simplification des clés désactivée. La réimportation de contrôle dans Blender exige `anim_offset=0` pour conserver les numéros d'images ; le décalage par défaut ajoutait une image.
- `exports/THK_V9.fbx` : maillages évalués au repos, cuits à l'origine véhicule pour le laboratoire.
- `exports/THK_V9_assembly.json` : deltas mondiaux et bornes au repos, convertis en centimètres et axes UE, 193 échantillons.
- UE : `/Game/Maps/THK_V9_AssetTest`, séquence `/Game/Thunderhawk_V9/THK_V9_RoundTrip`, 244 acteurs de pièces, 54 bindings animés. Scripts `import_thunderhawk_v9.py` et `verify_import_v9.py` dans `unreal/MASK_AssetLab/`.

La séquence de pièces rigides est un test d'intégration, pas un SkeletalMesh gameplay. Les quadrillages procéduraux Blender ne sont pas automatiquement conservés par FBX ; leur baking et les UV/PBR définitifs restent à faire. Pas de promesse d'équivalence visuelle UE : le contrôle actuel est numérique.

## Validation et limites

Voir `docs/qa/thunderhawk_v9.md`, `validation_v9.json`, `geometry_audit_v9.json`, `articulated_fbx_roundtrip_v9.json`, ainsi que les rapports `import_v9_result.json` et `import_v9_geometry_check.json` du laboratoire.

Les tests de surface ne couvrent que 35 couples à 385 positions, tous les demi-frames de 1 à 193. Ils ne garantissent ni absence d'intersection de toutes les pièces ni collision volumique continue. Les frontières ouvertes des décorations surfaciques sont intentionnelles. Aucun test de conduite, physique, réseau, LOD ou budget GPU n'est revendiqué.

Les sources V8, la copie de son état ouvert et une copie V9 avant recalage dimensionnel sont conservées. La conformité finale au dessin animé, les mécanismes internes complets, la retopologie Gameplay et l'import squelettique restent à produire et valider.
