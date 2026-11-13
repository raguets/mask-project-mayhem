# Condor — sources Blender MCP

Références : `../../Images de reference/Condor et Brad Turner/`. Fiche transformation lue avant les onze images, toutes ouvertes. Photos du jouet ancien prioritaires pour les mécanismes ; réédition Loyal Subjects et dessins animés conservés comme catégories distinctes. Aucune dimension officielle : échelle adulte et pivots cachés estimés.

Assemblage courant : `Condor_V20_Assembly.blend`. Itérations V1–V19 conservées. Sources indépendantes : `Condor_V20_Vehicle.blend`, `../Brad_Turner/BradTurner_V2.blend`, `../Brad_Turner/HocusPocus_V2.blend`. Voir `standalone_validation_v20.json` pour les trois réouvertures et `clearance_v20.json` pour les contrôles roue/support/carénage sur61phases. Rendus courants : `renders/v20_review`,11vues inspectées.

## Commandes

- `Condor_Control` : animation `transform`, frames1–121. La roue arrière attend transform0,36 (support relevé45°) avant sa bascule ; pales après redressement du mât. Cette correction utilisateur remplace le départ simultané de la roue. Roue et deux bras plats internes désormais liés au vrai moyeu.
- `rotor_angle` : angle en radians, rotor principal et roue/rotor arrière ; pas de roue dupliquée. Patins courts fixes sous le bloc siège, aucune ouverture latérale indépendante. Masque postérieur allégé et deux nervures/tiges noires verticales par côté.
- `forward_flight` : 0, attitude horizontale de stationnaire ; 1, nez abaissé d'environ 6°. `hover_height` : hauteur de présentation en mètres. Ces contrôles d'asset ne constituent pas une dynamique de jeu.
- `BradTurner_Rig` : `driving_pose` 0/1, `mask_on` faux/vrai, `in_vehicle` 0/1. Même corps, tête et armature pondérés ; visage conservé sous le masque.

Catégories demandées : Rhino/Hurricane route / route ; Thunderhawk/Raven route / avion sans stationnaire ; Condor route / hélicoptère avec stationnaire au freinage maximal. Aucun code Unreal modifié dans ce lot.

## Corrections utilisateur intégrées

Bloc arrière monobloc, flancs plans chanfreinés, partie basse descendant en diagonale vers le siège, arrière aminci. Pales rangées contre ce bloc le long des montants pivotants. Nez plus effilé à faces saillantes ; une ouverture carrée sans phares, canon télescopique. Pare-brise à facette centrale et deux retours angulaires descendant jusqu'au carénage vert. Roue arrière avancée au repos ; fourche reliée à un pivot fixe sur le bloc. Masque Hocus Pocus : visière noire opaque intégrée, coque bouche/menton fermée et rapprochée du visage.

## Limites

Dernières précisions : arrière raccourci de18% puis largeur diminuant progressivement vers le dos de la moto ; montants convergents avec moyeu et porte-pales centraux. Avant et pare-brise rétrécis de18%. Face du nez inclinée vers le haut. Selle/patins sous un seul bloc, course0,12m. Masque en un seul maillage connecté, visière de plongée uniquement frontale, raccords avant/côtés plus carrés, collerette sans pincement sous le casque, grille vocale triangulaire intégrée.

Première passe artistique éditable. Plis, peau, cheveux, lunettes, prise des doigts et détails du masque restent stylisés. Contrôles de triangles échantillonnés et borne verticale de rotor : pas de certification de tous les volumes, des jeux mécaniques ou des contacts souples. UV/retopologie finale, gréement de jeu et intégration Unreal non réalisés.





