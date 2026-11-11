# Silent Valley — paysage, atmosphère et lac

Passe du 10 novembre 2026. Objectif : une première zone naturelle cohérente autour de Pinewood et d'un petit lac. La validation artistique exige les rendus inspectés ; une sauvegarde seule ne constitue pas cette validation.

La [photo de Pine Valley Ranch](https://www.uncovercolorado.com/wp-content/uploads/2021/02/pine-lake-pine-valley-ranch-colorado-1600x800-1.jpg) a été inspectée dans Chrome : collines rocheuses arrondies, conifères dispersés, herbes sèches, berges basses et irrégulières, eau bleue légèrement ridée et cumulus espacés. L'utilisateur a autorisé le choix de références du Colorado et l'interprétation de l'implantation. La photo sert à la comparaison visuelle ; elle n'est pas une texture du jeu.

Le relief est une interprétation procédurale, avec un bassin centré en (-1050, -550, 54) mètres. L'emprise nominale du lac est d'environ 280 × 180 m, la profondeur maximale d'environ 6,5 m ; le rivage effectif dépend de l'intersection eau/terrain. Ces chiffres sont des choix locaux, pas des mesures de la photo. Le pin baltique Quixel est utilisé comme substitut visuel de conifère ; il ne représente pas une identification botanique du Colorado.

## Ressources et sources

- Pins : `Content/Megaplant_Library/Tree_Baltic_Pine`, import gratuit effectué dans Fab, quatre variantes squelettiques avec sources PVE, branches, matériaux et textures préservés. `ProceduralVegetationEditor` natif UE activé, ainsi que `r.Nanite.Foliage` pour les assemblages. Cette fonctionnalité est expérimentale ; rendu et coût doivent être contrôlés.
- Herbe : `Content/Fab/Megascans/Plants/Wild_Grass_vczndjqja/Medium`, import Fab Quixel gratuit sauvegardé, huit variantes, textures 2K. Aperçu inspecté avant import.
- Rochers : réemploi du `Small_Beach_Rock_wd4kfdx` local, sans modifier l'ancien graphe PCG ni ses 39 instances.
- Eau : matériau original `M_SV_LakeWater_v1`, Single Layer Water, absorption/diffusion, normales animées et masque de contour. Surface sans collision ; pas de nage, flottaison ou dégâts de noyade implémentés.
- Nuages : instance locale `MI_SV_Clouds_v1` dérivée du matériau volumétrique fourni avec Unreal ; matériau moteur conservé. Couche à 2,2 km, épaisseur 2,8 km, éclairage et brume ajustés.

Aucun achat payant ni installation de logiciel. Les liens exacts des fiches/licences des imports doivent être joints au manifeste avant une diffusion externe ; aucune validation juridique n'est revendiquée.

## Génération et garanties techniques

`Tools/Art/build_silent_valley_natural_environment.py` charge seulement la carte indépendante, conserve une copie datée, affine le relief, puis enregistre matériaux, lac et atmosphère. Le traitement natif `RefineNaturalLandscape` conserve les échantillons de hauteur dans le couloir de 80 m autour de la route et près des cinq lieux de mission. Le marqueur `SV_NATURAL_TERRAIN_V1` interdit une seconde déformation cumulative. Une nouvelle révision du relief doit partir de la source antérieure ou utiliser une migration explicite.

La première modification a changé 3 601 889 échantillons hors zones protégées. Les 382 sondes de collision dans le couloir ont montré un écart maximal de 0,361 cm après reconstruction du heightfield, sous le centimètre de tolérance et sous les 3,125 cm de quantification verticale du Landscape. La route, ses 476 segments, les points de départ, les objectifs et les matériaux de Boulder Hill restent conservés.

`Tools/Art/plant_silent_valley_environment.py` emploie une graine fixe, des regroupements irréguliers et des projections sur le vrai Landscape. Les exclusions portent sur l'intégralité de la route, les points de départ et les objectifs. Les instances natives restent persistantes et éditables ; le script reconstruit leur placement après une modification de la route. Herbes et rochers utilisent HISM ; les arbres gardent leurs assemblages dans des composants InstancedSkinnedMesh. Aucun obstacle de collision ou de navigation ajouté. Les matériaux d'instanciation sont des copies locales ; imports originaux préservés.

`validate_silent_valley_environment.py` contrôle indépendamment la carte rouverte, les instances, les collisions, le bassin, huit points de berge, les nuages et la conservation du parcours. `Capture-SilentValley.ps1 -Environment` produit dix vues jour/soir depuis la route, la rive, une vue large du lac et le col, avec HUD masqué. Ces contrôles sont distincts de la conduite physique et d'une validation à la manette.

## État de validation

Mise à jour 11 novembre : 514 pins, 10826 herbes et 115 rochers de berge sauvegardés. TSR activé, bark local relié aux textures importées ; lac v2 sans collision, normales réduites ; soleil 75000 lux et histogramme -8 à16, nuages 2,2–4km. Mips de rendu du Landscape reconstruits sans modifier mip0 (16 textures,95 sondes collision inchangées). Arrière-plan v2 : winding corrigé, précédent conservé. Compilation native r15 : quatre sorties0. Mission `natural-ballistic-r3` :14 contrôles passés après compensation de chute du projectile dans le TEST uniquement. Rhino :9548m, écart max0,923m, aucune perte de contact roue. [Preuves](../validation/silent-valley/natural-environment-r3).

**Validation artistique incomplète** : dix vues `views-natural-winding-r3` produites sortie0 ; la vue du col montre le raccord distant corrigé mais la rive garde une paroi abrupte. Le heightfield source exporté révèle des sauts32,22m entre sommets espacés2m, près de(-1702,-902)m. Hypothèse à vérifier : recherche spatiale de route limitée aux3×3 cellules100m alors que la transition naturelle atteint180m ; certaines cellules candidates sont exclues et le poids devient discontinu. Corriger cette géométrie hors couloirs/POI protégés, puis reprojeter la végétation affectée. Ne pas déclarer tout le clipping résolu. Traversée caméra continue pas encore exécutée ; package/coop non revalidés. Le texte historique ci-dessous décrit l'état antérieur.

À compléter après la construction des assemblages de pins et les rendus. Rapports de travail : `Saved/SilentValley/environment-v1`. Compilation native : `environment-actions-r5`, six commandes exportées réussies. La mission et la maniabilité précédentes ne sont pas réimplémentées. Les captures de cette nouvelle passe, la régression complète de conduite et la mission après modification du paysage ne sont pas encore revendiquées comme réussies.
