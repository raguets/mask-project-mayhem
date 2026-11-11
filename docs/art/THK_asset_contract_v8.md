# Thunderhawk — contrat Blender / Unreal V8

Version active : `art_source/Thunderhawk/Thunderhawk_V8.blend`. État : **IN_PROGRESS**, étude extérieure articulée à partir des dix images fournies et examinées. Les anciennes itérations sont conservées ; le contrat antérieur se trouve dans `THK_asset_contract_history_pre_v7.md`. Aucun travail de VehicularCombat n'est requis par ce pipeline.

## Références et périmètre

Voir `THK_reference_review_v7.md` et `user_reference_manifest_v7.csv`. Les photos montrent plusieurs variantes de jouet ; `images (4).jpg` compare Ramen et Loyal Subjects, `images (6).jpg` porte TLS/Hasbro 2025. La conformité au dessin animé 1985 n'est pas validée par ces images. Les décorations sont une interprétation géométrique originale, sans appliquer les photos comme textures.

Extérieur, pièces mobiles et volumes noirs de masquage uniquement : aucun cockpit. Le modèle reste intermédiaire ; courbures du nez, raccords et détails internes des réacteurs à affiner. Pas de statut Hero ou AAA final.

## Échelle et repères

Blender : mètres, avant +X, haut +Z, gauche véhicule +Y. Unreal : centimètres, avant +X, haut +Z, gauche véhicule -Y. Conversion du spike : `(X,Y,Z)m -> (100X,-100Y,100Z)cm`.

Enveloppe routière mesurée dans `validation_v8.json` : **4,799 × 2,043 × 1,295 m**, accessoires compris. Empattement paramétré : 2,83 m ; rayon des pneus : 0,322 m. Ces dimensions sont des estimations à échelle réaliste, pas des mesures officielles du véhicule ou du jouet.

Origine `THK_Root` au sol à proximité du centre du véhicule. Les pièces et collections sont modifiables ; les photos sont liées dans la collection masquée `Reference_Study_UserImages`, exclue des rendus et exports.

## Hiérarchie fonctionnelle

- `THK_Root` : racine indépendante du moteur.
- `THK_Body`, `THK_Hood`, vitrages et cadres : maillages extérieurs distincts.
- `THK_Wing_Hinge_L/R` à Y ±0,125 m, Z 1,29 m : rotation autour de X. `THK_Wing_L/R` sont des coques coudées, avec feuille de toit, cadre de vitre et flanc presque vertical. Vitrages, décoration, rétroviseur et rail suivent la porte.
- `THK_CannonDeploy_L/R`, enfants des charnières : translation sur le rail de déploiement ; canon, bouche et support sont des pièces séparées. `THK_CannonTelescopicGuide_L/R` assure la liaison avec la porte.
- `THK_RearPanel_Lift` : translation verticale seule du bandeau/pare-chocs arrière mobile, hauteur de la façade 0,255 m. La bande supérieure et les feux fins sont fixes ; le bandeau mobile passe devant eux pendant sa montée, selon l'interprétation du jouet.
- `THK_Spoiler_Lift` : aileron sur support central, commande indépendante du panneau arrière. Surface violette quadrillée, géométrie originale.
- `THK_Reactor_L/R` : contours oblongs arrondis fixes, cavités et éléments internes simples ; la profondeur exacte reste hypothétique.
- `THK_Wheel_FL/FR/RL/RR`, jantes et moyeux : pièces séparées, sans suspension fonctionnelle.

## Animation

Timeline 1–193, 24 i/s ; marqueurs `THK_RoadIdle`, `THK_RoadToFlight`, `THK_FlightIdle`, `THK_FlightToRoad`. Les marqueurs ne sont pas quatre actions squelettiques indépendantes.

| Pièce | Aller | État vol | Retour |
|---|---|---|---|
| Portes/ailes | frames 25–97, rotation symétrique 0 -> ±79° | 97–121 | 121–193 -> 0° |
| Aileron | 25–55, +0,215 m Z | 55–165 | 165–193 |
| Panneau arrière | 45–85, +0,235 m Z, rotation nulle | 85–121 | 121–161 |
| Canons | 65–97, course 0,18 m selon -Z du repère de porte | 97–121 | 121–151 |

