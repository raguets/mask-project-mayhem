# Silent Valley — plan et audit ciblé

Branche `feature/silent-valley-mission-01`, base `a542c4d`. La [checklist persistante](SILENT_VALLEY_CHECKLIST.md) indique la prochaine action et les résultats ; elle prime sur ce plan de travail après interruption. Les gates G0–G5 suivent le prompt utilisateur récent (environnement avant mission), plutôt que les numéros différents de la proposition v1 locale.

## G0 : faits vérifiés

- Dépôt réel : `G:/DEV/mask-project-mayhem/VehicularCombat`, module runtime `VehicularCombat`, `VehicularCombat.uproject`, association 5.8. Aucune nouvelle migration.
- UE installé : 5.8.2, CL 56702186, `G:/Program Files/Epic Games/UE_5.8`. Scripts UBT/UAT opérationnels déjà présents dans `Tools/Migration` ; état de référence compilé et testé au commit de départ.
- GPU : RTX 4060 Ti, 16 380 MiB via nvidia-smi. Mémoire système ~32 Go d'après les builds précédents ; à relever à nouveau lors du profilage. Espace initial G: ~2,36 Go, C: ~12,86 Go : risque réel pour le cook/archivage, aucun ancien paquet supprimé.
- Plugins présents et montés dans les journaux Editor existants : PCG, PythonScriptPlugin, EditorScriptingUtilities, ModelingToolsEditorMode et Fab. Vérification API dans `Saved/SilentValley/environment-audit.json`. Ne pas réinstaller ni demander une réactivation. Bridge est ignoré, même s'il figure dans le descripteur.
- Cartes existantes : `/Game/Maps/MainMenu` et `/Game/Maps/TestMaps/Test`. Elles sont conservées.
- Trois véhicules : `AThunderhawkPawn`, `ARhinoPawn`, `AHurricanePawn`, Blueprints `/Game/MASK/{Thunderhawk,Rhino,Hurricane}/BP_<nom>`, définitions `DA_<nom>`. Matt/Spectrum, Alex/Jackrabbit, Hondo/Blaster ; Rhino garde son module `ARhinoRearModule` et Bruce/Lifter. Source : `Source/VehicularCombat/Private/MASK`.
- Spawn : `ACustomGameMode::InitGame` lit `?Vehicle=Thunderhawk|Rhino|Hurricane`, puis `RestartPlayer` et PlayerStarts. Le GameMode existant conserve HUD, armes et contrôleur. Une carte distincte et son GameMode dérivé pourront réutiliser ces mécanismes sans modifier la physique.
- IA : `AVehicleBotController`, véhicules Chaos réels ; combat dans `ABaseWheeledVehiclePawn::UpdateBotCombat`, armes/projectiles existants, `UHealthComponent`. Réseau OnlineSubsystemNull/IpNetDriver et changement de véhicule déjà testés. Conducteurs à pied autoritaires serveur/CharacterMovement conservés.
- Aucun système d'objectifs de mission identifié dans les headers existants ; ajout spécialisé uniquement après validation du parcours.
- Fab : `Small_Beach_Rock_wd4kfdx`, mesh sous `/Game/Fab/Megascans/3D/Small_Beach_Rock_wd4kfdx/Medium/wd4kfdx_tier_2/StaticMeshes/wd4kfdx_tier_2`, textures 2K et matériau. Contenu utilisateur non suivi avant notre travail ; ne pas le supprimer ni le committer avec les créations de niveau. Source/licence/statut gratuit à consigner après vérification réelle.
- Boulder Hill réutilisable : `../art_source/Boulder_Hill/BoulderHill_V6_Base.blend`, source indépendante, sans véhicules de démonstration. Palette brune intermédiaire approuvée et mécanismes existants préservés. Porte estimée 6 × 5,43 m ; Rhino de source 9,18 × 3,19 × 4,49 m. Ces mesures sont des estimations du modèle, pas des dimensions officielles. Vérifier les véhicules effectivement importés.

