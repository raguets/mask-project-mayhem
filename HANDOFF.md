# Handoff — Raven V16, corrections de carrosserie et vitrage — 11 novembre 2026

## Lot suivant EN COURS — intégration Raven dans Pinewoods

Demande : Raven roule et vole comme Thunderhawk sans stationnaire. Code ajouté : RavenPawn/roues33,5cm, ConfigureRavenChassis, flotte/menu/retry et lanceur Bots3. Dynamique fixed-wing existante réutilisée. Export Blender MCP terminé sous `VehicularCombat/SourceArt/MASK/Raven` :20 groupes rigides,4 pneus,97 samples, FBX/atlases/manifest ; source dérivée `art_source/GameReady/Raven/Raven_GameReady.blend`. Calhoun18 animations à pied dans SourceArt/MASK/OnFoot/Calhoun. V16 restaurée ; utilisateur informé qu'il peut fermer Blender et n'a pas à lancer Unreal.

Compilation principale sortie0 (Saved/SilentValley/raven-native-r3 actions0/1, raven-native-r4 actions2/3/4). UBT reste en échec UBA après export actions ; ne pas prétendre build UBT normal. Runner RC corrigé pour passer les guillemets natifs exacts. Nouveau RavenSmoke ajouté ensuite : -gather nécessaire. Compilation test EN COURS exec84352, `Saved/SilentValley/raven-test-native-r5`, graphe build-raven-test-actions.json ; ne relier la DLL qu'après fin de l'import.

Import graphique r1 arrêté avant création d'assets après démarrage sans progression pendant3min. Import r2 NullRHI/NoShaderCompile EN COURS, exec10073, PID/arguments dans `Saved/Art/raven-import-r2/launch.json`, log editor.log. Vérifier raven-import.json ET raven-locomotion-import.json passed ; éditeur doit quitter. Ensuite Test-Raven.ps1 (Pinewoods4 véhicules, switch/route/vol minimum/virage/atterrissage) et Test-OnFoot -Terrain -Vehicle Raven. Aucun essai gameplay Raven passé à ce stade. Sections suivantes : lot artistique précédent.

## Objectif et état réel

Lot actuel : raffiner Raven et Calhoun Burns dans Blender MCP suivant les corrections utilisateur. Assemblage actif enregistré : `art_source/Raven/Raven_V16_Assembly.blend`, frame1, hover_height0, Raven_Control sélectionné. Aucun rendu actif ni état essentiel non enregistré ; preuve `art_source/Raven/checkpoint_v16.json`. V11 initialement ouverte dirty/frame171 a été préservée dans `Session_before_V12_20261111_195221.blend`. V12 à V16 et exports antérieurs conservés.

Dépôt Git réellement à la RACINE `G:/DEV/mask-project-mayhem`, branche main, HEAD `a2fce0c` « Pine Valley environment OK ». Unreal reste dans `VehicularCombat/VehicularCombat.uproject`. Aucun commit/push effectué. Ancienne instruction parlant du dépôt imbriqué dépassée par cette migration vérifiée. Status global retenté : échec clean LFS sur L_SilentValley_Blockout.umap, accès refusé à `.git/lfs/tmp`. Ne pas contourner la restriction lecture seule de .git. Status ciblé/diffs texte consultés, aucune modification indexée. Préserver branding, README/lanceur racine, archives et preuves environnement antérieurs.

## Réalisé dans ce lot

Skill projet mask-asset-production appliqué ; fiche de transformation lue avant les images. Références fournies inspectées : jouets Raven, photographies Corvette C4 et illustration/figurine Calhoun distinguées. s-l500.jpg réinspectée pour le pare-brise. Interprétation réaliste du visage/anatomie et habitacle caché autorisée ; dimensions et mécanismes non cotés restent estimés.

Capot lissé rigide au niveau des épaules, retours/joints repris ; partie fixe saillante devant le pare-brise supprimée, tableau de bord rentré. Plancher fixe arrêté àX0,425m, tunnel à0,405m. Portes incurvées avec retours ; canons diamétraux encastrés élargis45→90mm et logements adaptés. Tout l'avant tourne avec ses roues, puis bascule secondaire de celles-ci : architecture V11 conservée.

