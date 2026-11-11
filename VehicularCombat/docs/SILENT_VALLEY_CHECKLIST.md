# Silent Valley — checklist de reprise

Demande du 8 novembre 2026. Source principale : prompt utilisateur complet et `../docs/Spécifications missions/MASK_Mission_01_Silent_Valley_Spec_v1.md` depuis la racine du dépôt Unreal (le fichier se trouve dans le dossier parent `mask-project-mayhem/docs`).

## Reprendre ici

### Reprise du 9 novembre — bugs de maniabilité prioritaires

Réglages sol/vol et motricité renforcés, marche 240 cm/s. Les TROIS boucles de 9548 m passent après changement physique ; pente 10° et demi-tour au sol passent pour les trois véhicules ; vol à 300 km/h et transformations passent. Voir [rapport de maniabilité](tests/HANDLING_TEST_REPORT.md).

Défaut à pied reproduit après saut à Pinewood : maintien en mode Falling, glissade et remontée refusée. Correction par réacquisition d'un sol praticable dans la distance de contact normale, via CharacterMovement ; les TROIS véhicules passent marche prolongée, saut/atterrissage et retour réel dans le même véhicule. Régression solo de tous les conducteurs et régression réseau à pied hôte/client réussies (cette dernière sur la plateforme historique, pas une mission coop Silent Valley). Aucun changement des assets/maps/sources Blender. Modifications C++/scripts non committées sur la branche existante ; conserver les Fab et matériaux non suivis.

G2 manuel/carrière/limites demeure partiel. Ne pas confondre les tests automatisés de conduite/locomotion et une validation artistique ou de coop de mission.

Branche `feature/silent-valley-mission-01`. Checkpoint route/retour : `49095be` ; lot suivant : première couche PCG et limites de prototype. Voir historique Git pour le dernier commit exact. Projet original, trois véhicules, sources Blender et `Content/Fab/` utilisateur préservés.

### Vérifié à la fin du lot

- Build Editor 17 réussi. Dix captures `views-showcase-r3`, toutes ouvertes, 1600×900 réels, copiées sous `docs/validation/silent-valley/views-showcase-r3`.
- `create-10` : route 9550,66 m. Retour r3 des TROIS véhicules : 9548 m, écarts 0,84–1,20 m, zéro intervalle sans contact roue. Rapports et deux échecs antérieurs conservés sous docs.
- G3 technique : vrai graphe PCG, 39 rochers sur 500–1000 m, sans collision, exclusions route/spawns/checkpoints précalculées (8,8 m depuis la rive au minimum). Nettoyage puis régénération et réouverture indépendante vérifiés, matériau adapté aux instances effectivement persistant. Copies de matériaux sous MASK ; import Fab inchangé.
- Matériau de sol v2 conservé après inspection ; v1 trop contrasté reste local inutilisé. Les deux assets inutilisés `M_SV_RoadMarked_v1` et `M_SV_ValleySurface_v1` restent hors commit, comme le Fab utilisateur.
- Treize sondes de collision des limites après sauvegarde/réouverture passent. Colliders invisibles en bord de Landscape et plafond à 1995 m ; réponse d'un avion contre eux NON TESTÉE.
- Régression Rhino `showcase-r1 -FullRoute` après décor/limites : sortie 0, 9548 m, 1186,13 s simulées, écart 0,84 m, zéro intervalle sans contact roue.
- Profil rendu r3 : 900 trames après 300 écartées, ~11,35 s, moyenne 12,61 ms/79,3 FPS, P95 13,49 ms, pic 1044,4 ms conservé. Échantillon de galerie, pas benchmark de conduite ni garantie 60 FPS finale. JSON sans métadonnées de compte sous docs.
- Aucun processus Unreal automatique restant. Deux lanceurs pratiques ajoutés pour Rhino et Hurricane ; défaut Thunderhawk avec `Jouer-SilentValley-Editor.cmd`. Contrôles Xbox inchangés.

### Prochaine action

