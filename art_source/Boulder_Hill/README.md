# Boulder Hill V6

Source assemblée : `BoulderHill_V6_Assembly.blend`. Base indépendante : `BoulderHill_V6_Base.blend`. Les versions V1 à V5 et les sessions de travail sont conservées. Modélisation, inspections, rendus et sauvegardes par la connexion Blender MCP installée.

V6 corrige l'aspect : marron chaud intermédiaire après le rejet du beige V4 et du brun trop sombre V5. Lumière d’ambiance renforcée, soleil et lumière principale relevés, grand éclairage frontal doux. Le viewport utilise les lumières et le monde de la scène. Géométrie et mécanismes identiques à V4 ; leurs contrôles restent applicables. Les deux vues V6 servent à vérifier la couleur et l’éclairage.

## Utilisation

Sélectionner `BoulderHill_Control`. La timeline native permet d'inspecter la transformation sans script à relancer :

| Image | État |
|---|---|
| 1 | Station, vitrine verticale, garage rangé, rocher en place |
| 65 | Prisme de la devanture à mi-bascule |
| 181 | Défense déployée, porte du garage fermée |
| 211 | Double porte ouverte |
| 285 | Thunderhawk sort du garage |
| 510 | Rhino sort du garage |

`battle_mode` pilote la transformation de 0 à 1. Cette propriété est animée : changer d'image reprend la valeur de la timeline. Les commandes partielles non animées peuvent être utilisées séparément : `pumps`, `sign_open`, `sign_guns`, `store_armor`, `garage_deploy`, `gate_open`, `boulder_fall`, `turret_lift`, `turret_extension`, `turret_yaw`. Les champs commençant par `_` sont des résultats internes de drivers, pas des commandes utilisateur. Les combinaisons manuelles arbitraires ne constituent pas une séquence validée.

La devanture est **un seul prisme triangulaire** : cadre, vitrage, joues triangulaires et face blindée suivent le même pivot inférieur, `BH_StorefrontPivot`. Le prisme tourne de 90° ; sa face vitrée se retrouve au sol, sa face inclinée devient le blindage. Aucun second prisme n'apparaît. Les meubles du magasin ont été reculés hors du volume balayé.

Les mêmes colonnes bleues des pompes pivotent en canons. L'enseigne se rabat vers le bas avant la sortie de ses deux canons. Le rocher mobile reste un objet distinct ; sa chute précède la montée du canon et du fauteuil. Le garage tourne de 90° dans le plan horizontal et sa porte courbe possède deux battants indépendants. Les axes des battants sont déportés de la coque avec un jeu latéral.

La montagne reprend la forme approuvée de V3, réduite à environ 31,6 m de haut. Le promontoire du canon rejoint le flanc arrière du relief. Les retours rocheux raccordent les côtés du magasin et du garage. Une dalle rectangulaire de 24,2 × 20,5 m, sans route rapportée, se trouve devant la base.

## Capacité et véhicules

Quatre emplacements estimés de 10,8 × 4,5 m, espacés de 6 m, desservent une allée. Ils sont dimensionnés avec le Rhino existant : 9,18 × 3,19 × 4,49 m. Ouverture nominale de la double porte : 6 m de large et 5,43 m de haut. Les cotes sont des estimations de production, pas des dimensions officielles.

L'assemblage comporte des copies des véritables véhicules Thunderhawk V14 et Rhino V3 à leur échelle d'origine, sans nouveaux personnages. Ces copies restent figées en configuration routière et suivent des courbes natives. Les fichiers originaux des véhicules ne sont pas modifiés. Dans la base indépendante, les véhicules et leurs courbes sont retirés ; la montagne, les bâtiments et tous les mécanismes restent éditables.

La vue `06_hangar_cutaway.png` masque explicitement le massif rocheux et le plafond pour montrer les quatre places. C'est une vue d'inspection ; la base complète conserve son plafond et sa montagne.

## Références, contrôles et limites

Références réellement inspectées : les neuf images de `Images de reference/boulder hill`, l'exemple `prisme-triangulaire-k9-en.webp` et la vidéo utilisateur entre 1 et 13 secondes. Voir `../../docs/art/BoulderHill_reference_review_v1.md`. Les photographies représentent le jouet, la vidéo et certaines vues représentent le dessin animé.

Rendus actuels de couleur et d’éclairage : `renders/v6/`. Les huit vues géométriques V4 restent dans `renders/v4/`. Les manifestes indiquent les images et les collections cachées par vue. Les anciennes passes sous `../../docs/qa/boulder_v1`, `boulder_v2` et `boulder_v3_first` documentent les corrections ; elles ne remplacent pas les vues V4.

Rapports finaux sous `../../docs/qa/` : `boulder_layout_final.json` (gabarits et quatre emplacements, véhicules stationnés, battants), `boulder_phases_final.json` (surfaces des mécanismes), `boulder_demo_sequence_v4.json` (espacement entre les deux véhicules), `boulder_standalone_final.json` (réouverture et indépendance). Synthèse géométrique V4 : `validation_v4.json`. Correction et réouverture V6 : `color_light_v6.json` et `validation_v6.json`. Lire leurs méthodes et résultats réels. Les contrôles sont discrets : ils ne prouvent pas une absence continue de toute collision ou une simulation physique.

Le volume intérieur agrandi, les dimensions, le relief de la montagne, les structures cachées, les trajectoires et certaines finitions sont interprétés. Les véhicules de démonstration ne simulent ni braquage, ni roulement des pneus, ni suspension ; le passage de la dalle au terrain est une présentation cinématique. Le rocher utilise une trajectoire animée, pas des corps rigides. La fidélité visuelle reste une interprétation des références, sans revendication de reproduction métrologique ni de modèle Unreal déjà optimisé.

## Méthode à réutiliser

Valider d'abord la silhouette de l'environnement, y compris son relief d'arrière-plan. Une structure peut être géométriquement assez grande et rester visuellement incorrecte. Définir la coupe des pièces mobiles avant les détails : les trois poses du prisme évitent de confondre une façade triangulaire complète avec un panneau incliné.

Mesurer les véhicules réels du projet avant de choisir portes, allées et places. Séparer le volume fonctionnel souterrain de la silhouette extérieure. Vérifier les battants contre leur propre coque : une trajectoire de véhicule libre ne prouve pas que la porte s'ouvre correctement. Inspecter aussi les raccords, les marges de dalle et la façon dont un poste d'arme rejoint son support.

Dans Blender, utiliser des propriétés intermédiaires natives pour les expressions de drivers longues : la limite de 255 caractères peut tronquer une formule pourtant correcte. Après modification de hiérarchie, réévaluer les drivers puis vérifier leur validité après réouverture. Conserver les sources précédentes, rendre les vues affectées et noter les limites restantes.
