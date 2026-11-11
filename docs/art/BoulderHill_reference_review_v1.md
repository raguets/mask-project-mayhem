# Boulder Hill — références et choix de production

Références fournies et inspectées le 5 novembre 2026 : les neuf images dans `Images de reference/boulder hill`, ainsi que la vidéo utilisateur <https://www.youtube.com/watch?v=CYgT9k8lJyY>, intervalle 1–13 secondes. Les images sont des photographies du jouet et une vue de dessin animé, pas des photographies d'une véritable installation. La vidéo montre le dessin animé. Les images `images (2).jpg` et `images (4).jpg` documentent particulièrement la porte courbe et le passage d'un véhicule.

## Formes et mouvements retenus

- Boutique rectangulaire blanche, toiture bleue, grande façade vitrée et fenêtres latérales ; deux pompes ivoire à éléments bleus sur une île commune.
- Enseigne GAS sur un haut poteau : panneau rabattable vers le bas, deux canons derrière. Les canons se rétractent avant la fermeture du panneau.
- La devanture EST un prisme triangulaire. Le prisme entier pivote de 90° autour du bas de la vitrine : le vitrage se retrouve contre le sol, et la face inclinée en acier, jusque-là dans le magasin, devient le blindage. Cette correction utilisateur est illustrée par `Images de reference/prisme-triangulaire-k9-en.webp`, également inspecté. Ce n'est pas un panneau plat ni un prisme distinct qui sortirait ensuite.
- Garage déployé horizontalement en quart de cercle, toiture à arête radiale, double porte dans la façade courbe, sortie orientée en diagonale.
- Rocher supérieur détachable ; plate-forme avec canon, fauteuil, repose-pieds et console émergeant de la colonne creuse. Le canon peut pivoter en azimut.
- Les colonnes bleues des pompes pivotent vers l'avant pour devenir des canons. Le mécanisme reste sous le compteur.

## Interprétations explicites

Les deux variantes jouet/dessin animé ne donnent pas toutes les pièces cachées ni les cotes. Les dimensions, les liaisons internes, le canon télescopique et la trajectoire animée du rocher sont interprétés. La chute n'est pas une simulation de rigid bodies. Le principe du prisme et son basculement viennent de la correction utilisateur ; les dimensions exactes et la structure interne du prisme sont estimées.

La base est adossée à une montagne, conformément à la vue de dessin animé et à la correction utilisateur. L'utilisateur a approuvé la forme de la montagne V3 et demandé de réduire son volume, de mieux y intégrer le support du canon et de fermer les vides entre la base et les bords. V4 conserve les crêtes, réduit la masse lointaine à environ 32 m de haut, intègre un contrefort asymétrique et rapproche les bords de la dalle. Il n'y a pas de route devant la sortie : seulement une dalle rectangulaire compacte.

Le volume arrière est prolongé sous un massif rocheux pour répondre à la demande d'accueillir plusieurs véhicules. Quatre emplacements de 10,8 × 4,5 m, espacés de 6 m, et une allée permettent de ranger des véhicules aux dimensions du Rhino existant. Ce plan intérieur, l'atelier, les consoles et la voie de sortie sont des aménagements estimés, non des éléments présentés comme officiels.

Les véritables meshes Thunderhawk V14 et Rhino V3 servent de véhicules de démonstration à leur échelle d'origine. Leurs sources n'ont pas été modifiées. Ces copies de démonstration sont figées dans leur configuration routière et suivent des courbes Blender natives ; elles ne simulent ni le braquage des roues ni la suspension. La base possède aussi une source autonome qui exclut ces copies.

## Validation et limites

Les premières vues V1 ont entraîné des corrections du rocher, des normales du toit, du chevauchement des sols, de la rétraction des canons d'enseigne et du pivot des canons des pompes. Les contrôles finaux, les vues réellement inspectées et les limitations sont consignés dans `art_source/Boulder_Hill/README.md` et les rapports sous `docs/qa`.

La ressemblance doit être appréciée à partir des rendus joints. Ce modèle n'est pas une reproduction métrologique du jouet ; le hangar agrandi et les parties cachées sont une adaptation à l'échelle des véhicules du projet.