La rotation de la porte convertit la course du rail en un déplacement vers l'extérieur de l'aile. Les canons sont rentrés avant fermeture complète. Supports et bouches restent solidaires. Ordre et courses sont choisis pour le prototype ; aucune analyse d'une séquence animée authentifiée n'a été effectuée. Interruption, conduite, physique et réplication ne sont pas implémentées.

## Export et test d'import neutre

`THK_V8.fbx` conserve meshes/empties et animation d'objets cuite. L'import de meshes statiques n'importe pas à lui seul l'animation. Pour le spike indépendant, `export_assembly_v8.py` écrit `THK_V8_assembly.json` : maillages cuits dans le repère véhicule et deltas de transformation échantillonnés aux 193 images, convertis en axes/unités UE.

`unreal/MASK_AssetLab/import_thunderhawk_v8.py` importe les meshes sous `/Game/Thunderhawk_V8`, crée `/Game/Maps/THK_V8_AssetTest` et la séquence `/Game/Thunderhawk_V8/THK_V8_RoundTrip`. La scène contient 183 acteurs de pièces et 72 bindings animés. Ouvrir la carte puis la séquence pour inspecter la transformation. Les étapes `SequencerScripting` s'appuient sur la documentation officielle Epic : https://dev.epicgames.com/documentation/unreal-engine/python-scripting-in-sequencer-in-unreal-engine

Ce test conserve le mouvement via une séquence de pièces rigides. Il ne constitue pas encore un SkeletalMesh/AnimationSequence de production, un PhysicsAsset ou un rig gameplay validé. Les pivots fonctionnels restent explicites dans Blender ; le spike UE utilise des coordonnées de meshes cuites à l'origine véhicule. Les empties `SOCKET_*` sont des repères source ; leur conversion en sockets Unreal reste à réaliser.

## Contrôles exécutés et limites

- Réouverture du .blend et évaluation des objets modifiés.
- `validate_v8.py` : 193 images entières, 19 couples sélectionnés, zéro intersection triangulaire détectée ; erreur maximale des positions de sommets entre frames 1 et 193 : 0 m. Ne couvre pas tous les couples, l'intérieur des volumes ou les positions entre deux images.
- Quatre vues orthographiques, perspective, route/vol arrière, face vol et poses intermédiaires rendues puis inspectées. L'aileron décoré et les canons déployés ont été vérifiés dans les rendus.
- Vidéos MJPEG AVI : transformation (97 JPEG à 12 i/s, pas de deux sur la timeline Blender) et turntable (72 JPEG à 12 i/s). Les images sources sont conservées. Structure RIFF/index et marqueurs JPEG contrôlés par le script ; lecture dans un lecteur multimédia externe non effectuée.
- Unreal : import, carte et LevelSequence créés et sauvegardés ; lecture évaluée numériquement sur six objets à cinq poses (30 mesures), comparaison aux échantillons Blender : PASS. Erreur maximale mesurée de translation ~0,000007 cm, rotation et échelle sous les seuils du test. Ce contrôle ne prouve pas la qualité du shading ni l'équivalence visuelle.
- Vérification des bornes réelles des meshes importés : rapport `import_v8_geometry_check.json` lorsqu'il est présent ; ne pas présumer son résultat avant lecture.

Les budgets, UV/PBR définitifs, textures, LOD, collisions physiques, cockpit, rig squelettique final et performance restent à faire. La scène UE n'a pas encore fait l'objet d'une revue visuelle. Le cache Zen local ne démarrait pas ; `-DDC-ForceMemoryCache` a permis les commandes. L'erreur de vignette Blender n'a pas empêché la sauvegarde, vérifiée par réouverture.

La vérification des bornes a été exécutée : `import_v8_geometry_check.json` = PASS sur 183 meshes, erreur maximale 0,00003052 cm (seuil 0,1 cm). Rapport complet : `docs/qa/thunderhawk_v8.md`.
