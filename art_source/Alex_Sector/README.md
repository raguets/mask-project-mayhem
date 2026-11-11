# Alex Sector V1

`AlexSector_V1.blend` : personnage indépendant avec armature, visage conservé et masque séparé. `AlexSector_Mask_V1.blend` : masque autonome avec repère et groupes de poids. Assemblage dans `../Rhino/Rhino_V2.blend`.

Sur `AlexSector_Rig` : `driving_pose` vaut 0 debout ou 1 assis ; `mask_on` affiche/cache le masque sur la même tête. Source indépendante centrée à l’origine ; position assise dans Rhino : `(2, -0.6, 1.37)`.

Références examinées : figurine fournie (chemise bleu canard, gilet clair, pantalon brun, crâne chauve et barbe rousse), deux illustrations (portrait et masque à visière bleue avec base évasée). Anatomie et volumes non montrés interprétés, sans ressemblance à une personne réelle. Base générique pondérée adaptée depuis Matt V5, avec données propres à Alex, tenue et casque distincts. Sources anatomiques CC0 et provenance conservées dans `../AnatomyBase/` et `../Matt_Trakker/anatomy_provenance_v4.json`.

Le masque autonome conserve `rest_bind_origin` sur `AlexSector_MaskSocket`. Rebrancher la coque sur `head` et les groupes poitrine/épaules de la base souple interprétée ; la version déjà attachée est dans le fichier personnage.

Vues inspectables : `renders/v1_final/`. Passes précédentes conservées. Rapports d’ensemble et de réouverture : `../Rhino/validation_v2.json`, `../Rhino/standalone_validation_v2.json`. Le visage, la barbe, les plis et certains contacts restent une première interprétation ; retopologie/UV de production et import Unreal non validés.
