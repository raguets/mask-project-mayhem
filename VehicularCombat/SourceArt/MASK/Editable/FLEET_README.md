# Sources conservées

Les dossiers Rhino et Hurricane contiennent des copies des assemblages artistiques, véhicules, personnages et masques indépendants, ainsi que les assemblages dérivés utilisés pour l'export Unreal. Les originaux dans `art_source` ne sont pas écrasés. `fleet-source-checksums.json` consigne les empreintes des copies.

Rhino : V3, Alex V1/Jackrabbit, Bruce V1/Lifter. GameReady v3 corrige le repère d'export des masques et recentre uniquement la physique du module arrière. Les coordonnées des pièces visibles restent celles de la source. Le masque demeure une pièce du même personnage et les deux acteurs utilisent chacun leur propre squelette.

Hurricane : V7, Hondo V1 et HondoMask V1/Blaster. GameReady conserve les six pneus, la roue de secours distincte, 97 échantillons de transformation et le même squelette de Hondo pour conduite, position debout et canonnier. Les cheveux courts font partie du corps dans cette source ; aucun second personnage n'est créé.

Les scènes artistiques restent en mètres. Les exports squelettiques dérivés sont en centimètres avec racines unitaires. Les atlas, FBX et manifestes se trouvent dans `SourceArt/MASK/Rhino` et `SourceArt/MASK/Hurricane` ; les outils d'export et de revue passent par la connexion Blender MCP installée. Les scripts indiquent les chemins locaux du projet : les adapter sur un autre poste. Certaines images des sources artistiques gardent leurs chemins externes ; les atlas nécessaires au jeu sont conservés dans le dépôt.

Les dimensions, masses, ressorts, courses cachées et paramètres de conduite sont des estimations de prototype issues des modèles. Les photos de jouets, illustrations de personnages et photographies des véhicules réels ne constituent pas un plan officiel. Les limites artistiques des versions originales restent applicables.
