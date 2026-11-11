# Handoff — Silent Valley, clipping et ciel — 11 novembre 2026

## Objectif, dépôt et état réel

Finir l'environnement avec un ciel réaliste/beau et résoudre le clipping signalé. Colorado photographique et implantation interprétée explicitement autorisés ; référence inspectée dans docs/levels/SILENT_VALLEY_NATURAL_ENVIRONMENT.md. Préserver véhicules, maniabilité confirmée, mission solo V0 (14 contrôles antérieurs) et sources.

Dépôt UNIQUE à G:/DEV/mask-project-mayhem, branche main, HEAD47dbab9, origin=https://github.com/raguets/mask-project-mayhem.git. GitHub migration déjà publiée, LFS actif ; ancien .git archivé sous .git-backups (ignoré). Tous les chemins suivants relatifs à VehicularCombat. L'état était propre au début du lot. Changements du lot actuel non committés ; aucune publication de ces changements revendiquée. Les écritures .git sont restreintes depuis Codex ; ne pas contourner.

Utilisateur avait ouvert Unreal/Fab. Les deux accès de contrôle, cua_repl et node_repl/@oai/sky, échouent désormais avant toute interaction : « failed to write kernel assets: chemin introuvable ». L'utilisateur a explicitement enregistré ET fermé Unreal à ma demande. Le travail se poursuit par vrais commandlets et captures GPU ; ne pas prétendre avoir utilisé Fab pendant ce lot. Ne pas relancer la plantation, terminée r6 : 298 pins, 10826 herbes, 115 rochers sauvegardés.

## Diagnostic et corrections enregistrées

Réouverture indépendante environment-reload-r1 : tous les comptes/route/PCG/berges passaient sauf la collision du lac, redevenue bloquante. Route9550,658m, 476 segments, 39 anciens rochers PCG et cinq objectifs conservés. Sonde collision antérieure : 2835 points, marge terrain/chaussée min43,524cm ; ne prouve pas l'absence de défaut visuel.

Dix images baseline RÉELLES inspectées dans Saved/SilentValley/views-natural-baseline-r2 : grandes ruptures/trames sur les versants, végétation et eau très aliasées, vagues répétitives trop fortes, ciel de base, HUD UMG encore visible. Compilation native et génération ne prouvent pas la qualité artistique. Diagnostic confirmé : r.AntiAliasingMethod=0 ; LOD Landscape par défaut. Certaines copies de matériaux de branches utilisaient les textures de démonstration PVE. Les imports originaux référencent aussi des chemins développeur absents (avertissements encore possibles au chargement).

Corrections du lot : Config/DefaultEngine.ini AA=4 (TSR). Tools/Art/refine_silent_valley_view_distance.py exécuté environment-distance-r2, sortie0 : LOD0ScreenSize.2, distribution3.5, maxLOD2 ; 93 composants à moins de330m du centre échantillonné de route forcésLOD0 ; fade herbe100–180m dans les deux masters locaux. Aucune donnée de hauteur/collision modifiée. R1 avait échoué sur propriété component_size_quads non exposée ; corrigé en dimensions connues252m et setter natif.

Tools/Art/refine_silent_valley_atmosphere.py exécuté atmosphere-r2, sortie0 : profil NoCollision du lac ; nouveau M_SV_LakeWater_v2 (v1 préservé), normales réduites, phases perturbées, rugosité.23 ; copies bark/young relient les vraies textures importées Baltic. Sun75000lux,6000K ; nuages couche2.2–4km, couverture-.12, échelle128, samples1 ; brume.0015, falloff.13 ; PPV local SV_EnvironmentExposure_v1 histogramme, luminance.3–10000 et biais-.3. Aucun matériau original Fab/Boulder Hill modifié. R1 avait échoué sur texture non scannée ; scan AssetRegistry explicite ajouté. Ces réglages ATTENDENT la comparaison rendue et peuvent nécessiter correction.

Capture native SilentValleyViews.cpp : RemoveAllWidgets ajouté pour masquer réellement l'UMG dans les vues de diagnostic ; aucun HUD normal changé. environment-views-r7 : objet CPP, DLL, LIB et métadonnées sortis0 via graphe MSVC exporté, pas un succès UBT standard (limitation UBA/AppData connue).

## Cause racine et réparation exécutée

Les vues quality-r1/r2 étaient surexposées : essais REJETÉS. Passage AutoExposure=True et surtout histogram_log_min=-8/max16 dans le PPV permet l'éclairage75000lux ; quality-r3 montre maintenant ciel nuageux et lac réfléchissant, mais des plaques de terrain manquantes. Diagnostic natural-culling-diagnostic-r1 avec r.ForceLOD0 et occlusion désactivée : les grandes parois disparaissent et révèlent le vrai relief bas. Cause trouvée dans UE5.8 LandscapeEditInterface.cpp : SetHeightData écrit mip0 et appelle RequestHeightmapUpdate, mais ne consomme pas InGenerateMips en commandlet. Les mips distants conservaient l'ancien terrain, provoquant parois artificielles/popping/culling incohérent.

SilentValleyEditorLibrary.cpp ajoute RebuildSilentValleyHeightmapMips : rééchantillonnage16bits de hauteur par sous-section, extrémités partagées, normales interpolées et mips finaux ; vérification CRC de CHAQUE mip0 inchangé ; GUID/resource dérivés et bounds rafraîchis. Helper natif de génération moteur non exporté : première tentative r9 lien échoué, remplacée par calcul local ; r10 objet/DLL/LIB/métadonnées sortis0. RefineNaturalLandscape conserve son API/retour0 sur terrain déjà raffiné ; répare une fois avec tag SV_RENDER_MIPS_V1. Les futurs appels de génération de hauteur reconstruisent aussi leurs mips. Aucun changement de géométrie source, véhicules ou mission.

Tools/Art/repair_silent_valley_render_mips.py exécuté environment-mip-repair-r1 sortie0 : 16 heightmaps,256 composants, mip0 CRC inchangés ; 95 sondes collision, delta0cm ; carte sauvegardée avec tag. Rapport environment-v1/render-mips.json. Réouverture r2 précédente passe TOUS les critères, collision lac corrigée. Rendus finaux avec culling normal encore à vérifier après réparation.

## Traitement EN COURS

Capture natural-repaired-r1, session exec42948 : Saved/SilentValley/views-natural-repaired-r1. Dix PNG jour/soir attendus avec réglages NORMAUX (aucun r.ForceLOD global ni désactivation d'occlusion). Inspecter TOUS avant de valider. Dossier de cache Temp indiqué plus haut. Aucun éditeur utilisateur ouvert, fermeture enregistrée explicitement confirmée.

## Première action recommandée

Récupérer session42948 / vérifier journal et dix PNG repaired-r1. Confirmer disparition des parois/plaques et continuité du terrain en fonctionnement normal. Ensuite densifier si nécessaire les bosquets Pinewood en réemployant les assets, valider en déplacement et faire Rhino FullRoute + mission solo. Ajouter preuves et rapport, puis mettre le handoff à jour. Ne pas relancer la plantation r6 ni refaire maniabilité/mission déjà acquises. Contrôle UI/Fab toujours indisponible, commandlets et captures GPU fonctionnent.