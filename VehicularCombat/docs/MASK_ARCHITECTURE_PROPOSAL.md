# Proposition M.A.S.K. — après stabilisation de VehicularCombat

Architecture acceptée par la demande « Réalise toutes ces étapes » du 7 novembre 2026. Son implantation progressive est suivie dans `THUNDERHAWK_IMPLEMENTATION.md`. Le présent document décrit aussi des extensions futures ; leur présence ici ne signifie pas qu'elles sont déjà opérationnelles. Les résultats du socle se trouvent dans `MIGRATION_LOG.md`.

## Séparer les responsabilités sans remplacer tout le prototype

| Élément proposé | Responsabilité |
|---|---|
| `UMaskVehicleDefinition` (PrimaryDataAsset) | Références souples aux meshes, paramètres de conduite, modes autorisés, sockets, armes et profils de collision |
| `UMaskVehicleModeComponent` | Mode actuel/cible, autorisation serveur, transfert de vitesse entre locomotions |
| `UMaskTransformationComponent` | Articulations et pistes visuelles, bornes, séquence, contrôle des volumes avant transition |
| Adaptateurs de mouvement | Chaos pour la route ; mouvement aérien distinct pour vol/vol stationnaire ; une seule autorité physique active |
| Composants d'armes et définitions | Cadence, munitions, projectile, points d'attache, effets, règles serveur communes |
| Personnage pilote | Un corps, un squelette et un visage ; poses debout/assis ; masque attaché et visibilité répliquée |
| Interface de commandes | Conduire, viser, tirer, demander un mode : mêmes commandes pour PlayerController et AIController |
| GameMode / GameState coopératifs | Missions et apparition côté serveur ; objectifs et progression de mission répliqués |

Conserver le module `VehicularCombat` et le véhicule original comme référence de non-régression. Un premier véhicule M.A.S.K. peut dériver du pawn existant ; extraire les responsabilités communes seulement lorsque ce second cas les justifie. Éviter une dépendance immédiate à GAS ou à un framework de missions sans besoin démontré.

## Transformation et physique

Le serveur autorise une transition après contrôle de vitesse, état de vie et dégagement. Répliquer un mode, une cible, un identifiant de séquence et une heure de départ serveur ; les clients évaluent les pistes articulées localement. Ne pas envoyer un RPC par os et par image.

Les pièces visuelles articulées suivent des sockets/os ou composants nommés. Les formes de collision fonctionnelles sont contrôlées séparément et testées pendant le mouvement ; ne pas animer directement un corps simulé en écrasant sa transform chaque image. Un seul système décide du mouvement du châssis à un instant donné. Lors du passage route/vol, conserver les vitesses linéaire/angulaire et activer le nouveau modèle de forces sans superposer deux réplications concurrentes.

La course du toit, les portes et réacteurs Thunderhawk, le module détachable Rhino, les pales d'un hélicoptère et les ailes d'un avion sont des mécanismes propres à leurs définitions. Leur séquencement ne doit pas être codé dans une classe universelle de voiture. Un module détachable possède sa propre autorité et son état de possession lorsqu'il devient autonome.

Les armes équipées suivent leur socket sans soudure physique au châssis. Conserver des réponses de collision explicites pour les traces de suspension, les projectiles et les objets ramassables. Le problème de contrainte autoréférente observé pendant la migration doit rester un cas de non-régression.

## Réseau, pilotes et IA

Les demandes de tir et de transition passent par le propriétaire réseau. Le serveur décide des munitions, dégâts et états de vie ; les effets peuvent être prédits ou multicast selon leur importance. Une action impossible à cause d'un cooldown n'est pas un RPC malformé : la refuser côté gameplay sans déconnecter le client.

S'appuyer sur la réplication/prédiction Chaos pour la conduite avant d'envisager un autre modèle. Définir séparément les exigences de prédiction aérienne, correction des collisions et reprise après perte de paquets. Les essais LAN à deux processus ne valident pas à eux seuls Steam, un serveur dédié, la latence Internet ou les pertes réseau.

Le pilote monte/descend par une transition de possession explicite. En conduite, conserver son squelette et ses poses ; le masque est un mesh attaché à la tête, pas un second personnage. Les pouvoirs du masque peuvent être des composants/objets de capacité à autorité serveur. L'IA utilise les mêmes demandes de conduite/tir/transformation, avec ses propres décisions et perception.

## Première intégration : Thunderhawk

1. Autorisation obtenue le 7 novembre 2026 ; conserver le périmètre du prototype et documenter les limites dans `THUNDERHAWK_IMPLEMENTATION.md`.
2. Préparer une copie d'export de la source Blender approuvée : unités/axes, origine du châssis, quatre roues, pivots, squelette de conduite, sockets et collisions simples. Conserver les sources artistiques originales. Retopologie, UV et LOD restent des travaux distincts.
3. Importer dans un dossier M.A.S.K. isolé, sans remplacer BP_PlayerVehicle. Mettre Matt et Spectrum dans des assets indépendants et vérifier les quatre états debout/assis, masque visible/caché.
4. Faire rouler Thunderhawk avec les fonctions originales et les tests réseau avant d'activer la transformation.
5. Ajouter les pistes spécifiques : portes à section de toit et section latérale coudées, canons distincts, façade arrière verticale, spoiler indépendant. Les réacteurs avancent après dégagement du capot et rentrent avant sa fermeture.
6. Contrôler les volumes pendant toute la transition, puis introduire le vol avec transfert de vitesse. Tester deux joueurs, collisions, tirs, destruction et réapparition dans chaque mode.

Les avions et hélicoptères devront ensuite valider leurs propres locomotions et géométries ; un premier Thunderhawk ne certifiera pas automatiquement ces familles.
