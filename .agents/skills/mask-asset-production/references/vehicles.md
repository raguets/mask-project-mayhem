# Véhicules : silhouette, assemblage et transformation

## Préparer la première passe

Constituer un registre léger : image, auteur de l’approbation, catégorie/édition, angle réellement inspecté, formes observées, zones non montrées. Choisir une référence principale cohérente ; conserver les variantes comme comparaisons distinctes. Une photo statique ne donne pas un pivot caché, une course ou un ordre de déploiement.

Fixer un repère et une échelle estimée/documentée. Identifier avant la carrosserie fine : enveloppe générale, empattement ou longueur pertinente, largeur, ligne de toit/canopée, surfaces portantes et découpes. Comparer face, arrière, profil, dessus et trois-quarts avec des focales raisonnablement proches des références. Un cadrage qui coupe le nez ou les extrémités ne valide pas la silhouette.

Écrire un petit graphe des mécanismes : pièce, parent, pivot/axe, état initial/final, prérequis, rétraction, zones réservées. Les panneaux rigides conservent leurs coudes réels ; une articulation ne remplace pas la forme d’une porte. Garder séparés les accessoires qui se déplacent indépendamment.

## Choisir les contrôles selon la famille

| Famille | Ce qu’il faut vérifier avant le détail | Contacts/enveloppes à tester |
|---|---|---|
| Voiture | Pavillon, montants, vitrage, roues, coffre, découpes et pivots effectivement observés | Pilote/toit/vitres, siège, volant, pédales ; portes et armements pendant tout le mouvement |
| Camion | Hauteur de cabine, marchepieds, nombre/placement des essieux, capot/cabine, articulation de remorque si elle existe dans les références | Accès et posture du conducteur, cabine basculante, roues/châssis, débattements des modules et de la remorque |
| Avion | Fuselage, envergure, empennage, canopée, train, charnières de repli réellement documentées | Ailes/empennage/fuselage, train et trappes, pilote/canopée et commandes ; positions intermédiaires de repli |
| Hélicoptère | Fuselage, mât/moyeu, rotor principal, rotor de queue, patins/train et mécanismes visibles | Enveloppe complète des pales sur 360°, queue/canopée/sol, repli des pales et modules ; pilote et commandes adaptées |

Pour un rotor, quelques frames éloignées ne couvrent pas forcément le balayage entre deux positions. Utiliser une enveloppe balayée ou un échantillonnage angulaire suffisamment fin, et le dire. N’inventer ni sens de rotation ni cinématique de moyeu à partir d’une vue ambiguë.

Ces contrôles concernent le design géométrique de l’asset. Ils ne certifient pas une aérodynamique, une résistance mécanique ou une aptitude au vol. Les adaptations camion/avion/hélicoptère sont des critères préparés ; elles n’ont pas été éprouvées par la création d’un modèle de chaque famille dans le projet d’origine.

## Intérieur et présentation

Respecter la phase demandée : ne pas ajouter un habitacle non référencé à une simple étude extérieure sans autorisation d’interprétation. Si le pilote est inclus, vérifier les points de contact adaptés : volant/pédales pour une voiture ; manche/palonnier ou commandes d’hélicoptère seulement si ces équipements font partie du design retenu.

Prévoir les surfaces qui ferment visuellement l’asset : passages de roues, planchers, cloisons ou plage arrière selon le cas. Un trou dans le coffre visible à travers la lunette ne se corrige pas par une vitre opaque.

Pour le verre : vérifier normales/épaisseur, shader transmissif et éclairage. Le mode Solide n’affiche pas la transparence physique. Les grandes surfaces lumineuses peuvent remplir les vitres de blanc ; inspecter les reflets et la lisibilité de l’habitacle, puis ajuster l’éclairage au lieu de simplement baisser l’opacité. Les valeurs IOR/teinte/rugosité du cas Thunderhawk sont des choix de rendu, pas des constantes universelles.

## Démontrer le fonctionnement

Rendre état fermé, état déployé et phases intermédiaires où les dégagements sont les plus faibles. Les gros plans/coupes sont utiles, mais garder aussi des vues avec toutes les pièces visibles. Consigner précisément les éléments cachés pour inspection.

Comparer des surfaces évaluées en coordonnées monde, après armature, morphs et modificateurs. Vérifier l’ordre des mécanismes séparément des collisions. Un recouvrement nul de triangles ne détecte pas nécessairement un volume entièrement contenu dans un autre ; compléter les cas pertinents par tests de volume, rayons ou enveloppes. Les contacts rembourrés ne se traitent pas comme une certification de non-intersection universelle.
