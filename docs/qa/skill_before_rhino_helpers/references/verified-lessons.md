# Résultats et limites du projet d’origine

Cas : `mask-project-mayhem`, Thunderhawk, Matt Trakker et Spectrum. Les règles utilisateur du projet et les autorisations en session restent prioritaires.

## Ce qui a été effectivement éprouvé

- Sources véhicule/personnage/masque indépendantes, sauvegardes conservées, puis réouverture réelle dans Blender MCP.
- Un seul Matt avec `driving_pose` et `mask_on`, visage conservé et cheveux masqués sous Spectrum. Vérification des mêmes datablocks dans les quatre états.
- Géométrie coudée des portes, panneau arrière en translation verticale, aileron indépendant, deux canons nommés séparément. Réacteurs sortant après ouverture du panneau et rentrant avant sa descente : contraintes propres à Thunderhawk.
- Verre transmissif, légèrement teinté, reflets lisibles après réduction de la taille des éclairages de studio ; distinction entre Solide et aperçu des matériaux.
- Plage arrière occultant le coffre et plaque M.A.S.K. fixée entre les réacteurs ; support modifié pour libérer la course du panneau arrière.
- Reprise du cou par une surface continue raccordée, avec révision des poids et de la pose assise ; base de masque plus large, ajustée à la surface des épaules et à leurs poids.
- Files de rendus avec restauration d’état, marqueurs de fin/erreur, vue de profil et contrôle dans les deux poses avant livraison.
- Contrôles géométriques évalués sur les 193 images entières de la transformation de ce véhicule, distincts du timing.

## Mesures locales, pas recettes universelles

Dans la V14, la tête a été abaissée d’environ 35 mm au repos, avec ajustement de la pose assise. La base de collerette atteint environ 352 mm de largeur ; les dimensions sont estimées, non officielles. Les 128 échantillons du bord inférieur donnent environ 3,4 mm d’écart moyen au vêtement debout et 3,3 mm assis, sans échantillon à plus de 2 mm à l’intérieur du vêtement lors de ce contrôle.

Ces chiffres concernent Matt et son rig actuel. Ils ne sont pas des valeurs à copier sur une autre personne, un autre masque ou une autre cabine.

## Échecs à ne pas reproduire comme méthodes

- Juger une modélisation sur le succès d’un script ou d’un fichier enregistré.
- Compter les frames d’un mécanisme sans évaluer les collisions.
- Utiliser une face procédurale simplifiée et des composants sphériques en prétendant obtenir un humain réaliste.
- Corriger le cou par des clamps/échelles locales sans regarder le profil ni les poids des deux poses : cela a créé une bosse et une cassure à la nuque.
- Empiler des anneaux de casque flottants ; confondre une large base épousant les épaules avec un long manchon vertical.
- Réutiliser des vues anciennes affectées par une nouvelle géométrie.
- Exporter une scène avec la méthode qui a provoqué le crash observé, ou conserver des wrappers Python d’objets déjà supprimés pendant un export.

## Preuves à retrouver dans le projet

- `docs/progress/2026-11-02-V13.md` : contexte précédent, matériaux, ajouts arrière et incident d’export.
- `docs/progress/2026-11-03-V14.md` : cou, collerette et capitalisation.
- `art_source/Thunderhawk/validation_v14.json` : scope, quatre états, contacts et transformation.
- `art_source/Thunderhawk/renders/v14/manifest.json` : vues réellement rendues et vues conservées.
- `art_source/Thunderhawk/standalone_validation_v14.json` : réouverture des composants.
- `art_source/AnatomyBase/README.md` et `art_source/Matt_Trakker/anatomy_provenance_v4.json` : sources génériques CC0 et limites d’interprétation.

À l’issue de V14, les défauts restants de peau, coiffure, vêtements, doigts et contact avec le siège ne sont pas des acquis validés. Cette étape ne démontrait pas une topologie/UV de jeu finales, une intégration Unreal de ces versions, ni un camion ou un aéronef complet. L’extension Rhino ci-dessous constitue la première application camion ; les méthodes aéronefs restent à éprouver sur leurs propres références.

## Extension Rhino — première application camion

Voir `docs/art/Rhino_reference_review_v1.md`, `art_source/Rhino/README.md` et les rapports V1. Les clichés de jouets Rhino et les photos réelles W900B sont distingués. Une édition promotionnelle différente ne remplace pas silencieusement l’édition principale.

Le train central est séparé par propriété réelle des pneus : extérieurs sur le camion, intérieurs sur le véhicule détachable. Les mêmes dix pneus persistent pendant le mouvement. Ce choix mécanique estimé appartient à Rhino ; ne pas en faire une règle pour les camions suivants.

Les premiers contrôles évalués ont détecté des collisions que les rendus généraux ne montraient pas : gaines d’échappement contre portes, rampe contre roues et rails. Les corrections ont porté sur le dégagement latéral des pivots, la largeur de rampe et sa hauteur d’articulation. Consulter le rapport final pour le résultat exact ; un ordre de lancement valide ne prouve toujours pas la liberté géométrique de la rampe.

Autres pièges observés :

- Créer une expression de driver avant ses variables peut laisser un driver invalide. Définir ses variables d’abord, puis son expression et vérifier `is_valid`, plusieurs frames et la réouverture. La normalisation des nombres décimaux a été appliquée dans le helper ; elle n’établit pas à elle seule la cause de l’invalidation initiale.
- Un shader de peau attendant un attribut propre au visage rend des mains noires si l’attribut manque. Vérifier ses entrées sur l’objet réel ; un matériau compatible distinct évite cet héritage.
- Attribuer pantalon/chemise uniquement selon la hauteur colore aussi les avant-bras. Utiliser les groupes de membres et contrôler les deux poses.
- Extraire un gilet par sélection de faces sur tout le corps inclut les manches et donne des bords dentelés. Un panneau régulier ajusté au torse préserve mieux une ouverture nette.
- Déplacer un dôme vers le bas sans adapter ses rayons fait traverser le front. Vérifier l’enveloppe du crâne avec le vrai visage conservé, de face et de profil ; ajuster aussi la visière et le raccord facial.
- Les zones de barbe découpées durement dans la tête donnent une peinture dentelée et peuvent recouvrir le nez. Séparer les repères bouche/nez, adoucir la densité et inspecter en gros plan.
- Une bande ajoutée sur un genou ne remplace pas une continuité de vêtement. Rhino a utilisé une union de surface sur le même objet, puis retransféré et normalisé les poids depuis la surface de repos. Cela exige une nouvelle revue assise et ne prouve pas une topologie de jeu finale.

Après cette union, un ancien `Surface Deform` de genouillère a étiré l’accessoire à travers le buste. Refaire le bind au repos peut supprimer l’étirement, mais ne corrige pas forcément un bord visuellement déchiré : des protections formées lisses, attachées explicitement au tibia dans ce cas, ont remplacé ces anciennes pièces. Vérifier la forme dans la pose, pas seulement l’état `is_bound`.

La correction utilisateur V2 de Rhino ajoute le recul du grand coffre, la façade vitrée fixe et le lancement d’un projectile unique par l’ouverture agrandie ; le petit radar est indépendant. La première paire de missiles horizontaux n’est pas une méthode validée à reproduire. La séparation de ces pièces est décrite dans `docs/art/Rhino_reference_review_v1.md` et contrôlée dans `validation_v2.json`.

Les rendus multi-acteurs et l’export autonome d’un module avec transforms figés sont désormais paramétrables dans les helpers. La validation de chaque source indépendante reste requise. Les méthodes avion/hélicoptère restent préparées ; Rhino ne les valide pas.
