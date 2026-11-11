# Thunderhawk V9 — revue des surfaces et intégration

Date : 2026-11-01. **IN_PROGRESS pour l'asset final ; passe de reconstruction extérieure produite et contrôlée.** Aucun cockpit. Aucun changement VehicularCombat.

## Audit réel de la scène ouverte

La connexion locale de l'extension Blender MCP a été rétablie. `audit_geometry_readonly.py` a été exécuté via cette connexion sur la V8 ouverte, frame 161, avec changements non enregistrés. Empreintes avant/après identiques pendant l'audit. Copie de l'état ouvert : `Thunderhawk_V8_live_before_rebuild.blend`, sans écraser `Thunderhawk_V8.blend`. Preuves : `thunderhawk_v8_live_mcp_audit.json`, `live_v8_preservation.json` et réponses MCP brutes.

Le diagnostic précédent est confirmé : capot à une face, portes à trois faces, grandes surfaces planes, jantes avec disques noirs, 481 faces évaluées d'aire quasi nulle. Aucun argument d'éclairage ou de matériau n'a été utilisé pour approuver la géométrie.

## Reconstruction et références

Le générateur V9 a été exécuté dans Blender par l'extension MCP. Nouvelle source : `art_source/Thunderhawk/Thunderhawk_V9.blend`. Les rendus et tests utilisent ensuite des instances Blender séparées, sans sauvegarder les scènes de diagnostic sur la source.

Les deux photos Camaro fournies ont guidé le galbe des ailes, le capot couronné, les logements de phares, les montants et les groupes de feux arrière. Les photos de jouets montrent le coude des portes, le panneau arrière vertical, le support d'aileron et les sorties oblongues ; leurs éditions diffèrent. Aucun relevé photographique exact ni pourcentage d'erreur de silhouette n'est revendiqué.

Un repère dimensionnel complémentaire provient du kit Camaro 1985 hébergé par GM : empattement 101 pouces = 2,5654 m. Le document complet de 20 Mo n'a pas pu être ouvert par le lecteur web ; la valeur apparaît dans son texte indexé et concorde avec le kit 1983. Cette valeur calibre la base automobile, pas une dimension canonique du dessin animé. Source et méthode : `dimensions_calibration_v9.json`.

## Corrections issues du contrôle

Les premières images de travail sont conservées sous `renders/v9/review_pass1` à `review_pass4`. Elles ne constituent pas le résultat actuel.

- Fermeture des grandes ouvertures de raccord autour du pare-brise et du hayon ; montants avant solidaires des portes.
- Correction d'un raccord supérieur de nez qui provoquait des pointes après ajout d'épaisseur.
- Décorations conformées aux surfaces, au lieu de grands polygones traversant le capot.
- Guides de canons replacés dans le bon repère parent et animés en longueur.
- Contour du montant arrière adapté à la porte, puis dégagement des montants avant vérifié pendant l'ouverture.
- Normales rendues cohérentes par composante connectée, sans retournements de faces isolées.
- Rayons de biseau limités sur les pièces minces, notamment après recalage dimensionnel.
- Noms de douze pièces corrigés pour l'import UE ; import du laboratoire rendu relançable lorsqu'une carte existe déjà.

## Contrôles réellement exécutés

| Contrôle | Preuve / portée |
|---|---|
| Réouverture du `.blend` et audit de maillage | `geometry_audit_v9.json`, source, maillage évalué et modificateurs |
| Retour de transformation | `validation_v9.json`, erreur maximale de position des sommets évalués entre 1 et 193 : 0 m |
| Intersections sélectionnées | 35 couples × 385 positions, pas de 0,5 frame ; résultat final dans `validation_v9.json` et `intersection_v9.json` |
| Silhouette et volumes | Dix PNG : face, arrière, profil, dessus, perspectives route/vol et deux poses intermédiaires ; tous ouverts et examinés |
| Structure de surface | `control_cage.png` : véritables arêtes de contrôle, modificateurs désactivés uniquement dans une scène de diagnostic non sauvegardée |
| Vue de l'application | Capture du viewport par l'extension MCP, `mcp_viewport.png` |
| Vidéos | Animation aller-retour : 97 JPEG à 12 i/s ; turntable : 72 JPEG à 12 i/s. AVI MJPEG et images sources conservés. Structure RIFF/index vérifiée ; pas de lecture dans un lecteur multimédia externe |
| FBX articulé réel | Réimport dans une scène Blender vide : bornes de six pièces à cinq poses. `articulated_fbx_roundtrip_v9.json` ; premier essai décalé d'une frame, corrigé avec `anim_offset=0` et simplification d'export nulle |
| Unreal | Import de 244 meshes, carte et séquence créées ; 54 bindings animés ; évaluation numérique de 30 poses dans `import_v9_result.json` |
| Bornes des meshes UE | `import_v9_geometry_check.json`, comparaison réelle aux sommets Blender au repos ; seuil 0,1 cm |

Le nombre de pièces ou de triangles ne prouve pas une qualité professionnelle. Les JSON sont la référence pour les chiffres finaux. Les UV présents sont des coordonnées de surface de construction, pas un atlas de production.

## Reproduction

Dans Blender, exécuter `build_thunderhawk_v9.py` ; il appelle `calibrate_v9_dimensions.py`. Le script reconstruit la scène active : sauvegarder son travail avant lancement. Depuis une instance séparée :

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b art_source/Thunderhawk/Thunderhawk_V9.blend -P art_source/Thunderhawk/scripts/validate_thunderhawk_v9.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b art_source/Thunderhawk/Thunderhawk_V9.blend -P art_source/Thunderhawk/scripts/render_thunderhawk_v9.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b art_source/Thunderhawk/Thunderhawk_V9.blend -P art_source/Thunderhawk/scripts/export_thunderhawk_v9.py
```

Les scripts Unreal sont exécutés avec `-run=pythonscript`, `-nullrhi`, `-ddc=InstalledNoZenLocalFallback` et `-DDC-ForceMemoryCache`. Le cache Zen local ne démarrait pas. Aucun rendu Unreal n'a été approuvé.

## Limites

Fidélité exacte à la série de 1985 : **NON VALIDÉE**. Dimensions hors empattement de Camaro : estimations. Rig squelettique, physique, sockets UE, atlas UV, textures baked, LOD et optimisation Gameplay : **NON PRODUITS pour V9**. Cockpit hors périmètre. Modèle final Hero/AAA : **NON TERMINÉ**.

Le nettoyage des itérations 1–7 demandé précédemment reste non exécuté après le rejet de l'environnement signalé au porteur ; aucun ancien fichier n'a été supprimé dans cette passe.