1. G2 reste partiel : conduite manuelle rapide, virages/retournements, plusieurs véhicules dans la carrière et réaction aux limites ne sont pas validés.
2. G3 artistique reste NON VALIDÉ : relief trop artificiel en périphérie, panneaux vus de dos, Boulder Hill trop sombre le soir, pas de pins/herbe/falaises finales. Garder la zone de 500 m et corriger avant toute extension massive.
3. Fiches Fab exactes et limites des ressources présélectionnées dans `ASSET_MANIFEST.md`. Aucun achat, contrat accepté ou nouvelle acquisition ; ne pas activer PVE/Nanite Foliage expérimental pour la fiche Baltic Pine. Propriété/licence du rocher local encore à documenter précisément avant publication.
4. Ensuite G4 : états de mission, objectifs/HUD, adversaire en carrière, récupération/extraction, autorité serveur et récompense locale. La V0 est implémentée ; sa validation complète reste en cours (docs/missions/MSN_SILENT_VALLEY_01.md). Coop, streaming et package Silent Valley restent NON TESTÉS.

### Reproduction / pièges déjà résolus

- Générateur de map : `Tools/Art/build_silent_valley.py` dans UnrealEditor-Cmd, sauvegarde automatique de la map précédente dans Saved.
- Sol : `build_silent_valley_surface.py`, commandlet Python. Bruit : broche `World Position` dans cette API.
- PCG : `UnrealEditor -ExecCmds="py <chemin absolu>/build_silent_valley_showcase.py"`. Ne pas utiliser `-ExecutePythonScript` : il quitte avant la fin des tâches. Désinscrire le callback Slate avant sauvegarde ; nettoyer les anciennes instances avant de valider nombre ET matériau.
- Validation : `validate_silent_valley_showcase.py` dans un autre processus ; `bound_silent_valley.py` recharge le niveau après sauvegarde avant rayons, pour enregistrer les nouveaux corps de collision.
- Rendu/profil : `Capture-SilentValley.ps1 -RunName <inédit> -Profile`, puis `Summarize-SilentValley-Profile.py`. R1 était en 888×500 ; seules les passes suivantes forcent réellement 1600×900.
- Logs complets sous `Saved/SilentValley`, données CSV natives sous Saved/Profiling/CSV. Copies de preuves utiles sous docs. Avertissement LogGrass de maps encore en attente à la fermeture : à revoir avant vraie végétation. Ne pas arrêter une instance utilisateur ; gérer seulement les lancements automatiques `-unattended`.

## Contraintes permanentes

- [x] Créer cette checklist persistante avant la production.
- [ ] Préserver les trois véhicules, leurs conducteurs/masques, gameplay, maps, sources Blender et changements locaux.
- [x] Branche `feature/silent-valley-mission-01` créée sans écraser les changements présents ; commits de validation à poursuivre.
- [ ] Budget 0 €, aucun achat/contrat accepté, aucun nouveau logiciel/MCP installé ; ne pas utiliser/réparer Bridge.
- [ ] Utiliser de vrais assets Unreal sauvegardés par l'éditeur ; aucun faux `.umap`/`.uasset` textuel.
- [ ] Actualiser cette checklist, les chemins, commandes, blocages et prochaine action avant chaque interruption/fin de lot.

## G0 — audit ciblé

- [x] Lire AGENTS.md applicables, spécification locale et workflow d'assets pertinent.
- [x] Confirmer Git, UE 5.8.2, RTX 4060 Ti 16 Go, RAM 32 Go, espace libre et outils.
- [x] Vérifier plugins PCG/Python/Editor Scripting/Modeling montés et APIs PCG/GeometryScript présentes.
- [x] Identifier classes/assets des trois véhicules, spawn, contrôleurs, HUD, IA, armes/dégâts et réseau existants.
- [x] Inspecter maps et source Boulder Hill par MCP ; rocher Fab local identifié, chargement direct/API à confirmer (la première requête AssetRegistry renvoie encore une liste vide).
- [x] Créer `docs/SILENT_VALLEY_IMPLEMENTATION_PLAN.md` et `docs/ASSET_MANIFEST.md` avec risques/provenances/statuts.

## G1 — carte pilote, priorité absolue

