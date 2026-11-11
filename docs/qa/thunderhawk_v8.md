# Contrôles Thunderhawk V8 — 2026-11-01

## Résultat

**Étude extérieure articulée améliorée, IN_PROGRESS.** Dix images locales examinées ; plusieurs éditions de jouet visibles, aucune capture du dessin animé authentifiée. Le cockpit reste hors périmètre. Les formes de détail et la fidélité à la série ne sont pas déclarées finales.

La V8 corrige le panneau arrière (façade mobile de 25,5 cm au lieu de 55 cm), affine les feux fixes et ajoute le quadrillage violet de l'aileron. Les deux canons possèdent un support coulissant : ils se déploient de 18 cm vers l'extérieur des portes en fin d'ouverture et rentrent avant fermeture complète. Un guide télescopique assure leur liaison.

## Fichiers principaux

| Livrable | Chemin |
|---|---|
| Source Blender | `art_source/Thunderhawk/Thunderhawk_V8.blend` |
| Générateur complet | `art_source/Thunderhawk/scripts/build_thunderhawk_v8.py` |
| Références liées et intactes | `art_source/Thunderhawk/Images reference/` ; collection Blender `Reference_Study_UserImages` |
| Contrat / analyse | `docs/art/THK_asset_contract.md`, `docs/art/THK_reference_review_v7.md` |
| Orthographies et vues de contrôle | `art_source/Thunderhawk/renders/v8/{front,rear,side,top,perspective,flight,rear_road,rear_flight,front_flight,mid_open,mid_return}.png` |
| Vidéo transformation | `art_source/Thunderhawk/renders/v8/transformation.avi` (MJPEG, 97 images à 12 i/s) |
| Turntable | `art_source/Thunderhawk/renders/v8/turntable.avi` (MJPEG, 72 images à 12 i/s) |
| Export | `art_source/Thunderhawk/exports/THK_V8.fbx`, `THK_V8_assembly.json` |
| Projet neutre | `unreal/MASK_AssetLab/MASK_AssetLab.uproject` |
| Carte / séquence UE | `/Game/Maps/THK_V8_AssetTest`, `/Game/Thunderhawk_V8/THK_V8_RoundTrip` |
| Consigne pour prochains assets | `AGENTS.md` |

## Tests réellement effectués

1. **Blender 5.2.3 LTS** : génération, rendus, sauvegarde puis réouverture du `.blend` et évaluation des objets avec leurs modificateurs.
2. **Revue visuelle** : photos fournies et rendus route/vol, face/dessus/profil, vues arrière et poses intermédiaires ouverts. Les rendus ont conduit à corriger phares saillants, contact des portes, panneau arrière trop plein et surface de décoration cachée par l'épaisseur de l'aileron. Les photos n'ont pas été transformées en textures du modèle.
3. **Intersections** : `validate_v8.py` teste 19 couples de pièces à chacune des 193 images entières. Résultat final : zéro ligne avec intersection ; 3 667 évaluations de couples. Limites : couples sélectionnés, surfaces triangulées, pas de test continu entre images ni de détection garantie des volumes entièrement contenus.
4. **Retour complet** : comparaison des positions de tous les sommets évalués à 1 et 193 : erreur maximale **0 m**. Enveloppe route mesurée, accessoires compris : **4,799 × 2,043 × 1,295 m** ; dimensions de conception estimées, non officielles.
5. **Vidéo** : 97 JPEG de transformation et 72 JPEG de rotation conservés. AVI MJPEG construits par script sans dépendance FFMPEG ; tailles RIFF/index et marqueurs JPEG vérifiés. Images des poses 65, 97, 151 et 193 examinées ; fichier AVI non lu dans un lecteur multimédia externe. Première génération jugée trop sombre, seconde génération éclaircie et image 97 réinspectée.
6. **Unreal 5.8 installé** : import des 183 meshes, création/sauvegarde d'une carte et de 72 bindings animés. Le lecteur LevelSequence a été évalué aux cinq poses Blender 1, 65, 97, 151, 193 sur six objets (ailes, panneau, aileron, canons). **30 comparaisons PASS** ; erreur maximale de translation ~0,000007 cm, rotation/échelle sous les seuils. Cette vérification porte sur les transformations, pas le rendu.
7. **Géométrie importée** : bornes des 183 StaticMesh réellement chargés comparées aux sommets Blender au repos, conversion d'axes/unités incluse : **PASS**, erreur maximale ~0,000031 cm, seuil 0,1 cm. Ce contrôle n'approuve ni UV ni shading.

Preuves : `validation_v8.json`, `intersection_v8.csv`, `video_v8.json`, `unreal/MASK_AssetLab/import_v8_result.json`, `import_v8_geometry_check.json` et leurs journaux.

## Commandes exécutées

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b --python art_source/Thunderhawk/scripts/build_thunderhawk_v8.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b art_source/Thunderhawk/Thunderhawk_V8.blend --python art_source/Thunderhawk/scripts/validate_v8.py --python art_source/Thunderhawk/scripts/export_assembly_v8.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b art_source/Thunderhawk/Thunderhawk_V8.blend --python art_source/Thunderhawk/scripts/render_motion_v8.py
```

Les deux scripts Unreal `import_thunderhawk_v8.py` et `verify_import_v8.py` ont été exécutés séparément par `UnrealEditor-Cmd.exe` avec `-run=pythonscript`, `-unattended -nosplash -nullrhi -DDC-ForceMemoryCache -stdout -FullStdOutLogOutput`. Voir `import_v8.log` et `verify_v8.log` pour les lignes de commande et résultats. Le cache Zen local ne démarre pas ; le cache mémoire a permis les tests. Une erreur de vignette Blender apparaît au journal, mais la sauvegarde et sa réouverture sont vérifiées.

## Contrôles restant à faire

Revue visuelle du viewer Unreal, comparaison à des captures du dessin animé et mesures plus précises de l'édition cible. Le rig UE de production (SkeletalMesh/AnimationSequence), les sockets, UV/PBR définitifs, collisions physiques, LOD, budgets et performance ne sont pas validés. Le test animé UE utilise des pièces rigides et des pistes Sequencer échantillonnées, indépendantes de VehicularCombat.
