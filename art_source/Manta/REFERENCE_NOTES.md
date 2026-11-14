# Manta / Vanessa / Whip — registre de production

La fiche `Images de reference/Manta et Vanessa Warfield/Fiche transformation.txt` a été lue avant les images. Elle impose le démarrage commun : bascule des roues avant, rotation vers l'arrière des ailes stockées sous la voiture depuis leurs pivots arrière, avance du dessus avant/médian du capot révélant deux canons et trois missiles, relevage du panneau portant les feux arrière et sortie de trois réacteurs. Catégorie autorisée : **route / avion**, comme Thunderhawk et Raven ; pas de stationnaire. Ces propriétés expriment l'intention de l'asset, sans intégration gameplay.

## Images réellement inspectées

- Jouets Kenner : `MASK-Manta-20.jpg` ouvert seul ; photos `images.jpg`, `s-l1200.jpg`, `maskmantafulguropop.jpg`, les deux longues références `KENNER-*`, `Sabd8636145e847d6ab6ef608de86c81fw.jpg`, `tp_mask_manta_03.jpg` et vue du dessus `9b38fefaa8966449e59f4f8dc02be36333e178c7.jpg` examinées dans `references/jpg_sheet.jpg`. Carrosserie prune, toit en T, persiennes noires, graphismes jaune-vert, ailes grises et roues arrière portées par leurs racines, petit aileron avant avec arme, trois jets, feux sur panneau relevable. Les courses et pivots masqués ne sont pas des cotes officielles.
- Nissan 300ZX Z31 réelle : `1985-nissan-300zx-t-top.jpg`, `e840f76e753311d09ada842bbf267b51.jpg`, `S8-modele--nissan-300-zx-z31.jpg` sur la planche. Volumes/pentes de référence, sans remplacer les mécanismes du jouet. `1985_nissan_300zx-turbo_5-img_1415-94657.webp` est une vue supplémentaire fournie, pas encore utilisée comme validation individuelle.
- Vanessa : figurine `mask---kenner---figurine-7cm-loose---vanessa-warfield--from-manta--p-image-600068-grande.webp`, illustration `Whip.webp`, capture `Vanessa_Warfield_Pointing.webp`, toutes ouvertes individuellement. Bleu, cyan aux bras/col, gants et bottes rouges, cheveux auburn. Figurine et illustration divergent sur coiffure, empiècements et équipement.
- Whip : captures `mask-image-n-43-043.webp` et `Screenshot_2026-07-09_222014.webp` ouvertes individuellement ; illustrations `d5bb6528aec177651d0fcd0eb480ed7c.jpg` et `0bb346640f73030a466cdba0e7c51705.jpg` sur planche. Front bleu gris carré, visière frontale sombre, deux ports or, arrière de casque rouge, cou évasé et tuyaux. Pas de photographie d'un masque réel ajusté à une personne.

## Interprétations autorisées

Autorisation générale du 13/11 : personnages réalistes et habitacles non montrés. Aucune ressemblance volontaire avec une personne réelle. Vanessa part du maillage féminin continu CC0 du bundle officiel Blender Human Base Meshes v1.2.0 conservé sous `art_source/AnatomyBase`, transformé et riggé indépendamment. Un même maillage conserve visage, corps et doigts dans les quatre états ; Whip est séparé. Chevelure, armature, anatomie et cockpit sont interprétés.

Échelle estimée : carrosserie environ 4,4 m, largeur 1,82 m, toit 1,30 m ; Vanessa environ 1,70 m. Envergure et courses adaptées au mécanisme, non documentées officiellement. La validation doit distinguer inspection visuelle, contrôle de surfaces évaluées et fonctionnement de jeu non testé.

## Versions

V1 véhicule et assemblage sont des étapes conservées. Les premiers rendus véhicule ne montrent pas une transformation valide : plusieurs drivers venaient d'être invalidés ; ils ont été contrôlés après réévaluation. Le premier assemblage contient des erreurs d'import/poids et n'est pas une livraison. V2 et V3 corrigent repères, contrôle, poids, yeux et certaines surfaces. Les rendus à retenir sont uniquement ceux correspondant à la version finale effectivement inspectée.

## Corrections utilisateur du 14 novembre, prioritaires

- Sièges à ciel ouvert, aucune vitre au-dessus, aucun rail supérieur de porte. Barre centrale du T et traverses de pare-brise/arrière conservées. Cheveux de Vanessa raccourcis vers le haut des épaules.
- Ailes rangées entièrement sous la voiture, plus courtes, sans empiéter sur les roues avant ni dépasser l'enveloppe des roues arrière. Pivots immédiatement derrière les pneus arrière ; mêmes roues portées rigidement par les ailes, axes devenant longitudinaux et faces de jante orientées à l'arrière comme des turbines. Liaison renforcée, petits canons à portée intermédiaire des ailes, pointant vers +X une fois déployés. Ailerons des roues avant légèrement élargis.
- Capot un peu galbé, et vitre arrière légèrement galbée avec persiennes adaptées. Seule bande centrale d'environ 40 % de largeur avance ; quart arrière près du pare-brise fixe. Le recul relatif de la bande révèle l'ouverture des trois missiles. Avant aminci et élargi transversalement en tête de requin-marteau plate, abaissé sous l'axe des canons. Canons sur glissières propres aux phares, jamais solidaires du capot mobile.
- Missiles raccourcis. Leur mécanisme commence en même temps mais reste sous le panneau jusqu'au dégagement complet, avant la levée principale ; rétraction inverse avant fermeture. Contrôle surfaces + échantillons de volume sur 121 phases.
- Aucun becquet séparé au-dessus des feux arrière. Le panneau porte-feux est la seule planche : petite sortie vers l'arrière, puis relevage et planche horizontale sur deux montants fins, confirmée dans les deux vues arrière ouvertes individuellement. Courses et emboîtements télescopiques des montants interprétés, pas un mécanisme officiel mesuré.

V8 a révélé une dégradation de topologie avec une succession de découpes booléennes : ne pas réutiliser sa carrosserie. V9 repart de la carrosserie propre V7, avec passages de roues continus et pivots légèrement plus externes. V10 incorpore le capot partiellement fixe, les missiles raccourcis/dégagés et les supports renforcés ; V11 remplace le panneau arrière et rentre correctement les canons derrière les phares au repos. Les versions précédentes sont conservées pour historique, pas présentées comme des validations finales.


## Source consolidée V23 —14 novembre

Les dernières corrections priment : habitacle raccourci puis ensemble arrière réduit de10%, avec essieu/arches et détails préservés ; contours des4 vitrages doublés, plats, continus. Pare-brise courbé55mm et trapézoïdal. Capot convexe partout, bande centrale à course195mm ; extrémité25mm devant les canons. Les3 projectiles et guides s'inclinent30°, base horizontale. Planche de feux fermée au niveau de la caisse, cache les jets ; supports rigides horizontaux puis verticaux, trajectoire gardée en arrière de la lunette. V23 corrige aussi les petits conflits de moulures de roues et de raccord capot par des points de rupture géométriques exacts.

Vues finales et rapports listés dans README ; sources indépendantes rouvertes. V1–V22 historiques uniquement. Le ratio initial40/30/30 est remplacé par les demandes ultérieures de raccourcissement ; pas un plan coté officiel. L'adaptation Unreal est autorisée : même dynamique fixe que Thunderhawk/Raven, faction VENOM et départ extérieur à la base MASK.