- [x] Nouvelle carte réelle `Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap`, créée/sauvegardée par Unreal Editor.
- [x] Landscape réel 4032 m, 256 composants, relief et raccords générés ; décision de prototype sans World Partition documentée (streaming NON TESTÉ).
- [x] Boulder Hill V6 importé à l'échelle cm, source originale préservée ; garage ouvert statique (animation runtime NON TESTÉE/non implémentée).
- [ ] Route continue Boulder Hill → Pinewood Road → Eagle Pass → Old Quarry → North Ridge ; bouclage/retour, deux retournements et raccourci terre si réalisable.
- [ ] Chaussée à deux voies par splines, collisions fiables ; mesurer gabarits des véhicules réels.
- [ ] Spawns de base, repères/checkpoints et extraction temporaire.
- [x] Parcours physique des trois véhicules de la base aux cinq lieux jusqu'au ridge : G2-r3, ~5969 m, sans téléportation, rapports conservés. Contrôles Xbox automatisés, pas essai manuel.
- [x] Point de contrôle Git G1 après vérification réelle (b3235d7 puis 49095be).

## G2 — collisions et pilotage

- [ ] Mesurer largeurs, rayons, pentes, raccords, dévers et dégagement de la sortie.
- [ ] Tester les trois véhicules, contacts de roues, non-chute, limites, retournement et carrière à plusieurs véhicules.
- [ ] Corriger avant décoration massive ; conserver tests reproductibles et états VÉRIFIÉ/NON TESTÉ/BLOQUÉ.

## G3 — environnement, tronçon vitrine ~500 m

- [ ] Réutiliser rocher Fab/Megascans importé et matériaux adaptés ; consigner source/licence visible/statut gratuit réel.
- [ ] Chercher uniquement des ressources précises pertinentes ; acquisition manuelle si contrat/compte requis, continuer avec placeholders explicites.
- [ ] Matériau Landscape, chaussée, rochers/falaises, pins/herbe, signalisation, lumière de jour et golden hour.
- [ ] PCG non destructif avec exclusions routes/base/spawns/arènes, après G1/G2 validés.
- [ ] Mesurer FPS/frame time/mémoire/instances et régler densités/ombres/Lumen/Nanite selon matériel réel.
- [ ] Étendre progressivement seulement après validation du tronçon.

## G4 — mission et combat

- [ ] Auditer puis réutiliser l'architecture existante ; états et données de mission ajoutés proprement.
- [ ] Briefing → départ → parcours → reconnaissance → interception → combat carrière → récupération → extraction → succès/échec.
- [ ] Déclenchements idempotents et autorité serveur ; HUD compatible et IA/armes/dégâts existants.
- [ ] Règles de convoi, récupération si bloqué/renversé, retry propre et déconnexion coop.
- [ ] Récompense locale `TechComponents`, une attribution par exécution, progression sauvegardée.
- [ ] Tests réels de chaque étape, échec, reprise et rejouabilité.

## G5 — validation et livraison

- [ ] Captures in-engine des cinq lieux, jour et golden hour ; comparaison blockout/habillage.
- [ ] Compiler Editor, charger/sauvegarder la nouvelle map, vérifier Blueprints/assets/PCG.
- [ ] Deux instances coop si possible : spawn, phases, dégâts, récompenses et déconnexion.
- [ ] Distribution Windows et lanceur de mission préservant l'accès au jeu existant.
- [ ] `docs/tests/SILENT_VALLEY_TEST_REPORT.md` : statuts par jalon, commandes/logs, performances mesurées, captures et limites.
- [ ] `docs/levels/SILENT_VALLEY_MAP.md`, `docs/missions/MSN_SILENT_VALLEY_01.md`, manifeste des assets et liste des fichiers modifiés.
- [ ] Commit(s) vérifiés, état Git final et procédure précise pour jouer.

## Journal de reprise

### Lot 00 — initialisation

Checklist créée. Aucun niveau, asset, gameplay ou plugin modifié. Audit détaillé à poursuivre.

### Lot 01 — audit et début G1

Scripts : `Tools/Art/audit_silent_valley.py`, `inspect_boulder_for_unreal.py`, `export_boulder_for_unreal.py`, `build_silent_valley.py`. Rapports et logs : `Saved/SilentValley/`. Compilation 01 : erreur de déduction `auto*` sur une liste TObjectPtr, corrigée ; compilation 02 VÉRIFIÉE. Premier audit Python : accès aux champs des structs par `get_editor_property` corrigé, audit 02 terminé.

