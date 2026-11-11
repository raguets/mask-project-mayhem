# Silent Valley — rapport de validation en cours

Ce rapport ne constitue pas une livraison finale de mission. Voir la [checklist de reprise](../SILENT_VALLEY_CHECKLIST.md).

## Premier lot G3 et limites de prototype

VÉRIFIÉ : compilation Editor 17 réussie (44,57 s). Graphe PCG réel `PCG_SV_PinewoodRocks_v1`, 39 rochers sur 500 m, nombre inchangé après nettoyage/régénération. Réouverture indépendante r4 : 39 instances persistantes, utilisables en jeu, sans collision, matériau isolé adapté aux instances, route de 9550,66 m inchangée et matériau de terrain v2 assigné. Dégagement conservateur minimal entre les rochers et la rive : 8,8 m. Les exclusions sont précalculées par script depuis toute la route et les spawns/checkpoints ; elles ne sont pas encore un filtre spline dynamique du graphe.

VÉRIFIÉ : treize rayons contre les quatre limites périphériques et le plafond, après sauvegarde/réouverture. Limites invisibles de prototype à ±2011 m, plafond 1995 m. Les rayons prouvent les collisions, pas la réponse manuelle des véhicules/avions contre les limites.

Régression après ajout de PCG, sol v2 et limites : Rhino `showcase-r1 -FullRoute` VÉRIFIÉ, sortie 0, 9548 m, 1186,13 s simulées, écart 0,84 m, zéro intervalle sans contact roue. Les limites étant invisibles et hors du parcours/cadrage, les captures prises juste avant leur ajout restent une preuve du décor affiché, pas de leur fonctionnement physique.

Les dix PNG `views-showcase-r3` ont été ouverts : cinq lieux, jour et golden hour, **1600×900 réels**. Rocher texturé visible à Pinewood. Le contraste excessif du sol v1 a été réduit dans v2 ; les matériaux Fab des anciennes instances ont été remplacés par leurs copies adaptées après détection du fallback. Le relief macro reste artificiel, les panneaux sont souvent vus de dos et le soir est trop sombre à Boulder Hill. Pas de pins, herbe ou falaises finales : **G3 artistique non validé**.

Profil diagnostique rendu : i7-4770, 32 Go RAM, RTX 4060 Ti 16 Go, Windows 11, UE 5.8.2 Development Editor `-game`, 1600×900, qualités interrogées à 3, VSync 0, t.MaxFPS 0, aucun pas fixe. Sur 900 trames après exclusion des 300 premières : moyenne **12,61 ms / 79,3 FPS**, médiane 11,12 ms, P95 13,49 ms, maximum **1044,4 ms**. Le pic est conservé ; captures, transitions de caméra et streaming peuvent contribuer, cause non isolée. Ce court intervalle (~11,35 s) n'est ni un benchmark de conduite ni une garantie de 60 FPS pour la mission entière. L'occupation VRAM figure dans le JSON de profil ; aucun réglage Lumen/Nanite global n'a été modifié. R1 était en 888×500 et ne permet pas une comparaison directe de performance avec r3.

Commandes : `build_silent_valley_surface.py` via Python commandlet ; `build_silent_valley_showcase.py` via `UnrealEditor -ExecCmds="py <chemin absolu>"` ; `validate_silent_valley_showcase.py` via commandlet ; `Capture-SilentValley.ps1 -RunName showcase-r3 -Profile` ; `bound_silent_valley.py` via commandlet. Logs sous `Saved/SilentValley/`, CSV natif sous `Saved/Profiling/CSV`. Les résumés publiés excluent les métadonnées de compte présentes dans le CSV natif.

