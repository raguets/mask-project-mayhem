# Silent Valley — provenance des assets

Budget d'acquisition : **0 €**. Les imports gratuits Fab du 10 novembre sont consignés dans le dernier lot ci-dessous. Les statuts historiques restent datés ; présence locale et droits de redistribution sont distincts.

| Asset | Source | Licence/statut gratuit visible | Statut | Destination / usage |
|---|---|---|---|---|
| Thunderhawk, Rhino, Hurricane et leurs pilotes/masques | Sources Blender et assets du projet déjà intégrés | Créations existantes du propriétaire ; aucun nouveau droit tiers vérifié ici | DÉJÀ IMPORTÉ, VÉRIFIÉ dans le dépôt | `/Game/MASK/Thunderhawk`, `/Game/MASK/Rhino`, `/Game/MASK/Hurricane`, réutilisés sans remplacement |
| Boulder Hill V6 | `../art_source/Boulder_Hill/BoulderHill_V6_Base.blend` et références du propriétaire | Source éditable existante ; dimensions/parties cachées interprétées | DÉJÀ IMPORTÉ, VÉRIFIÉ dans la carte et les passages G2 | `/Game/MASK/Environment/SilentValley/Structures/BoulderHill/SM_BoulderHill_V6_Open_v2` ; pose ouverte statique |
| Small Beach Rock, identifiant Megascans `wd4kfdx`, qualité Medium/tier_2 | Fab importé par le propriétaire ; URL de fiche exacte à vérifier, ne pas inventer un UUID | NON VÉRIFIÉ : présence locale ne prouve ni gratuité actuelle ni licence du compte | DÉJÀ IMPORTÉ, VÉRIFIÉ par chargement réel dans l'éditeur après scan synchrone (asset-resolution.json) ; acquisition non effectuée par l'agent | `/Game/Fab/Megascans/3D/Small_Beach_Rock_wd4kfdx/Medium/wd4kfdx_tier_2/StaticMeshes/wd4kfdx_tier_2` ; réemploi G3 après vérification |
| Landscape, tracé routier et matériaux de blockout | Géométrie et paramètres originaux créés dans l'éditeur du projet | Aucun asset tiers ajouté | CRÉÉS dans Unreal, VÉRIFIÉS en rendu et conduite | `/Game/MASK/Environment/SilentValley/` |
| Pins, herbe, falaises photoréalistes supplémentaires | Ressources Fab précises à rechercher seulement après G1/G2 | NON VÉRIFIÉ, aucune acquisition autorisée si contrat/paiement requis | PLACEHOLDERS avant sélection ; liens à ajouter lors de la recherche G3 | Aucune destination importée à ce stade |

Les primitives de blockout doivent être étiquetées comme telles. Bridge ne fait pas partie de la chaîne de production. Ce manifeste sera complété à chaque ajout réellement exécuté, avec URL précise, licence affichée et chemin local.

## Présélection G3 — aucune acquisition effectuée

Fiches Fab consultées le 8 novembre 2026. La mention publique « Free » ne constitue pas une vérification des droits du compte ; la rubrique licence des pages lisibles affiche `-`.

