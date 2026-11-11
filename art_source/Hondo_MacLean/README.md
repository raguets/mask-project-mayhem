# Hondo MacLean et masque

`HondoMacLean_V1.blend` contient un seul personnage articulé, sa tête et son masque amovible. Sélectionner `HondoMacLean_Rig` : `driving_pose` 0 debout / 1 assis, `gunner_pose` 0/1 pose de tir, `mask_on` faux/vrai. `in_vehicle` reste à 0 pour une utilisation indépendante. Aucun changement de corps ou de tête entre les états. Les liaisons vers Hurricane ont été retirées individuellement ; les drivers de pose et les poids restent éditables.

`HondoMask_V1.blend` contient uniquement le masque, son socket et le studio. `HondoMask_HeadSocket` conserve `rest_bind_origin`. Pour le remonter sur le rig correspondant, restaurer cette origine dans les sommets, conserver les groupes de poids et remettre un modificateur d'armature vers `HondoMacLean_Rig`. La coque et les cartouches suivent la tête ; la partie arrière possède ses poids propres. Ne pas remplacer le visage par un second personnage.

Tenue violette, protections jaunes, plastron bleu et masque turquoise/rouge issus des références Hurricane fournies. Anatomie et visage : interprétation humaine générique des images illustrées et de la figurine. Base anatomique CC0 du projet, provenance dans `../AnatomyBase/`. Aucun modèle d'une personne réelle. La finition reste stylisée, avec prise des doigts et déformations fines à approfondir ; asset de jeu final non validé.

Assemblage, rendus et rapports : `../Hurricane/README.md`. L'assemblage V7 conserve le même personnage contrôlé par le véhicule. Les versions sources précédentes restent dans le dossier Hurricane.