## Choix initiaux G1/G2

Nouvelle carte `/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout`. Landscape natif d'environ 4,032 × 4,032 km : 2017 × 2017 sommets, pas XY 2 m, 256 composants à deux sections de 63 quads. Relief déterministe original, pas de heightmap tierce. Grader le terrain sous les routes selon les mêmes échantillons de spline pour éviter un faux raccord visuel.

Routes par `USplineComponent` et `USplineMeshComponent`, chaussée subdivisée avec collision complexe statique réelle : ce choix permet d'automatiser les profils longitudinaux et la continuité avec l'API locale, sans dépendre d'une façade Python Landscape Splines absente. Cible initiale : 10 m de chaussée pour les véhicules larges, accotements, courbes progressives, pentes visées <8 %. Toutes ces valeurs restent NON TESTÉES avant les passages physiques.

Le blockout sera d'abord une carte classique indépendante : 256 composants Landscape avec LOD, faible densité et aucune conversion des maps existantes. World Partition est évalué pour une future carte gameplay distincte après mesures de mémoire/streaming ; il n'est pas indispensable à cette première preuve de parcours. Ne pas annoncer le streaming testé avant exécution.

Boulder Hill : inspecter par Blender MCP, exporter une copie évaluée en configuration de garage ouvert pour le premier passage, sauvegarder les sources originales et le manifeste. Les mécanismes animés natifs seront ajoutés ensuite ; un asset figé ouvert devra être explicitement présenté comme tel. Un garage simple temporaire permet de poursuivre le premier test si l'import n'est pas prêt.

## Lots et fichiers

1. `Private/SilentValley/` : acteurs de route et outils éditeur strictement limités au namespace de la nouvelle carte ; `Tools/Art/build_silent_valley.py` exécuté dans Unreal pour créer/sauvegarder les véritables assets. Modules éditeur sous `WITH_EDITOR`.
2. `Content/MASK/Maps/SilentValley`, `Environment/SilentValley/{Landscape,Roads,Materials,Structures}` : map, matériau et chaussée. Aucune modification des véhicules ni de la carte de test.
3. `Private/Tests/SilentValleySmoke.cpp`, `Tools/Migration/Test-SilentValley.ps1` : conduite physique des trois classes depuis le garage jusqu'aux POI, mesures contacts/pentes/progression, traces de collision, captures et logs. Des téléportations de cadrage ne compteront jamais comme parcours pilotés.
4. G3 : tronçon vitrine seulement, puis PCG avec exclusions routes, base, spawns et carrière ; assets natifs/originaux et Fab vérifiés, pas d'achat. Matériaux et lumière jour/golden hour comparés in-engine. Profilage réel avant extension.
5. G4 : directeur répliqué et définition de mission, déclenchements idempotents, IA/armes existantes, récupération/extraction, récompense locale et retry. Ne pas refondre le gameplay existant.
6. G5 : rapport `docs/tests/SILENT_VALLEY_TEST_REPORT.md`, cinq lieux jour/golden hour, coop à deux instances si possible, distribution avec accès séparé au jeu d'origine, points de contrôle Git.

## Risques et preuves attendues

API Landscape/PCG/GeometryScript : inspecter les headers et classes effectivement installés ; corriger progressivement après compilation. Un import/sauvegarde réussi ne valide ni collision ni qualité visuelle. L'IA routière, les pentes et le raccord de la porte de Boulder Hill sont prioritaires. Les performances de Lumen/Nanite restent à mesurer ; ne pas activer aveuglément. Les assets Fab ne sont pas présumés gratuits ni licenciés pour le projet sur la seule présence d'un fichier.

Les fonctionnalités existantes doivent rester accessibles par le lanceur actuel. Les éléments générés sont isolés, les scripts refusent d'écraser une map existante sans sauvegarde/version explicite. Avant chaque mutation risquée, conserver hashes et copie des fichiers concernés. Aucun achat, contrat accepté, secret transmis ou installation.