| Ressource | Fiche source exacte | Statut constaté | Usage proposé / limites |
|---|---|---|---|
| Grass, Quixel Megascans | [Fab — Grass](https://www.fab.com/listings/6f1ba858-c1c3-4ccd-89e0-58a29ffff1ad) | DISPONIBLE DANS FAB, prix public Free ; licence du compte NON VÉRIFIÉE ; NON IMPORTÉ | Atlas de textures d'herbe ; ne contient pas un peuplement végétal prêt à jouer. Destination éventuelle `Environment/SilentValley/Vegetation`, après import autorisé par le propriétaire. |
| Megaplants: Baltic Pine, Quixel | [Fab — Baltic Pine](https://www.fab.com/listings/a2b04e81-5075-479f-a9d2-4940022f330a) | DISPONIBLE DANS FAB, prix public Free ; NON IMPORTÉ, NON RETENU pour le premier lot | La fiche demande PVE et Nanite Foliage expérimentaux. Aucun plugin supplémentaire activé. Préférer un mesh statique compatible avec l'installation présente. |

Si une ressource est retenue : ouvrir sa fiche dans Fab depuis Unreal, vérifier le prix et les conditions avec le compte propriétaire, puis utiliser l'ajout au projet proposé par Fab. L'agent n'accepte aucune condition à sa place. Ces ressources n'empêchent pas les tests du blockout. Le script `build_silent_valley_showcase.py` prévoit seulement le réemploi du rocher déjà importé, sans acquisition ; son exécution et sa validation doivent être consignées avant de compter le peuplement comme réalisé.

Ajout original : `M_SV_RoadMarked_v2`, shader de marquages procéduraux jaune/blanc créé dans Unreal par `Tools/Art/mark_silent_valley_road.py` ; aucun contenu externe ni téléchargement. Destination `/Game/MASK/Environment/SilentValley/Materials`. La v1 est une tentative locale en échec shader, conservée et inutilisée. Les connexions d'API 5.8 sont vérifiées et la v2 a été inspectée en rendu de jeu. Une recherche Fab préliminaire n'a pas établi la correspondance exacte du rocher local avec une fiche ni de nouveaux droits gratuits : aucune acquisition supplémentaire effectuée ni ajoutée à la carte.

## Réemploi effectivement réalisé — premier lot G3

- `Small Beach Rock wd4kfdx` : 39 instances PCG sur 500 m de Pinewood, vérifiées après réouverture et en rendu. Source locale Fab ci-dessus ; URL exacte et droits du compte restent NON VÉRIFIÉS. Aucun téléchargement ni acquisition supplémentaire. L'import original demeure inchangé.
- `M_SV_BeachRock_Instanced_v1` et `MI_SV_BeachRock_Instanced_0_v1` : copies du master et de l'instance de ce rocher dans `Environment/SilentValley/Materials`, flag InstancedStaticMeshes activé pour corriger le fallback de rendu. Contenu dérivé du même import Fab, donc même statut de provenance/licence ; ce ne sont pas des matériaux originaux indépendants.
- `PCG_SV_PinewoodRocks_v1` : graphe et placement originaux, références au rocher existant. Nettoyage/régénération contrôlés, exclusions précalculées ; aucune collision sur les instances.
- `M_SV_ValleySurface_v2` : shader original de prairie sèche/versants, sans texture externe ni modification de géométrie. V1 conservée localement inutilisée après rejet du contraste en rendu. La couche est une base de travail et ne constitue pas un sol photoréaliste fini.
- Limites de prototype : cubes natifs `/Engine/BasicShapes/Cube`, cinq colliders invisibles, aucun téléchargement.

## Lisibilité et mission V0 — 9 novembre 2026

- `M_SV_ValleySurface_v3` et `v4` : matériaux procéduraux originaux, sans texture externe. V3 conservée après rejet du grain trop marqué ; v4 active sur le Landscape, couleurs prairie/roche et grain adoucis. Dix captures jour/soir inspectées sous `Saved/SilentValley/views-readability-r3`. Ce sol reste une base de prototype, sans relief de matériau, végétation ni falaises réalistes.
- Cinq panneaux recto/verso et dix poteaux : textes et cubes natifs Unreal, dimensions estimées, sans collision. Lumière `SV_AmbientFill` et skylight ajustés ; matériaux de Boulder Hill préservés. Relief et route inchangés.
- `DA_SilentValley_01` : données originales de temporisation/récompense. Escorte : ancien `BP_PlayerVehicle`, IA et armes déjà présents. Module de guidage : cube temporaire natif, sans collision. Aucun nouvel asset V.E.N.O.M. revendiqué.
- Aucun achat, téléchargement ou nouvelle acquisition. La licence précise du rocher Fab local reste à vérifier avant diffusion.

- `M_SV_RoadMarked_v3` : dérivé original de v2, sans texture externe ; variation de grain et rugosité en coordonnées monde, marquage conservé. Dix vues jour/soir `views-asphalt-r1` inspectées et matériau vérifié sur les 476 segments après réouverture. Priorité du soleil distincte du fill pour les passes forward. Pas de déplacement de surface ni de modification des collisions.

## Environnement naturel — 10 novembre 2026

Imports gratuits effectivement exécutés et sauvegardés dans le plugin Fab natif :

| Ressource | Source locale et usage | État |
|---|---|---|
| [Tree Baltic Pine](https://www.fab.com/listings/a2b04e81-5075-479f-a9d2-4940022f330a) | `Content/Megaplant_Library/Tree_Baltic_Pine` ; quatre variantes squelettiques Nanite, sources PVE, branches et textures conservées | Importé ; substitut visuel de conifère du Colorado, implantation/rendu à valider |
| Wild Grass, Megascans `vczndjqja` | `Content/Fab/Megascans/Plants/Wild_Grass_vczndjqja/Medium` ; huit variantes et textures 2K | Importé et sauvegardé ; implantation/rendu à valider |
| Small Beach Rock `wd4kfdx` | Import local préexistant ci-dessus | Réutilisé pour les berges, sans nouveau téléchargement |
| Sol naturel, lac et atmosphère | `M_SV_NaturalTerrain_v1`, `M_SV_LakeWater_v1`, `MI_SV_Clouds_v1` | Sol dérivé utilisant la texture du rocher ; eau originale Single Layer Water ; nuages dérivés du matériau moteur UE |

Aucun paiement ni acceptation de nouvelles conditions. Les URL exactes des fiches et la licence affichée restent à compléter avant diffusion externe. Les imports précédents et les originaux Fab sont conservés. Référence photo, autorisation et limites : [rapport du paysage](levels/SILENT_VALLEY_NATURAL_ENVIRONMENT.md).