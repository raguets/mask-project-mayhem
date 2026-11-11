# Rhino V3 — pare-buffle repris sur la nouvelle photo

Référence réellement ouverte et inspectée : `Images de reference/rhino/rhino pare buffle.jpg`. Il s’agit d’une photographie du jouet, avec boîte et module arrière. Elle montre un contour fermé rectangulaire et de fins barreaux verticaux devant la calandre. Les cotes réelles et les attaches cachées ne sont pas documentées.

La V3 conserve l’assemblage V2 et son mécanisme de coulisse. L’ancien pare-buffle à deux montants hauts et traverses ouvertes est remplacé par un cadre fermé, légèrement adouci aux angles, et sept barreaux fins éditables séparément. Leur répartition est reconstruite depuis la photo non cotée. Les bornes latérales et verticales du cadre suivent exactement celles de l’encadrement de la calandre existante : largeur d’environ 1,760 m et hauteur de 1,454 m dans le modèle. Ce sont des dimensions dérivées du modèle, pas des mesures officielles du véhicule.

Le sommet passe d’environ 2,980 à 2,512 m : les montants ne dépassent plus la calandre. Le bas du contour est aligné sur son bord inférieur. Les supports télescopiques ont été replacés derrière le bord inférieur et reliés au pare-chocs par des attaches fixes interprétées. La commande `bullbar` et l’avance existante de 0,80 m sont conservées.

Sources : `art_source/Rhino/Rhino_V3.blend` et `Rhino_V3_Vehicle.blend`. V2 et copie de la session avant modification sont conservées. Les sources du module, d’Alex, de Bruce et de leurs masques restent celles déjà vérifiées ; ces assets n’ont pas été modifiés.

Vues de contrôle : `art_source/Rhino/renders/v3/`, face rapprochée, trois-quarts, pare-buffle avancé, ensemble routier et transformé. Leurs PNG sont examinés contre la photo avant livraison.

`bullbar_validation_v3.json` vérifie l’enveloppe évaluée identique à la calandre en largeur/hauteur, le cadre fermé sans arêtes non-manifold, l’ouverture au centre et les barreaux, puis les 241 images entières du mouvement contre les surfaces du camion. Aucune intersection détectée dans ce périmètre ; les raccords internes et supports télescopiques intentionnels sont exclus. Les autres mécanismes/personnages conservent le contrôle de référence `validation_v2.json`. Cette passe ne constitue pas une certification de temps continu ou de volumes contenus.

La source véhicule indépendante est effectivement rouverte et sa coulisse vérifiée à plusieurs frames ; résultat dans `standalone_vehicle_validation_v3.json`. La finition des personnages et du vêtement reste celle décrite dans le compte rendu V2.