Boulder Hill : source originale V6 indépendante inspectée à la frame 211 (garage ouvert). Dérivé éditable et FBX réel sous `SourceArt/MASK/BoulderHill/`, source originale inchangée et session Blender restaurée. Exclure `BH_DesertGround` du niveau (c'est un plan de studio de 2 km). Les deux premiers exports ont rencontré un contexte Blender sans selected_objects ; combinaison par données et export de la scène isolée résolvent le problème. Manifest précise la pose statique, sans prétendre que la transformation est déjà animée dans Unreal.

La création de carte s'exécute avec UnrealEditor-Cmd (vrai éditeur), `-run=pythonscript -script=<absolu>/Tools/Art/build_silent_valley.py -NullRHI -Unattended`. Le script sauvegarde une copie d'une map générée existante avant reprise, réutilise les acteurs nommés et ne touche pas aux cartes précédentes. Session de commande en cours au moment de cette note : 27412 ; vérifier fichiers/logs/processus avant toute relance après interruption. Aucun succès de conduite revendiqué à ce stade.

### Lot 02 — carte géométrique et erreurs découvertes avant conduite

`create-01` a produit la vraie map de ~15 Mo, Landscape 4032 m, 438 segments de route et 27 acteurs, mais une duplication GameMode avait échoué (asset absent de l'AssetRegistry initial) : **G1 NON TESTÉ**, ne pas annoncer la carte jouable. La vérification a trouvé cette erreur dans les logs malgré le retour global 0. `probe_silent_valley_assets.py` confirme que le scan synchrone complet permet de charger le vrai GameMode, le contrôleur et le rocher Fab ; résultat `asset-resolution.json`.

Corrections ajoutées : route ouverte avec raccord de retour extérieur (ne pas boucler à travers la paroi du garage) ; altitudes du col/carrière/ridge réduites et plateau de retournement ; terrain mis à jour par LandscapeEdit, uniquement sur le Landscape marqué SV_GENERATED de la nouvelle map après sauvegarde. Nouveau mesh Boulder Hill v2 avec UV planaires, originaux et v1 préservés ; quelques tangentes proches de zéro subsistent à investiguer avant validation visuelle. Modules éditeur Landscape/Foliage ajoutés, uniquement build Editor. Compilation 03 réussie ; 04 manquait Foliage pour LandscapeEdit ; 05 réussie. La dernière modification de la sonde (refus si véhicule absent) reste à recompiler.

`create-02` utilise encore l'ancienne fonction d'affectation matériau slot par slot, coûteuse en reconstructions de mesh. Le script sur disque est corrigé pour affecter tous les slots en une fois lors de la prochaine exécution. Ne pas lancer deux mutations concurrentes de cette map. La sonde PowerShell refuse désormais un GameMode absent plutôt que de patienter sans véhicule. Aucun test physique de trajet n'a encore été exécuté ; aucun plugin, téléchargement ou achat ajouté.

### Lot 03 — GameMode résolu et premiers passages physiques

`create-03` et `create-04` : vrais assets sauvegardés et Blueprint GameMode dérivé correct après scan AssetRegistry complet/chargement direct. Route totale mesurée ~8858 m, incluant le retour extérieur ; 441 spline meshes. La route principale jusqu'à North Ridge est à mesurer séparément. Compilations Editor 06/07 réussies.

`g1-r2` (NullRHI accéléré) et `g1-r3` (rendu réel) **ÉCHECS** : véhicule présent, 2658 traces de sol sans trou, pente maximale 6,51 %, mais départ face à une armoire du garage et progression bloquée à 0 m. Aucun passage complet revendiqué. Captures réelles sous `drive-g1-r3-Thunderhawk/departure-*.png`. Diagnostic read-only `route-transforms.json` : tangent de spline nul exactement à 0 cm ; surtout le constructeur Python Rotator positionnel transforme les angles au mauvais axe. Tous les Rotator sont maintenant construits par mots-clés, le départ prend la direction à 1 cm et la reprise repositionne les acteurs générés. `create-05` sauvegarde ces corrections après copie de la map précédente ; essai `g1-r4` à lire ensuite.

La sonde native `MASK.SilentValleyDrive` commande les axes Xbox sur le vrai véhicule Chaos ; aucun déplacement cinématique ni téléportation. Son mode `-Fast` utilise un pas fixe de 1/60 s pour accélérer les essais sans changer la physique. Le rapport distingue temps simulé/réel, trajectoire, contacts, traces et états. Ne pas confondre une map sauvegardée avec un parcours jouable. Les véhicules et cartes historiques n'ont pas été modifiés.

### Lot 04 — parcours effectif et critères G2 renforcés

`g1-r5` : Thunderhawk atteint les cinq lieux sans téléportation en 435,79 s simulées, 5,867 km ; Hurricane en 459,28 s. Aucun intervalle sans contact de roue. **Cela ne valide pas le maintien sur chaussée** : écarts max 11,02 m et 12,11 m, tolérance initiale trop large 13 m. Rhino échoue à 3482 m (Eagle Pass), écart 13 m. Échecs/réussites brutes conservés, rapport de tests explicite cette limite. La sonde corrige la zone morte Xbox 25 %, puis utilise désormais un lookahead 4,5–8 m, vitesse 10,8–36 km/h suivant virage et écart max 3,2 m. Aucun changement de physique des véhicules.

La surface routière était masquée par le Landscape par endroits (quantification/interpolation) : terrain sous le tracé abaissé de 45 cm avec transition d'accotement. À vérifier en image et contact après `create-06`. `probe_silent_valley_surfaces.py` confirme que les 441 spline meshes sont sauvegardés, visibles et portent le matériau asphalte, mais sa première présentation des traces Python ne fournit pas encore une identité de surface exploitable.

G2-r1 Rhino échoue avant Eagle Pass : Pinewood 714 m, 3,24 m d'écart. La spline `CurveClamped` pouvait créer un tangent nul à un extrême et un angle presque vif, incompatible avec le rayon du camion. `Curve` remplace ce réglage, map/terrain reconstruits en create-07, compilation 10 réussie. Essai G2-r2 en cours ; ne pas annoncer sa réussite avant lecture du rapport complet. Les rapports bruts historiques sont copiés sous `docs/validation/silent-valley/driving/`.

G2-r2 atteint les cinq lieux avec Rhino mais échoue au contrôle de pente (14,65 %) : tangentes verticales automatiques dépassent les altitudes près des petits plateaux. La correction conserve les courbes horizontales et fixe les tangentes verticales à zéro aux nœuds. Compilation 11, create-08 puis G2-r3 : **trois succès réels** ; Rhino 775,69 s simulées / écart 0,84 m, Thunderhawk 753,86 s / 1,22 m, Hurricane 811,58 s / 1,18 m. Aucun intervalle sans contact roue ; pente max 8,47 %, 2712 traces de sol sans trou. La sonde indépendante identifie réellement les SplineMeshComponents de la route aux six échantillons. La vérification visuelle reste séparée : captures de la nouvelle version en cours, pas encore inspectées.

Point de contrôle audit : `144ffd8`. Nouveau lanceur **Editor seulement** `Jouer-SilentValley-Editor.cmd [Thunderhawk|Rhino|Hurricane]` ; ne touche pas à `Jouer-MASK.cmd` et n'annonce pas un package de mission. Rapport en cours `docs/tests/SILENT_VALLEY_TEST_REPORT.md`. G3/PCG, mission complète, coop, package et performance restent NON TESTÉS/non livrés. Aucun nouveau téléchargement, achat ou changement des véhicules/cartes historiques.

### Lot suivant — lisibilité et mission V0

Matériau Landscape v4, panneaux recto/verso sur dix poteaux, skylight et fill enregistrés. Réouverture indépendante : matériau, route 9550,66 m, 39 instances PCG et panneaux passent. Dix captures jour/soir de readability-r3 inspectées ; v3 trop granuleuse conservée. Le terrain reste un blockout : parois artificielles, sol uniforme et absence de végétation. G3 artistique toujours incomplet. Route Rhino après première passe v3 : 9548 m, écart 0,923 m, aucun intervalle sans contact roue. V4 ne modifie ni relief ni collision.

Mission V0 ajoutée, escorte existante en attente à la carrière, récupération/extraction et récompense locale implémentées. Convoi mobile et coop de mission restent hors validation. Résultats effectifs dans docs/tests/SILENT_VALLEY_SLICE_REPORT.md. Les anciennes cases non cochées ne constituent pas une preuve d'absence du code actuel.
