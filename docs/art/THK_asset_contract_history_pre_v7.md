# Thunderhawk — contrat d'asset V0 (provisoire)

Statut : IN_PROGRESS. Indépendant de VehicularCombat. Ce contrat est une hypothèse de travail, non une validation artistique ou d'import.

## Repère et dimensions
Blender : mètres, +X avant, +Z haut ; gauche du véhicule = +Y. Origine au sol, au centre longitudinal. Unreal : centimètres, +X avant, +Z haut ; conversion et parité à vérifier par import. Caisse estimée 4,67 m × 1,86 m, hauteur de toit 1,34 m, empattement 2,82 m, roues diamètre 0,66 m. Mesures inventées pour la maquette, pas des dimensions officielles. Ajouter des repères d'axes et mesurer dans Unreal avant de figer l'orientation FBX.

## Hiérarchie et mécanique
`THK_Root`, `THK_Body`, quatre `THK_Wheel_FL/FR/RL/RR`, `THK_Wing_Hinge_L/R` et enfants `THK_Wing_L/R` et `THK_DoorGlass_L/R`. Pivots des ailes au bord du toit, axe longitudinal X ; ouverture symétrique à 75°, hypothèse à revoir. `THK_RearStabilizer` est séparé mais fixe. Roues séparées, aucune suspension ni rotation configurée. Le vitrage est une enveloppe opaque, sans cockpit.

Timeline 24 i/s : 1–25 route ; 25–97 ouverture ; 97–121 vol ; 121–193 fermeture. Les marqueurs nomment les séquences : ils ne sont pas des actions Blender distinctes. Animation Bézier par défaut ; interruption, collisions, mécanisme du stabilisateur et réacteurs non définis. La réversibilité des clés ne prouve pas l'absence d'intersections. Pivots et raccords de portes à reprendre avant validation.

Emplacements provisoires `SOCKET_DriverSeat`, `SOCKET_Muzzle_L/R`, `SOCKET_CameraCockpit`, `SOCKET_Exhaust`, `SOCKET_VFX_Transform` sous forme d'empties, non validés dans UE. `L/R` se rapportent au véhicule, vu vers l'avant.

## Export et qualité
`THK_V0.fbx` est un essai d'objets/empties avec animation cuite ; ce n'est pas un squelette validé. Essayer d'abord l'import de meshes séparés, puis choisir rig squelettique ou hiérarchie d'acteurs après test des pivots et du mouvement dans UE. Ne pas supposer que l'animation d'objets FBX devient une animation Unreal. Appliquer les conventions seulement après test d'échelle, axes, pivots, sockets et allers-retours. UV, textures PBR, collisions, LOD, rig de production et physics asset restent à faire.

## Références et décisions
Voir `reference_manifest.csv`. CarsGuide décrit une Camaro rouge dont les portes servent d'ailes ; MASKFORCE décrit aussi stabilisateur et deux réacteurs, mais sa fiche est orientée jouet. Aucune planche orthographique fiable ni analyse image par image d'un épisode n'a été obtenue. Les différences dessin animé/jouet et les couleurs exactes restent À TESTER. Aucun fichier tiers n'est inclus. Les noms et designs M.A.S.K. exigent une validation des droits avant diffusion.

## Revue visuelle
Rendus route front/rear/side/top et perspective, plus vol, produits et inspectés ; la dernière correction du vitrage a été inspectée en perspective. Le rouge et l'idée des portes-ailes sont présents. La carrosserie est trop anguleuse, les fenêtres de portes restent géométriquement approximatives, le nez et les passages de roue sont approximatifs, ailes trop courtes et mécanisme arrière incomplet. Comparaison fondée sur descriptions et aperçu indexé, pas sur un relevé visuel multi-vues d'épisode ; fidélité non validée. Le rendu blanc initial a été corrigé en reconstruisant explicitement le graphe des matériaux. Aucune inspection continue de l'animation ni 360° n'a été faite.


## Itération V1 — contrôle du 1er novembre 2026

`Thunderhawk_V1.blend` et `scripts/build_thunderhawk_v1.py` préservent la V0. La carrosserie utilise des échancrures de roue polygonales et un évidement sous les portes. La découpe des roues traverse toute la largeur sous la carrosserie : ce n'est pas une géométrie de production. Le stabilisateur se translate de 0,94 à 1,16 m, avec supports télescopiques hypothétiques ; mouvement synchronisé avec les ailes, mais non tiré d'un relevé de l'animé. Les portes demeurent trop rectangulaires et courtes. En vol, l'évidement latéral est très visible ; raccords et profil doivent être reconstruits.