Preuves conservées : [génération PCG](../validation/silent-valley/showcase-01/generation.json), [réouverture indépendante](../validation/silent-valley/showcase-01/reload.json), [profil](../validation/silent-valley/showcase-01/profile.json), [limites](../validation/silent-valley/showcase-01/boundary-probes.json), [conduite Rhino après décor](../validation/silent-valley/driving/showcase-r1-Rhino.json), [Pinewood jour](../validation/silent-valley/views-showcase-r3/day-zone-1.png). Les dix images sont dans ce même dossier de captures.

Corrections d'automatisation : nom de broche Noise `World Position` ; `-ExecutePythonScript` quitte avant la fin des tâches PCG, remplacé par `ExecCmds py` ; désinscription du callback Slate avant sauvegarde pour éviter une sauvegarde réentrante ; nettoyage des anciennes instances avant validation du nouveau matériau ; rechargement du niveau avant sondes des nouveaux corps de collision. Ces échecs sont conservés dans Saved. Avertissement restant `LogGrass` : maps d'herbe encore en attente à la fermeture de l'éditeur ; aucune couche d'herbe n'est implémentée. Les avertissements d'UI éditeur et du compilateur non préféré sont consignés, sans désactivation arbitraire.

## Dernière validation : boucle de retour return-r3

VÉRIFIÉ : create-10, route 9550,66 m. Les trois vrais véhicules terminent 9548 m, sans récupération, téléportation ou transformation, zéro intervalle sans contact roue. Traces de terrain sans trou, pente maximale 8,47 % ; chiffres bruts dans les rapports.

| Véhicule | Temps simulé | Écart maximal | Sortie processus |
|---|---|---|---|
| Thunderhawk | 1165,21 s | 1,20 m | 0 |
| Hurricane | 1236,48 s | 1,18 m | 0 |
| Rhino | 1186,13 s | 0,84 m | 0 |

Rapports `docs/validation/silent-valley/driving/return-r3-<véhicule>.json`. Commande pour chacun : `Tools/Migration/Test-SilentValley.ps1 -RunName return-r3 -Vehicle <véhicule> -Fast -FullRoute`. Tests automatisés prudents, pas une mesure FPS ni une validation manuelle à 300 km/h.

Échecs conservés : r1 Rhino dépasse le seuil dans le dernier virage ; r2 Thunderhawk se renverse au croisement final, alors que Rhino l'avait passé. La géométrie a été élargie puis le croisement supprimé, sans réduire les critères ni modifier les véhicules. Le retour r3 est la géométrie actuelle. Limites de carte, collisions latérales et arène à plusieurs véhicules restent NON TESTÉES ; G2 complet reste ouvert. Les notes ci-dessous conservent les validations et défauts antérieurs.

| Jalon | Statut | Preuve / limite |
|---|---|---|
| G0 audit ciblé | VÉRIFIÉ | UE 5.8.2, plugins, trois véhicules, Fab local et sources Boulder Hill identifiés ; plan et manifeste |
| Nouvelle map et Landscape | VÉRIFIÉ | Vrais assets sauvegardés par UnrealEditor-Cmd ; `Saved/SilentValley/create-05.log` |
| Spawn et sortie de Boulder Hill, Thunderhawk | VÉRIFIÉ | Conduite Chaos sans téléportation, captures `drive-g1-r5-Thunderhawk/zone-0.png` |
| Parcours jusqu'aux cinq POI, Thunderhawk | VÉRIFIÉ pour franchissement | 5,867 km, 435,79 s simulées ; aucun intervalle sans contact de roues ; `drive-g1-r5-Thunderhawk/drive.json` |
| Maintien sur la chaussée | NON TESTÉ avec critères suffisants | Écart maximal 11,02 m : l'ancienne sonde autorisait 13 m. Ce passage prouve le parcours du terrain, pas un maintien dans une route de 10 m. Corriger le contrôle et valider le revêtement visible |
| Rhino / Hurricane | NON TESTÉ en totalité | Passages en cours, ne pas interpréter le champ passed=false d'un rapport incomplet comme un résultat final |
| Continuité des surfaces | VÉRIFIÉ partiellement | 2658 traces au sol sans trou ; pente maximale 6,51 %. Identité chaussée/terrain et rendu à contrôler séparément |
| G2 limites, retour et trois véhicules | NON TESTÉ | Pas de validation globale tant que les écarts, raccords et collisions n'ont pas passé les critères |
| G3 vitrine / PCG / photoréalisme | NON TESTÉ | Pas de dressing massif avant G1/G2 ; matériaux actuels explicitement blockout |
| G4 mission, combat et récompense | NON TESTÉ | Checkpoints d'observation uniquement, aucun succès de mission implémenté/revendiqué |
| Coop / package / performance finale | NON TESTÉ | Aucun chiffre FPS revendiqué depuis les essais accélérés à pas fixe |

