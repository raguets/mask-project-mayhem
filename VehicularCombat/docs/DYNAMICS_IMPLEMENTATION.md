# Transformations en mouvement et dynamique — 8 novembre 2026

**Réglage avion actuel : [50 à 300 km/h, avec accélération et freinage progressifs](AIRCRAFT_SPEED_RANGE.md).** Les chiffres de vitesse ci-dessous décrivent la livraison initiale.

**Correction suivante : [roues arrière d'Hurricane et limite de vol à 108 km/h](HANDLING_FIXES.md).** Les résultats r2 ci-dessous conservent le périmètre de la première livraison de dynamique.

Branche `feature/moving-transform-dynamics`, depuis `af3c168`, Unreal Engine 5.8.2. Aucun modèle, fichier Blender, asset artistique ou module Unreal n'est renommé ou supprimé.

## Comportement

Les transformations ne forcent plus le freinage et ne sont plus refusées pour cause de vitesse. Les enveloppes de dégagement restent contrôlées au déploiement. Le même corps Chaos conserve sa vitesse pendant la transformation.

Thunderhawk déploie en roulant, puis reçoit une assistance de décollage limitée à quelques mètres. RT/LT augmentent/diminuent une vitesse cible ; leur relâchement conserve la croisière. La cible minimale par défaut est de 18 m/s (64,8 km/h). Un avion continue donc d'avancer quand on maintient LT. La vitesse réelle évolue sous des forces finies : elle peut transitoirement s'écarter de la consigne lors d'une collision ou d'une manœuvre, elle n'est pas écrasée artificiellement à la valeur minimale.

X en vol passe en `Landing` : les ailes restent déployées pendant la descente automatique. Le repli commence à hauteur des roues, puis les forces des roues/suspensions/moteur reprennent. L'accélérateur reste disponible. La descente continue aussi si le terrain est initialement hors de portée de la sonde. L'atterrissage suppose un terrain praticable : il ne planifie pas un trajet autour des montagnes, bâtiments ou autres obstacles.

Le virage avion couple un roulis physique à la force latérale et au lacet. Le stick vertical règle le tangage ; A/B ne donnent plus d'impulsion de saut en l'air. La caméra cockpit conserve l'inclinaison du véhicule même quand la vue est orientée au stick droit.

Le profil `Rotorcraft` permet une vitesse cible nulle, le stationnement, la montée/descente et la pose. L'inclinaison du rotor suit l'accélération : nez abaissé pour accélérer, relevé pour freiner, roulis lors d'un virage en déplacement. Il est disponible dans les données pour les futurs hélicoptères. Les tests utilisent une copie transitoire des données de Thunderhawk comme véhicule de substitution : aucun hélicoptère artistique n'est annoncé.

Le profil `FixedWing` est partagé par les futures conversions voiture/avion telles que Raven, Manta et Firefly. Il suffit de sélectionner le profil et ses réglages dans leur définition ; ces véhicules ne sont pas ajoutés par cette modification.

Rhino éjecte le même module dès le début du déploiement, vers l'arrière. Une courte séparation initiale évite le chevauchement des volumes physiques, puis le module reçoit la vitesse du camion et une vitesse relative de recul de 8 m/s. Le camion conserve son élan et l'IA accompagne le joueur. Au rappel, le module cesse d'être un corps indépendant, se replace derrière le camion et s'attache immédiatement. X depuis le module transfère d'abord le joueur au camion, si ce dernier n'est pas occupé par un autre humain. Aucun stationnement ni animation de réunion complexe n'est requis. Bruce reste le même personnage et change directement de siège.

Hurricane reste au sol et peut lui aussi déployer ses six roues en roulant.

Sa simulation conserve désormais six emplacements stables : quatre supports actifs en route, six après déploiement. La paire centrale rentrée n'apporte ni contact au sol, ni traction, ni freinage. Cela évite une course dans les sorties asynchrones de Chaos lors d'un changement de taille du tableau de roues en mouvement. Les six pneus visibles et les vitesses du châssis restent persistants ; le moteur n'est pas recréé pour ce changement.

## Modèle physique et réglages

`UMaskDynamicsComponent` applique les forces au corps existant. L'énergie affichée dans les rapports est calculée à partir de sa masse et de sa vitesse réelles : `E = ½mv²`. Le moteur routier reste celui de Chaos, limité en puissance par `P = couple × régime angulaire`. La traînée croît avec `v²`, la résistance au roulement dépend du poids et les freins restent des couples de roues finis. Les pneus ont une adhérence moins excessive. Le bonus de puissance M.A.S.K. agit sur la puissance disponible plutôt que sur une multiplication instantanée de la vitesse.

En vol, poussée, traînée, portance assistée et couples d'attitude sont bornés. Le couple utilise le tenseur d'inertie du corps. Le virage coordonné utilise `vitesse de lacet ≈ g × tan(roulis) / vitesse`. Il n'y a pas de changement direct de position, rotation ou vitesse pour piloter l'avion ; le repositionnement du module Rhino est en revanche le comportement explicitement demandé.

Les masses et paramètres sont des estimations de jeu configurables dans `FMaskDynamicsSettings`. La portance motorisée aide les conversions M.A.S.K. ; ce modèle ne simule pas complètement profils d'ailes, décrochage, vent, rotor ou consommation énergétique. Les collisions restent actives et peuvent empêcher une manœuvre. Les actifs artistiques sont réutilisés sans modification.

## Validation

La sonde `MASK.DynamicsSmoke`, lancée par `Tools/Migration/Test-Dynamics.ps1`, utilise les vrais véhicules et des événements Xbox injectés. Une plateforme répliquée isolée au-dessus de la carte sert de terrain d'essai ; aucune carte persistante n'est modifiée. Les mesures de freinage utilisent explicitement deux vitesses initiales imposées. La branche de descente hors portée est testée en altitude, puis une seconde condition initiale plus basse borne la durée de l'approche : aucun vol continu de 600 m de descente n'est revendiqué.

Les tests couvrent transformation pendant l'accélération, décollage autonome, inclinaison et trajectoire de virage, vitesse minimale sous frein, atterrissage/repli sans descente manuelle, conservation du mouvement, énergie et distance de freinage, éjection/rappel réels de Rhino depuis les deux postes et profil hélicoptère. Le réseau vérifie les mêmes transitions sur l'autorité et sur le client, sans placement artificiel au point d'amarrage.

## Ouvrir et jouer

Lancer `Jouer-MASK.cmd` à la racine du dépôt Unreal, puis **Menu** pour le solo contre trois bots. **X** dans le menu principal sélectionne le véhicule. En partie : **RT/LT** pour accélérer/freiner, **X** pour transformer ou demander l'atterrissage, **stick gauche** pour diriger/cabrer/piquer, **stick droit** pour la caméra. **Croix haut/bas** échange le véhicule avec une IA. Depuis le module Rhino, **X** reprend le camion et réattache le module. Les commandes sont aussi dans la pause (**Menu**) et [XBOX_CONTROLS.md](XBOX_CONTROLS.md).

Pour régler un futur véhicule, éditer sa `UMaskVehicleDefinition` : `bSupportsFlight`, `Dynamics.FlightModel`, vitesses en m/s, puissance en kW, poussée en N, hauteur de décollage et angles limites. Le type avion conserve la vitesse minimale ; le type hélicoptère accepte zéro. Les transformations continuent d'utiliser les pièces et durées propres à chaque définition.

## Résultats vérifiés

Distribution finale : `Saved/Packages/MASK-Dynamics-Development-r2/Windows`, **Win64 Development, UE 5.8.2**. Compilation Editor réussie ; compilation des Blueprints : 0 erreur, 0 avertissement, 0 échec de chargement. BuildCookRun r2 réussi en 95,71 s. Le lanceur pointe vers cette version ; les anciennes distributions sont conservées. Empreinte de l'exécutable : [package.json](validation/dynamics/package.json).

| Essai sur la distribution r2 | Résultat |
|---|---|
| Dynamique solo, avec profil hélicoptère de substitution | [29/29](validation/dynamics/packaged-solo.json), sortie 0 |
| Réseau, serveur listen et client séparé | [7 hôte + 22 client](validation/dynamics/packaged-network.json), deux sorties 0 |
| Commandes Xbox, Thunderhawk, tir, caméra, menus | [32/32](validation/dynamics/packaged-xbox.json), sortie 0 |
| Hurricane, transformation en mouvement, six roues, tir et roue éjectable | [23/23](validation/dynamics/packaged-hurricane.json), sortie 0 |

Les événements de manette sont injectés dans le vrai jeu ; aucun essai physique d'une manette n'est revendiqué. Le réseau utilise une connexion directe locale entre deux processus ; le parcours des boutons Host/Join conserve sa validation du 7 novembre et n'est pas recompté ici. Les transformations réseau de Rhino n'utilisent aucun placement au point d'amarrage. Les captures de roulis, retour au sol, module réattaché et Hurricane ont été inspectées ; elles complètent les mesures physiques sans remplacer une appréciation manuelle du pilotage.

Freinage sur le terrain d'essai : **8,17 m à 10 m/s**, **32,31 m à 20 m/s**, avec le même véhicule et les mêmes freins. Le rapport d'énergie vaut 4. Les valeurs sont des mesures du prototype, pas des distances garanties sur chaque revêtement.

Les premiers échecs, les corrections et les limites des sondes sont conservés dans [MIGRATION_LOG.md](MIGRATION_LOG.md) et [failed-runs.json](validation/dynamics/failed-runs.json). Les suites Editor corrigées passent également. Toutes les instances de jeu/éditeur lancées pour ces essais sont fermées. Aucun fichier `.blend`, `.uasset` ou `.umap` modifié. Liste exhaustive des fichiers de cette livraison : [DYNAMICS_FILES.md](DYNAMICS_FILES.md).

Pour reproduire les essais depuis le dépôt :

```powershell
$maskExe = (Resolve-Path 'Saved/Packages/MASK-Dynamics-Development-r2/Windows/VehicularCombat/Binaries/Win64/VehicularCombat.exe').Path
& Tools/Migration/Test-Dynamics.ps1 -RunName new-solo -Render -GameExecutable $maskExe
& Tools/Migration/Test-Dynamics.ps1 -RunName new-network -Network -Render -GameExecutable $maskExe
& Tools/Migration/Test-Thunderhawk.ps1 -RunName new-xbox -Xbox -Render -GameExecutable $maskExe
& Tools/Migration/Test-Hurricane.ps1 -RunName new-hurricane -Render -GameExecutable $maskExe
```

Choisir de nouveaux noms à chaque passe : les rapports existants ne sont pas écrasés.
