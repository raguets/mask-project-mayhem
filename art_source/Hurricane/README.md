# Hurricane V7 — Hondo MacLean

Source assemblée : `Hurricane_V7_Assembly.blend`. Véhicule indépendant : `Hurricane_V7_Vehicle.blend`. Hondo et son masque indépendant : `../Hondo_MacLean/HondoMacLean_V1.blend` et `../Hondo_MacLean/HondoMask_V1.blend`. Les versions et sauvegardes précédentes sont conservées. Modélisation, inspections, rendus et exports effectués dans Blender par la connexion MCP installée.

## Correction du châssis et du côté du canon

La course estimée de la carrosserie est réduite de 0,58 à **0,30 m**. Le haut des roues centrales demeure caché sur environ 0,12 m par le bas de caisse, sans traverser sa surface. Le bloc noir porteur est plus haut, avec quatre montants entre les roues et des longerons supérieurs suivant le relevage. Les six pneus sont des objets persistants : aucune substitution pendant la transformation.

Le canon unique de pare-brise est à **droite du véhicule** : axe -Y, avec +X vers l'avant. Cette correction utilisateur remplace la première consigne gauche. Son volet possède une surface courbe et un axe suivant le bord incliné du vitrage. Les phares possèdent chacun une lentille escamotée et un canon télescopique. Le disque denté et la roue de secours éjectable sont deux systèmes distincts ; le disque reste relié au châssis par ses guides.

## Commandes

Sélectionner `Hurricane_Control`. Les propriétés se trouvent dans les propriétés personnalisées de l'objet. L'animation de `battle_mode` fournit la transformation assemblée ; les autres commandes permettent des essais indépendants. Pour piloter manuellement une propriété animée, retirer ou neutraliser ses clés dans une copie de travail.

| Commande | Fonction |
|---|---|
| `battle_mode` | 0 route, 1 défense ; séquence des mécanismes |
| `chassis_lift` | Relevage de la carrosserie et déploiement du châssis |
| `roof_open` | Ouverture du toit vers l'avant |
| `roof_guns` | Déploiement des doubles canons après ouverture |
| `windshield_cannon` | Volet et canon droit du pare-brise |
| `headlight_cannons` | Escamotage des lentilles puis sortie des canons |
| `lower_cannons` | Canons inférieurs, conditionnés par le relevage |
| `rear_disc` / `disc_spin` | Sortie du disque arrière / rotation en degrés |
| `spare_eject` | Éjection animée de la roue carénée vers l'arrière |

Toutes les commandes de déploiement vont de 0 à 1. Les propriétés commençant par `_` sont des résultats internes pilotés, à conserver.

Timeline : image **1** route ; **151** défense ; **191** roue de secours en vol ; **211** roue arrivée au sol ; fin à 241. Le toit comporte des réserves pour les deux canons et des couvercles articulés. La plateforme et la trajectoire intermédiaire de Hondo dégagent le toit fixe avant sa montée. Ces mécanismes cachés sont une interprétation, pas un relevé du jouet.

Sur `HondoMacLean_Rig`, `mask_on` affiche ou cache le masque du même personnage. `driving_pose` vaut 0 debout / 1 assis. Dans l'assemblage, `gunner_pose` et `vehicle_lift` suivent la voiture ; `in_vehicle=1` active son placement. Dans la source indépendante, ces deux liens sont retirés individuellement et `in_vehicle=0` ; `gunner_pose` reste une commande manuelle. Les drivers des os, les poids, le visage sous le masque et le corps unique sont conservés.

## Références et validation

Les 26 images fournies et les images de la vidéo utilisateur ont été inspectées. Analyse : `../../docs/art/Hurricane_reference_review_v1.md`. Les photographies du jouet guident la livrée et les accessoires ; les photos de Bel Air 1957 guident les formes automobiles. L'illustration et la figurine guident une interprétation anatomique humaine générique de Hondo. Aucun portrait d'une personne réelle n'est revendiqué. Provenance anatomique CC0 : `../AnatomyBase/` ; adaptation indépendante de la base éditable déjà employée dans le projet.

`motion_validation_v7.json` contrôle les surfaces évaluées sur **70 positions** entre les images 1 et 241 : toit, passage des doubles canons, volet/canon droit, phares, canons bas, disque, roue éjectée, pneus et tête/masque. Aucun croisement détecté dans ce périmètre, aucun driver invalide. Le même corps, la même tête et la même armature sont conservés. Les mains sont proches des commandes ; les semelles sont à environ 1,8 mm des pédales et en contact de 1,5 mm avec la plateforme. Ces distances minimales n'établissent pas une prise correcte de tous les doigts.

Rendus de la géométrie finale : `renders/v7_final/`. Revue des quatre états debout/assis avec/sans masque de Hondo, dont la géométrie n'a pas changé en V7 : `renders/v6_review/05_hondo_stand.png` à `08_hondo_seated_mask.png`. Les manifestes identifient les sources et les vues réellement calculées. Exports : `component_exports_v7.json` ; réouvertures : `standalone_validation_v7.json`.

## Limites conservées

Les dimensions, le relevage, les courses, les cavités internes, l'intérieur et la trajectoire d'éjection sont estimés. Le contrôle par échantillons ne certifie pas le mouvement continu, toutes les combinaisons arbitraires des commandes, les volumes fermés, la simulation de suspension ou de vêtements. La prise des doigts, la compression des sièges et les contacts souples restent approximatifs. Hondo conserve une finition stylisée ; fidélité photoréaliste, retopologie de jeu, UV complets, LOD et import Unreal ne sont pas validés dans cette passe. Les flammes latérales utilisent des UV et une texture RGBA procédurale empaquetée, avec contours JSON et générateur conservés dans `textures/` et `scripts/prepare_side_paint_texture.py`. Les peintures du capot, du toit et du coffre restent des maillages éditables ; leur densité doit être réduite ou cuite pour un usage temps réel.

Les scripts de construction sont historiques et non idempotents. Ne pas les rejouer sur la version affinée. Charger une copie de la précondition correspondante et lire le script avant usage.
