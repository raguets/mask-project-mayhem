# Conducteurs jouables à pied

8 novembre 2026 — branche `feature/on-foot-drivers`, depuis `06ceb0a`. UE 5.8.2 installé, aucun logiciel ajouté. Le bouton de saut du véhicule devient la sortie du conducteur. Les commandes complètes sont dans [XBOX_CONTROLS.md](XBOX_CONTROLS.md) et dans la pause du jeu.

## Utilisation

Lancer `Jouer-MASK.cmd`, choisir le véhicule avec X dans le menu principal, puis Menu pour le solo avec bots. Arrêter le véhicule au sol ; A fait sortir son conducteur si un côté est libre. Stick gauche : marcher ; maintenir L3 : courir ; stick droit : regarder/viser ; A : sauter ; Y : masque ; RT ou RB : fusil ; X près de son véhicule : remonter. Menu ouvre l'aide et la pause. En réseau, le monde continue pendant la pause locale.

La sortie est refusée en mouvement, en vol, pendant une transformation, sur un véhicule renversé ou sans emplacement sûr. Les seuils d'arrêt sont 15 cm/s et 0,2 rad/s. Le serveur vérifie les contacts des roues, la pente, l'altitude du sol latéral par rapport aux contacts des pneus et la place pour une capsule de 34 × 88 cm. Il essaie les deux côtés près de la cabine, puis deux positions plus éloignées. La remontée exige un véhicule sain et libre, le conducteur d'origine au sol et une distance réelle inférieure à 4 m.

Le véhicule quitté reste garé et réservé, sans IA qui s'en empare. Les changements par croix haut/bas reprennent une fois remonté. Le rappel du module Rhino est bloqué lorsqu'un des deux conducteurs est à pied.

## Même personnage dans les deux états

`AMaskDriverCharacter` existe déjà à l'intérieur du véhicule. Il possède le corps, les cheveux et le masque ; le véhicule réutilise ces composants pour ses références de pilote et ses poses. La sortie détache et possède cet acteur, puis la remontée rattache le même acteur. Aucun corps supplémentaire pour les variantes masquées ou les poses assises/debout.

Matt/Spectrum, Alex/Jackrabbit, Bruce/Lifter et Hondo/Blaster utilisent leurs meshes et squelettes existants. La berline de démonstration utilise Matt comme conducteur par défaut de prototype. Le corps d'un conducteur déjà dehors survit à la destruction de son véhicule. La santé à pied est de 100 ; une mort ramène après trois secondes au véhicule d'origine s'il est encore disponible, sinon le GameMode réapparaît avec la classe de véhicule mémorisée.

`CharacterMovement` assure déplacement, collision, gravité, saut et réplication. Marche : 150 cm/s ; course : 400 cm/s. Le BlendSpace natif mélange repos et huit directions de marche/course ; un clip de saut est mélangé pendant la chute. Les FBX d'animation seuls réutilisent les quatre squelettes. Les sources éditables et les actions d'origine sont conservées sous [SourceArt/MASK/OnFoot](../SourceArt/MASK/OnFoot/README.md), les sources artistiques antérieures restent intactes.

Le fusil d'assaut et ses projectiles/effets sont ceux du projet original. Le serveur contrôle cadence, munitions, rechargement automatique et dégâts. Les projectiles clients restent cosmétiques ; ils ne causent pas de dégâts. La capsule du conducteur bloque les balles et la visibilité, contrairement au profil Pawn historique qui les ignorait. Les filtres de dégâts alliés prennent aussi en compte les conducteurs ; les bots peuvent viser un joueur à pied et suivre un allié à pied.

## Validation enregistrée

- Compilation Editor, dernière passe 11 : réussite ; erreurs intermédiaires et journaux dans `Saved/Migration/onfoot-build-*`.
- Import : 72 animations, quatre BlendSpaces et quatre définitions mises à jour ; rapport `Saved/Art/onfoot/import.json`.
- Blender MCP : 20 rendus inspectables, repos avec/sans masque, marche/course/saut pour les quatre conducteurs. Les meshes et les sources d'origine ne sont pas modifiés.
- Solo Editor `editor-r3` : contrôles de sortie refusée en mouvement et sur côtés bloqués, même acteur/corps, marche/course/saut, caméra, masque, tir/dégâts, remontée, seconde sortie, pause, balle hostile/capsule, dégâts alliés, mort/réapparition. Sortie/remontée avec Rhino et Hurricane en route et en combat, Bruce dans le module détaché et la berline d'origine.
- Deux instances Editor `network-editor-r1` : sortie, marche/course/saut, masque et tir répliqués ; dégâts réellement appliqués sur l'hôte et retour au même véhicule contrôlés côté autorité. Deux sorties de processus à 0.
- CompileAllBlueprints : 0 erreur, 0 avertissement, 0 échec de chargement. DataValidation : succès. Les assets Fab locaux de l'utilisateur ont aussi été examinés par ces commandes, préservés et exclus des changements de cette fonctionnalité.

