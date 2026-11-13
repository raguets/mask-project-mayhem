# Brad Turner et Hocus Pocus

Interprétation humaine réaliste explicitement autorisée le 12 novembre 2026 à partir des illustrations et figurines fournies, sans ressemblance avec une personne réelle. Anatomie CC0 générique du projet : voir `../AnatomyBase/README.md`. Copie indépendante de la base articulée Calhoun V2, sources antérieures inchangées ; tenue, accessoires, tête et masque adaptés à Brad.

`BradTurner_V2.blend` : un seul corps/tête et un rig éditable `BradTurner_Rig`. V1 conservée. `driving_pose` 0 debout / 1 moto, `mask_on` visibilité du masque. Pas de corps alternatif pour les poses. Masque noir/jaune séparé ; visage toujours conservé dessous.

`HocusPocus_V2.blend` : masque seul, sans dépendance au personnage ou à Condor. V1 conservée. Arrière allégé selon la garde au crâne, deux nervures noires verticales par côté. Socket `HocusPocus_HeadSocket`, propriété `rest_bind_origin` ; groupes de poids tête ET épaules conservés. Restaurer cette origine et relier les poids à la même armature pour remonter la collerette. Un seul maillage connecté, visière opaque frontale, bouche/menton fermés, grille vocale en relief et base évasée sur les épaules.

Assemblage : `../Condor/Condor_V20_Assembly.blend`. Rendus et vérifications : `../Condor/renders/v20_review`, `../Condor/standalone_validation_v20.json`. Export jeu sur le même squelette : `../../VehicularCombat/SourceArt/MASK/Condor`, locomotion `../../VehicularCombat/SourceArt/MASK/OnFoot/Brad`. Limites : anatomie/plis, cheveux/lunettes et prise des mains encore stylisés.





