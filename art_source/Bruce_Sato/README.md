# Bruce Sato V1

`BruceSato_V1.blend` : personnage indépendant avec armature, visage conservé et masque séparé. `BruceSato_Mask_V1.blend` : masque autonome avec repère et groupes de poids. Assemblage dans `../Rhino/Rhino_V2.blend`.

Sur `BruceSato_Rig` : `driving_pose` vaut 0 debout ou 1 assis ; `mask_on` affiche/cache le masque sur la même tête. Source indépendante centrée à l’origine ; position assise dans Rhino : `(2, 0.6, 1.37)`.

Références examinées : figurines, captures de dessin animé et illustration détaillée fournie. Cheveux courts noirs, uniforme beige, pièces et bottes orange, plastron sombre ; masque orange avec lunettes rondes, respirateur et deux flexibles. Les variations entre éditions et illustration de réinterprétation ne sont pas présentées comme une photographie officielle. Anatomie et parties cachées interprétées, sans ressemblance à une personne réelle. Base générique pondérée adaptée depuis Matt V5, avec données, proportions du visage, tenue et casque propres à Bruce. Provenance anatomique CC0 conservée dans `../AnatomyBase/` et `../Matt_Trakker/anatomy_provenance_v4.json`.

Le masque autonome conserve `rest_bind_origin` sur `BruceSato_MaskSocket`. Rebrancher la coque sur `head` et les groupes poitrine/épaules de la base souple interprétée ; la version déjà attachée est dans le fichier personnage.

Après changement de topologie du vêtement, les genouillères suivant sa surface ont été réassociées au repos pour supprimer l’ancien bind invalide. Vues : `renders/v1_final/`, anciennes passes conservées. Rapports : `../Rhino/validation_v2.json`, `../Rhino/standalone_validation_v2.json`. La finition du visage, de la coiffure et des vêtements reste à affiner ; retopologie/UV de production et import Unreal non validés.
