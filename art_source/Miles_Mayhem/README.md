# Miles Mayhem / Viper

Interprétation humaine réaliste autorisée expressément le13 novembre2026, désormais autorisation générale inscrite dans `../../AGENTS.md`. Sources : illustration et figurines fournies de Miles et Viper, pas de portrait photographique d'une personne réelle. Anatomie générique CC0 du projet, copiée indépendamment depuis Calhoun ; provenance dans `../AnatomyBase/README.md`. Les anciens personnages sont inchangés.

Un seul `MilesMayhem_Rig`, une seule tête anatomique et un seul vêtement pondéré servent pour les deux poses, avec visage conservé sous Viper. `driving_pose`0/1, `mask_on`faux/vrai, `in_vehicle`0 pour les sources autonomes. Le masque possède un casque/mentonnière, une visière ambre et une collerette suivant le torse ; la zone souple de cou est une interprétation. Les poids du casque et de la collerette sont conservés lors de l'export.

Dans l'assemblage `../Switchblade/Switchblade_V15_Assembly.blend`, Miles est installé dans le cockpit bas corrigé. Le cockpit orange reprend les détails visibles du jouet ; commandes, dégagements et dimensions sont interprétés. Les meshes, matériaux, armature et drivers restent éditables.

La réouverture réelle des sources indépendantes et l'identité tête/corps dans les quatre états sont consignées dans `../Switchblade/standalone_validation.json` (trois sources passent). Le socket du masque enregistre `rest_bind_origin` : restaurer cette origine et les modificateurs d'armature vers Miles pour réassembler ; une simple parenté tête ne reproduit pas le suivi de la collerette par le torse.

Limites : première interprétation, visage/cheveux/vêtements à raffiner par comparaison. Une tête anatomique et un rig ne prouvent pas à eux seuls une fidélité artistique définitive. Contrôler les rendus actuels des quatre états, le cou de profil, les mains/commandes, pieds/palonnier et siège. Pas de retopologie/UV finales ni d'export Unreal revendiqués.

Sources courantes : MilesMayhem_V2.blend et Viper_V2.blend. V1 conservées. Réouvertures réelles réussies, aucune dépendance manquante ; même tête et même corps dans les quatre états. Collerette ajustée par projection sur le vêtement évalué, poids normalisés du cou et des épaules ; aucun ancien Surface Deform conservé. Vues autonomes réellement rendues sous ../Switchblade/renders/independent_final ; poses et gros plans sous ../Switchblade/renders/v13_assembly et v15_mask. La forme générale reste une première interprétation ; finesse du visage, jonctions de cheveux, col et doigts perfectibles.