Distribution livrée : `Saved/Packages/MASK-OnFoot-Development-r2/Windows`. `Jouer-MASK.cmd` pointe vers cette version. BuildCookRun termine avec le code 0. Après une reprise automatique de copie faute de place, les 50 fichiers archivés sont vérifiés par longueur et SHA-256 contre le staging : [intégrité complète](validation/onfoot/archive-integrity.json). La compression NTFS sans perte des fichiers de compilation a libéré de l'espace ; aucun fichier source, asset ou ancien paquet n'a été supprimé.

| Essai sur l'exécutable Windows r2 | Résultat |
|---|---|
| Conducteurs à pied et six cas de véhicule/état | [40/40](validation/onfoot/packaged-solo.json), sortie 0 |
| Deux instances : hôte et client | [10/10 hôte](validation/onfoot/packaged-host.json), [20/20 client](validation/onfoot/packaged-client.json), deux sorties 0 |
| Dynamique route/air, 50 → 300 → 50 km/h, rappel Rhino, profil hélicoptère | [35/35](validation/onfoot/packaged-dynamics.json), sortie 0 |
| Flotte, personnages, armes, échange de véhicules, module allié | [41/41](validation/onfoot/packaged-fleet.json), sortie 0 |
| Hurricane et stabilité des roues | [23/23](validation/onfoot/packaged-hurricane.json), sortie 0 |
| Commandes Xbox, caméras, armes et menus | [32/32](validation/onfoot/packaged-xbox.json), sortie 0 |

Les sondes utilisent une plateforme temporaire à 200 m et des événements Xbox injectés. Les placements de véhicules, obstacles et arme hostile sont des fixtures explicites ; aucun asset de carte n'est remplacé pour faciliter les essais. Une manette XInput est détectée à l'emplacement 0 le 8 novembre ; aucun essai physique de ses boutons n'est revendiqué. Les captures de [Matt démasqué](validation/onfoot/foot-face.png), [Alex](validation/onfoot/roster-0.png), [Bruce](validation/onfoot/roster-1.png) et [Hondo](validation/onfoot/roster-2.png) ont été inspectées. Le contrôle de sol compare les géométries Blender et les poses Unreal : mêmes racines à l'origine, chevilles à 11,5 cm et semelles à environ 0,5 cm dans l'espace du mesh ; la marge de collision au sol de CharacterMovement demeure. Voir les rapports [Blender](validation/onfoot/ground-blender.json) et [Unreal](validation/onfoot/ground-unreal.json).

Commandes reproductibles, depuis le dépôt, avec `$exe` pointant sur l'exécutable r2 :

```powershell
Tools/Migration/Invoke-UE58.ps1 -Task Build
Tools/Migration/Invoke-UE58.ps1 -Task Blueprints
Tools/Migration/Invoke-UE58.ps1 -Task Assets
Tools/Migration/Package-Windows.ps1 -RunName MASK-OnFoot-Development-r2
Tools/Migration/Test-OnFoot.ps1 -RunName packaged-r2 -Render -GameExecutable $exe
Tools/Migration/Test-OnFoot.ps1 -RunName network-packaged-r2 -Network -Render -GameExecutable $exe
Tools/Migration/Test-Dynamics.ps1 -RunName onfoot-packaged-r2 -Render -GameExecutable $exe
Tools/Migration/Test-Fleet.ps1 -RunName onfoot-packaged-r2 -Render -GameExecutable $exe
Tools/Migration/Test-Hurricane.ps1 -RunName onfoot-packaged-r2 -Render -GameExecutable $exe
Tools/Migration/Test-Thunderhawk.ps1 -RunName onfoot-xbox-packaged-r2 -Render -Xbox -GameExecutable $exe
```

Choisir des noms de run inédits pour réexécuter : les scripts refusent d'écraser les précédents rapports/paquets. Commandes complètes avec arguments réellement lancés et journaux conservés sous `Saved/Migration`, `Saved/Art` et dans les fichiers `launch.json` des runs. [Liste des fichiers changés](validation/onfoot/changed-files.txt).

## Limites

La sortie/entrée est immédiate, sans animation de porte. Le rig actuel à 17 os n'articule pas les doigts : la prise du fusil reste approximative. Pas encore d'IK des pieds sur terrain accidenté, d'animation dédiée de rechargement, de mort, de pouvoirs des masques ou de prise d'un autre véhicule en marchant. Les animations sont des interprétations génériques, sans mocap ; leur présence ne prouve pas un réalisme photographique. Les contrôles réseau sont locaux sur une machine, sans simulation de latence WAN.

Les avertissements UE/MSVC et RawInput déjà connus restent visibles. Les nouveaux accès à la fréquence réseau utilisent les accesseurs UE 5.8 ; les avertissements C4996 des en-têtes moteur ne sont pas masqués.