Les essais de conduite injectent les axes Xbox dans le vrai véhicule Chaos ; ils ne déplacent pas l'acteur sur la spline. Les captures sont de vraies trames du jeu. `-Fast` fixe le pas à 1/60 s ; son temps réel et son débit ne sont pas une mesure de performance de jeu.

Erreurs corrigées : AssetRegistry incomplet empêchant la duplication du GameMode ; départ à tangent nul ; construction Python Rotator positionnelle aux axes incorrects ; sous-braquage de la sonde dû à la zone morte Xbox 25 %. Les échecs précédents sont conservés. Boulder Hill est importé en pose ouverte statique, sans animation native de ses mécanismes à ce stade. Les tangentes quasi nulles du mesh importé restent un point de QA artistique.

Suite G2 : `g2-r1` Rhino échoue à Pinewood (714 m, écart 3,24 m, seuil 3,2 m). Le passage des tangentes `CurveClamped` à `Curve` corrige la rupture de virage en plan. `g2-r2` conserve un écart inférieur à un mètre jusqu'après la carrière, mais la pente mesurée monte à 14,65 % par dépassement vertical des tangentes automatiques : résultat global en échec même si les POI sont atteints. Une correction séparée limite les tangentes verticales ; compilation 11 et create-08 puis g2-r3 sont à vérifier. Aucun critère n'est relâché pour cacher ce défaut.

## Résultats du parcours corrigé — G2-r3

Compilation 11 et reconstruction create-08 réussies. Pente maximale ramenée à **8,47 %** ; 2712 traces sans trou. Les trois vrais véhicules atteignent successivement les cinq lieux, sans téléportation ni changement de mode, avec **zéro intervalle sans contact de roue** dans ces passages :

| Véhicule | Parcours | Temps simulé | Écart maximal à l'axe | Résultat brut |
|---|---|---|---|---|
| Rhino | 5969 m | 775,69 s | 0,84 m | VÉRIFIÉ, sortie 0 |
| Thunderhawk | 5969 m | 753,86 s | 1,22 m | VÉRIFIÉ, sortie 0 |
| Hurricane | 5969 m | 811,58 s | 1,18 m | VÉRIFIÉ, sortie 0 |

Rapports : `docs/validation/silent-valley/driving/g2-r3-<véhicule>.json`. Les traces indépendantes `surface-probe.json` identifient le véritable acteur SilentValleyRoad et ses SplineMeshComponents aux six distances échantillonnées, à la hauteur attendue. La lisibilité visuelle du revêtement après correction reste à confirmer avec les nouvelles captures ; les anciennes images montrent la version antérieure.

Cette preuve valide le trajet de sortie → cinq POI pour ces contrôles automatisés à vitesse prudente. Elle ne valide pas encore le retour complet, la conduite manuelle à grande vitesse, les collisions latérales et limites de carte, le photoréalisme, la mission ou le réseau. G1 parcours principal VÉRIFIÉ ; G2 complet toujours EN COURS.

## Contrôle visuel — défauts ouverts

### Reprise validée : chaussée et marquages