Contrôle BVH : `scripts/check_intersections_v1.py`, `intersection_v1.csv` ; à chaque image entière 1–193, chaque aile contre caisse et toit. Première géométrie : 76 images avec intersections par aile ; après évidement, aucune paire de triangles intersectée pour ces objets. Cela ne teste ni contacts tangentiels, ni mouvement entre images, ni autres pièces, ni dégagements minimaux ; pas une validation de toutes les collisions.

Import V1 : `unreal/MASK_AssetLab/import_thunderhawk_v1.py` et `import_v1.log`. 27 assets statiques/matériaux enregistrés. Dimensions de `THK_Body` : X -235 à 232 cm, Y -93 à 93 cm, Z 30 à 90 cm. Le +Y Blender devient -Y Unreal pour les ailes gauches, conforme à la convention des côtés ; +X reste avant, +Z haut pour les bornes observées. Ces bornes sont des coordonnées locales du mesh importé autour de l'origine du véhicule et ne prouvent pas le bon placement des pivots d'articulation. Les empties, sockets et animation ne sont pas validés ; l'import effectué est statique. Le cache Zen était inaccessible et un cache mémoire a permis l'import.

La séquence `renders/v1/sequence/frame_*.png` comprend 97 images, frames 1–193 par pas de 2, à jouer à 12 images/s pour respecter 24 i/s d'origine. Les poses route, ouverture et vol ont été inspectées visuellement, sans lecture vidéo intégrale. Blender disponible ne propose pas l'encodeur FFMPEG et `ffmpeg` n'est pas sur le PATH ; aucune vidéo n'a été créée. La source [Panda Power](https://www.maskforce.com/panda-power-s1e27.html) signale deux occurrences de la transformation dans S1E27 : repère documentaire, épisode et séquence non visionnés. Le mouvement reste hypothétique jusqu'à observation directe.

## Itération V2 — ensemble arrière

À la demande du porteur, `THK_RearHatch_Hinge` pivote autour de Y à (-1,85, 0, 0,90) m ; `THK_RearHatch` porte le stabilisateur, ses supports et les feux. Deux réacteurs fixes `THK_Reactor_L/R` et deux tuyères `THK_ReactorNozzle_L/R` sont placés dans la baie arrière. De 33 à 85, le capot s'ouvre de 0 à 60 degrés ; il reste ouvert jusqu'à 121 et revient à zéro à 173. Le mouvement est synchronisé aux portes mais constitue une interprétation mécanique, pas un relevé de l'animation 1985. V0 et V1 conservées.

VÉRIFIÉ : inspection des rendus `rear_road`, `rear_mid`, `rear_flight`, `rear_return` ; capot fermé, ouverture, réacteurs visibles et fermeture lisibles. Les cylindres et raccords restent volontairement grossiers ; les ailes sont trop courtes et la silhouette générale n'est pas approuvée. L'examen n'est pas une comparaison frame-by-frame à l'épisode.

VÉRIFIÉ : `scripts/check_intersections_v2.py` teste chaque frame entière 1–193 ; chaque aile contre caisse et toit, capot contre caisse et chacun des deux réacteurs. La première construction avait des collisions ; après retrait du fond de coque et déplacement de charnière, aucune intersection triangulaire pour ces sept couples aux frames testées (`intersection_v2.csv`). Les autres objets, les contacts tangents, les épaisseurs et les positions entre frames ne sont pas couverts.

VÉRIFIÉ : import statique Unreal V2, 32 fichiers `.uasset`, capot et réacteurs séparés (`unreal/MASK_AssetLab/import_v2.log`). L'échelle de caisse demeure 467 × 186 cm. Animation, hiérarchie et pivots ne sont pas validés dans Unreal ; l'export ne constitue pas encore un rig animé prêt à intégrer.

## Itération V3 — correction des mécanismes
La V3 remplace le pivot arrière de V2. `THK_RearPanel_Lift` n'a aucune rotation : translation +Z de 0,26 m entre frames 45 et 85, retour entre 121 et 161. `THK_RearStabilizer` est un objet indépendant parenté à `THK_Root` : translation +Z 0,34 m entre frames 25 et 55 puis retour entre 165 et 193. À la frame 45, l'aileron est en cours de montée et le panneau reste fermé ; à 161, le panneau est fermé tandis que l'aileron reste haut. Des supports séparés se déploient avec l'aileron.

Les charnières des deux portes sont déplacées à Y ±0,25 m au voisinage du milieu du toit, et la section supérieure des portes rejoint cette zone. Les ailes tournent de ±63° autour de X depuis leur position routière oblique, donnant une extrémité inclinée en vol. La découpe des panneaux et les vitrages restent des formes provisoires ; l'ouverture laisse des volumes et raccords grossiers. Absence de cockpit, comme demandé.

VÉRIFIÉ : `check_intersections_v3.py` balaie les 193 images entières, dix couples (ailes/caisse, ailes/toit, panneau/caisse, panneau/réacteurs, panneau/aileron et panneau/supports). Des intersections portes/toit sont apparues durant l'itération ; modification du contour puis zéro intersection triangulaire sur les couples testés. Cela n'exclut pas des contacts tangents, d'autres pièces ou des intersections entre frames. `intersection_v3.log` indique positions et rotation nulle du panneau ; `intersection_v3.csv` donne les mesures.

Les références et les limites d'accès aux images MASKFORCE sont listées dans `THK_references_complementaires.md`. Vues de contrôle générées en V3 ; fidélité à l'animé et cinématique UE animée restent non validées. La V2 est conservée.

## Itération V4 — porte coudée
La V3, dont la porte formait un panneau plat entre l'axe du toit et le flanc, est rejetée visuellement. Sur instruction du porteur, la V4 conserve une articulation proche du centre mais chaque porte est une seule pièce coudée : section supérieure presque horizontale, puis changement de plan vers la section latérale. Les deux sections conservent un angle entre elles et pivotent ensemble ; ce ne sont pas deux panneaux qui se replient. Les pivots des portes et les translations indépendantes du panneau arrière et de l'aileron sont conservés.

Les rendus d'essai `renders/v4/preview_road.png` et `preview_flight.png` ont été inspectés : le coude et le volume supérieur sont plus lisibles que sur V3, mais le profil général de Camaro, les raccords au pare-brise et les ouvertures latérales restent inexacts ; il ne s'agit pas d'une validation esthétique. Contrôle BVH `intersection_v4.csv` : aucune paire de triangles pour les dix couples et les 193 images entières testées ; les autres couples et les positions entre images demeurent non vérifiés.

La fiche [Transformerland](https://www.transformerland.com/wiki/toy-info/mask-original-mask-series-series-1-vehicles-thunderhawk/38634/) décrit le bouton central du toit en T ; [MASKFORCE](https://maskforce.com/thunderhawk-mask/) propose les vues du jouet. Les pages textuelles ont été consultées, mais l'accès aux images et au navigateur intégré a échoué : la comparaison directe à leurs photographies reste à faire et ne doit pas être déclarée accomplie.

L'import statique Unreal V4 a créé 32 assets ; la caisse mesure 467 × 186 cm selon `import_v4.log`. Les pivots et l'animation ne sont pas validés par cet essai.

## Itération V5 — largeur du vitrage
La V5 conserve les portes coudées et les mécanismes indépendants de V4, mais élargit les extrémités du vitrage avant et arrière pour éviter la face triangulaire observée sur les rendus V4. `preview_road.png` a été inspecté : le pare-brise est plus large, mais il subsiste des jours aux raccords et la carrosserie reste trop rudimentaire. Cette amélioration n'est pas une validation de fidélité.

Le contrôle `intersection_v5.csv` évalue les mêmes dix couples à chaque frame entière 1–193 et ne relève aucune intersection triangulaire. Il n'établit pas l'absence d'intersections entre frames ou avec les autres pièces. L'angle de porte, les proportions et la finition doivent être comparés à des images effectivement accessibles avant toute validation artistique.

## Itération V6 — canons et lacunes visuelles
Deux objets séparés `THK_DoorCannon_L/R`, parents des charnières d'aile, sont placés au bas des portes. Ils se déplacent de 0,18 m selon X local entre les frames 60 et 97 puis rentrent entre 121 et 158. Leur géométrie cylindrique, leurs dimensions et leur trajectoire sont provisoires ; les rendus `preview_road` et `preview_flight` ont été inspectés. Le [catalogue Kenner 1986](https://wheeljackslab.com/files/uploads/59Kenner-1986-Toy-Fair-Employee-Dealer-Vendor-Rep-Catalog-Mask-0c046d1b-2136-449a-9fb1-ff55a3f4d224.pdf) confirme la présence de canons d'aile rétractables, mais la forme de cette V6 n'a pas été vérifiée sur une image.

Le balayage `intersection_v6.csv` teste douze couples à chaque image entière (dont canons/caisse) : aucune intersection triangulaire enregistrée. Les couples non listés, contacts tangentiels et positions entre images ne sont pas couverts.

Lacunes signalées : forme réelle des réacteurs et de leur logement non reproduite, silhouettes et raccords de Camaro insuffisants, pièces de porte et armes rudimentaires, jantes, pare-chocs, éclairages et détails extérieurs approximatifs, ailes extensibles éventuelles non étudiées. Décorations/couleurs précises et différence animé/jouet non établies. Cockpit volontairement hors périmètre de cette étape. Aucune de ces lacunes ne doit être qualifiée de validée sur la seule base des rendus du prototype.

L'import statique Unreal V6 a créé 34 assets, y compris les deux canons (`import_v6.log`). Cet essai ne valide ni l'animation ni les pivots.
