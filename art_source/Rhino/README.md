# Rhino V3 — Alex Sector et Bruce Sato

Assemblage éditable : `Rhino_V3.blend`. V1, V2 et passes intermédiaires conservées. La scène précédente Thunderhawk est conservée séparément ; elle n’a pas été remplacée par Rhino.

V3 reprend le pare-buffle depuis la nouvelle photo `rhino pare buffle.jpg` : contour fermé et barreaux verticaux, largeur/hauteur alignées sur la calandre, sans montants dépassant vers le haut. L’avance de 0,80 m et sa commande sont conservées. Compte rendu : `../../docs/progress/2026-11-03-Rhino-V3-pare-buffle.md`.

V2 reprend les corrections utilisateur : capot abaissé pour dégager le pare-brise, fenêtres hautes abaissées et évasées en plan, petit radar tournant sur le toit, grand coffre coulissant vers l’arrière avant la montée d’un missile noir unique. Courses et angles restent estimés depuis les images et les consignes ; ils ne sont pas des cotes officielles.

## Commandes

Sélectionner `Rhino_Control`. La timeline 1–241 montre route, transformation, maintien, retour. Image 1 : route ; image 151 : transformé. La propriété `battle_mode` pilote la séquence complète entre 0 et 1. Comme elle est animée, changer de frame reprend la valeur de la timeline.

Commandes partielles : `bullbar` (pare-buffle avancé), `cannons` (échappements rabattus vers l’avant), `rear_detach` (séparation du module), `rear_open` (ouverture arrière du cockpit), `cabinet_slide` (recul de 0,80 m du grand coffre), `launcher_up` (déploiement conditionné par l’ouverture ET le recul du coffre). `radar_spin` active sa rotation indépendante. La séquence principale sépare le module avant l’abaissement de la rampe et rétracte le lanceur avant fermeture. Les combinaisons manuelles arbitraires des commandes partielles ne constituent pas une séquence validée.

Les mêmes dix pneus sont conservés pendant le mouvement : deux avant, quatre au jumelage central, quatre arrière. Après séparation, le camion conserve les deux avant et les deux roues centrales extérieures ; le module reçoit les deux centrales intérieures et les quatre arrière. Cette construction des roues et des liaisons cachées est estimée à partir des photos fournies et de la consigne utilisateur.

`AlexSector_Rig` et `BruceSato_Rig` possèdent chacun `driving_pose` (0 debout, 1 assis) et `mask_on` (masque caché/visible). Un seul corps, une seule tête et une seule armature par personne. Les deux personnages sont distincts, avec leurs propres données et matériaux. Dans l’assemblage, la position prévue pour l’assise est `(2, -0.6, 1.37)` pour Alex et `(2, 0.6, 1.37)` pour Bruce. Les sources personnages indépendantes sont centrées au repos.

## Sources indépendantes

- `Rhino_V3_Vehicle.blend` : camion et module, sans personnages.
- `Rhino_RearVehicle_V1.blend` : module autonome recentré, six pneus, sans dépendance au camion.
- `../Alex_Sector/AlexSector_V1.blend` et `AlexSector_Mask_V1.blend`.
- `../Bruce_Sato/BruceSato_V1.blend` et `BruceSato_Mask_V1.blend`.

Dans les masques indépendants, le socket conserve `rest_bind_origin`. Les groupes de poids sont gardés pour le remontage : la coque suit la tête, la base interprétée utilise aussi des poids poitrine/épaules. La version déjà montée est incluse dans chaque source personnage.

## Références, contrôles et limites

Lecture des images réellement inspectées : `../../docs/art/Rhino_reference_review_v1.md`. Jouets, autre édition promotionnelle, photos réelles de W900B et illustrations des personnages restent distingués. Dimensions, anatomie humaine, finitions de cabine et liaisons cachées sont interprétées ; aucune ressemblance à une personne réelle n’est revendiquée.

Rendus V3 : `renders/v3/`. Rendus V2 conservés : `renders/v2_final/`. Personnages : `../Alex_Sector/renders/v1_final/`, `../Bruce_Sato/renders/v1_final/`. Les vues d’inspection de cabine cachent des panneaux, conformément au manifeste ; les vues générales montrent l’assemblage. Les passes précédentes sont conservées.

Contrôles V3 du pare-buffle : `bullbar_validation_v3.json`, `standalone_vehicle_validation_v3.json`. Les autres mécanismes et personnages conservent les rapports de référence `validation_v2.json` et `standalone_validation_v2.json`. Lire le périmètre réel, pas seulement les marqueurs de fin. Les contrôles discrets de triangles ne garantissent ni les volumes contenus ni le mouvement continu. La finition du visage, de la barbe, de la coiffure, du tissu et de certains contacts reste celle d’une première interprétation ; retopologie, UV de production et intégration Unreal ne sont pas validées.

Modélisation, inspection et sauvegardes réalisées par la connexion MCP Blender installée. Les scripts de `scripts/` ont des préconditions : ne pas relancer la construction initiale sur l’asset affiné. Les outils communs paramétrables restent dans `../shared_tools/` et la compétence projet.