Cassette commune de quatre réacteurs montant de0,197m, coque noire seulement dessus/flancs avec raccords arrondis, dessus HORIZONTAL. Les buses dégagent la façade fixe de9mm au déploiement. V13 avait encore deux buses extérieures visibles au repos : correction de profondeur18mm, contrôlée par rendu fermé V14/V16.

Toit : centre fixe et deux parties latérales solidaires des portes, environ trois tiers. Dernière correction : ailes un peu plus fines à l'avant, raccord arrondi vitre latérale/toit. V15 avait des extrémités de joints saillantes : coins des vitrages et joints repris en V16. Pare-brise au contour trapézoïdal courbe ; lunette prolongée jusqu'àX−1,815m près de la cassette, plus arrondie et très sombre avec matériau distinct. Montants noirs derrière les portes. AGENTS.md et fiche actualisés.

## Validation et fichiers courants

`art_source/Raven/validation_v16.json` PASSE24 contrôles :33 états pneus/carrosserie,31 états nouvelles pièces de toit contre vitrages fixes, rigidité capot et limites. Aucune intersection sur ces paires ; accostages fermés exclus du test mobile de toit. Ce n'est pas une certification de tous les volumes ni de l'ajustement du pilote.

`art_source/Raven/renders/v16_review` :8 PNG1280×960 Cycles GPU28 échantillons, TOUS ouverts et inspectés ; COMPLETE présent, aucun ERROR. V14 contient12 vues supplémentaires (lunette, cassette, coupe habitacle, personnage assis). Rendus anciens conservés, V15 remplacée pour les coins.

Sources autonomes exportées et réellement rouvertes : `art_source/Raven/Raven_V16_Vehicle.blend`, `art_source/Calhoun_Burns/CalhounBurns_V2.blend`, masque inchangé `CalhounMask_V1.blend`. Rapport `standalone_validation_v16.json` PASSE : trois sources indépendantes, drivers valides, même personnage/poids dans quatre états, pneus persistants, cassette verticale0,197m. V2 adapte la pose de jambes au plancher court. Rapport détaillé : `docs/progress/2026-11-11-Raven-canopy-and-cassette.md`, README des deux assets actualisés. Scripts dans `art_source/Raven/scripts`, helpers partagés dans `art_source/shared_tools`.

## Terminé auparavant / limites et suite

Retry Unreal conserve Bots0–6, Vehicle/listen. Build natif r17 sorties0 ; tests réels Bots2 donne2→2 et Bots0 donne0→0,16 contrôles chacun. Preuves `VehicularCombat/docs/validation/silent-valley/retry-fleet`. Ne pas refaire ce correctif.

Raven n'est pas intégrée dans Unreal ; pas de retopologie/UV finale. Peau, cheveux, plis et contacts mains/pédales encore stylisés. Contact pied/plancher NON validé : dessus des bottes minZ0,126m contre plancher haut0,160m, à reprendre par coupe dédiée. Vérifier direction MONDIALE des canons arrière après bascule ;45° local ne certifie pas le tir vers l'avant. Pinewood reste avec diagnostic rupture relief32m/2m, LAN/pickups et consolidation racine en attente ; utilisateur dirige actuellement vers Raven.

## Première action recommandée

Interroger la scène réellement ouverte, puis reprendre en priorité les contacts pilote/plancher et direction des canons arrière sur une NOUVELLE version, sans refaire le toit corrigé :

```powershell
& 'G:/Program Files/Epic Games/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe' .agents/skills/mask-asset-production/scripts/mcp_client.py get_scene_info --port 9876
```

MCP local9876 opérationnel. Utiliser ce même Python avec execute_code --code-file pour les scripts Blender. Vérifier l'absence de file active avant mutation ; ne pas remplacer ce workflow par Blender batch. Suivre toute nouvelle correction utilisateur prioritaire.