Build 15 réussi après fermeture de la partie utilisateur. Les captures `views-blockout-r3` ont confirmé la cause principale : culling des faces du ruban routier, corrigé par le matériau double face (pas de modification du LOD Landscape dans ce diagnostic). Le matériau marqué v2 utilise les broches d'API UE 5.8 réelles ; v1 est conservé comme tentative en échec et n'est plus utilisé par la carte. Le shader v2 ne produit pas d'erreur de compilation dans le log du rendu final.

Les **10 captures de `views-roadpaint-r2` ont été ouvertes** : route visible aux cinq lieux en jour/golden hour, ligne centrale jaune discontinue et rives blanches ; disparition des triangles alternés sur les deux dalles après abaissement de 3 cm. Voir [Boulder Hill](../validation/silent-valley/views-roadpaint-r2/day-zone-0.png), [Pinewood](../validation/silent-valley/views-roadpaint-r2/day-zone-1.png), [Eagle Pass](../validation/silent-valley/views-roadpaint-r2/day-zone-2.png), [Old Quarry](../validation/silent-valley/views-roadpaint-r2/day-zone-3.png), [North Ridge](../validation/silent-valley/views-roadpaint-r2/day-zone-4.png). Il s'agit de géométrie et de matériaux de blockout, sans revendication photoréaliste. Les panneaux sont encore vus de dos dans plusieurs cadrages ; le relief macro et l'éclairage golden hour restent à améliorer.

Régression après modification des dalles : Rhino G2-r4 **VÉRIFIÉ**, 5969 m, 775,69 s simulées, écart max 0,84 m, aucun intervalle sans contact roue, sortie 0. Rapport [G2-r4 Rhino](../validation/silent-valley/driving/g2-r4-Rhino.json). Les physiques et géométries des véhicules n'ont pas changé. Sonde de retour complet ajoutée via `Test-SilentValley.ps1 -FullRoute`, résultat à enregistrer après exécution ; ne pas déduire une validation du retour de cette régression jusqu'au ridge.

Reprise : la correction de séquencement des captures est ajoutée en C++. Build 14 échoue **au lien**, LNK1104 : une partie utilisateur lancée par `Jouer-SilentValley-Editor.cmd` verrouille `UnrealEditor-VehicularCombat.dll`. Cette partie est volontairement préservée. Aucun succès de compilation complète ou de nouveau rendu annoncé pour cette passe ; le diagnostic double face n'a pas encore été exécuté. Reprendre le lien après fermeture de la partie, puis inspecter de nouvelles images.

Compilation 13 avec `-gather` réussie : le nouveau fichier de capture est désormais effectivement lié. Le matériau asphalte porte son flag `used_with_spline_meshes`, enregistré par `fix_silent_valley_road_material.py`. Les quatre premières images jour de `views-blockout-r2` ont été ouvertes et **ne valident pas la lisibilité** : relief très grossier, asphalte encore caché malgré les traces physiques correctes, cadrage de la base inadéquat. Hypothèse à vérifier : LOD du Landscape dont la surface rendue peut dépasser la chaussée ; ne pas présenter l'hypothèse comme diagnostic confirmé. La file de captures change aussi la caméra dans la même trame que la demande de screenshot : corriger avant de légender définitivement les lieux. Les images actuelles sont preuves de défaut, pas preuve d'un environnement fini. G3/mission/coop/package restent non réalisés.

Commandes exécutées : `Invoke-UE58.ps1 -Task Build` (dernière passe 08 réussie), `UnrealEditor-Cmd -run=pythonscript -script=<absolu>/Tools/Art/build_silent_valley.py` (create-01 à create-05, corrections documentées), `Test-SilentValley.ps1 -RunName g1-r5 -Vehicle Thunderhawk -Fast -Render`, puis les deux autres véhicules en mode `-Fast`. Les arguments exacts et les logs sont dans `Saved/SilentValley/drive-*/launch.json` et `game.log`.
