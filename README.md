# M.A.S.K. Project Mayhem

Entrée de jeu : **`Jouer-MASK.cmd` à la racine** (Unreal Engine 5.8). Elle lance Pinewood / Silent Valley avec Thunderhawk et trois équipiers : Rhino, Hurricane et Raven. L'essai Raven vérifie leur présence et le changement de contrôle sur cette carte. Les anciens raccourcis sont archivés comme texte ; les scripts `Tools/Migration/Test-*` sont des diagnostics.

Raven utilise Calhoun Burns et son masque séparé, avec conduite au sol et vol de type avion comme Thunderhawk : vitesse commandée50–300km/h, sans stationnaire, puis atterrissage et rétraction. Source artistique préservée : `art_source/Raven/Raven_V16_Assembly.blend`. Intégration : `/Game/MASK/Raven/BP_Raven`, contrôles et réplication communs aux autres véhicules. Le mode de navigation sur l'eau n'est pas implémenté.

Le projet Unreal reste provisoirement dans `VehicularCombat`. Le regroupement à la racine et les transitions de l'ancien menu sont en cours d'audit : [consolidation](VehicularCombat/docs/levels/PINEWOOD_CONSOLIDATION.md). État exact et reprise : [HANDOFF.md](HANDOFF.md).

## Hurricane V7 — Hondo MacLean

Assemblage : `art_source/Hurricane/Hurricane_V7_Assembly.blend`. Véhicule indépendant : `art_source/Hurricane/Hurricane_V7_Vehicle.blend`. Hondo et son masque : `art_source/Hondo_MacLean/HondoMacLean_V1.blend` et `HondoMask_V1.blend`.

Relevage limité à 0,30 m, haut des roues centrales partiellement caché, soubassement noir plus haut avec quatre montants entre les roues. Canon de pare-brise à droite. Toit ouvrant et doubles canons, phares-canons, canons inférieurs, disque arrière guidé et roue de secours éjectable. Le même Hondo est debout, assis ou au double canon, avec masque visible/caché.

Images 1 (route), 151 (défense), 191 (roue en vol), 211 (roue au sol). Commandes et limites : `art_source/Hurricane/README.md`. Rendus : `art_source/Hurricane/renders/v7_final/`. Références : `docs/art/Hurricane_reference_review_v1.md`. Contrôles : `motion_validation_v7.json` et `standalone_validation_v7.json` dans le dossier source. Dimensions et mécanismes cachés estimés ; finition humaine stylisée et préparation de jeu encore à approfondir. Versions antérieures conservées.

## Boulder Hill V6

Couleur V6 : marron chaud intermédiaire et éclairage de scène renforcé. Géométrie et mécanismes V4 conservés. Base secrète adossée à une montagne réduite et raccordée aux bâtiments. Devanture en prisme triangulaire pivotant d'un seul bloc, pompes et enseigne armées, rocher mobile avec canon/fauteuil, garage en quart de cercle à double porte. Dalle rectangulaire compacte, sans route devant la sortie. Quatre emplacements intérieurs dimensionnés avec les véhicules existants.

Assemblage : `art_source/Boulder_Hill/BoulderHill_V6_Assembly.blend`. Source de la base indépendante : `art_source/Boulder_Hill/BoulderHill_V6_Base.blend`. Sélectionner `BoulderHill_Control` ; images 1 (station), 65 (prisme intermédiaire), 181 (défense), 211 (porte ouverte), 285 (sortie Thunderhawk), 510 (sortie Rhino). Les véhicules sont des copies de démonstration à leur échelle d'origine ; leurs sources restent inchangées.

Commandes, références, contrôles et limites : `art_source/Boulder_Hill/README.md`. Rendus inspectés : `art_source/Boulder_Hill/renders/v6/`. Les dimensions, le volume arrière agrandi, la montagne et les mécanismes cachés restent des interprétations des références jouet/dessin animé et des corrections utilisateur. Les versions précédentes sont conservées.

## Rhino V3 — Alex Sector et Bruce Sato

Assemblage : `art_source/Rhino/Rhino_V3.blend`. Véhicule indépendant : `art_source/Rhino/Rhino_V3_Vehicle.blend`. Module arrière autonome : `art_source/Rhino/Rhino_RearVehicle_V1.blend`. Alex et Bruce ont chacun une source articulée et un masque indépendant dans `art_source/Alex_Sector/` et `art_source/Bruce_Sato/`.

V3 : pare-buffle repris depuis la nouvelle photo fournie, avec contour fermé et barreaux verticaux. Sa largeur et sa hauteur correspondent à celles de la calandre, sans montants trop hauts ; coulisse conservée. Rendus `art_source/Rhino/renders/v3/`, contrôle `bullbar_validation_v3.json` et réouverture `standalone_vehicle_validation_v3.json`. Compte rendu : `docs/progress/2026-11-03-Rhino-V3-pare-buffle.md`.

V2 : capot abaissé, vitres supérieures abaissées et évasées en plan, petit radar tournant, grand coffre reculant avant la sortie d’un missile noir unique. Pare-buffle avancé, échappements rabattus en canons et module détachable ; roues centrales extérieures conservées au camion, intérieures au module. Timeline 1–241 : route à l’image 1, transformé à l’image 151.

Commandes et limites : `art_source/Rhino/README.md`. Références : `docs/art/Rhino_reference_review_v1.md`. Compte rendu : `docs/progress/2026-11-03-Rhino-V2.md`. Rendus : `art_source/Rhino/renders/v2_final/` ; rapports `validation_v2.json`, `cabin_fit_v2.json` et `standalone_validation_v2.json` dans le même dossier source. Versions antérieures conservées.

## Thunderhawk V14 — Matt Trakker et Spectrum


Version active : **V14**, avec Matt V5 (cou repris et pose de conduite corrigée) et Spectrum V4 amovible (base évasée ajustée aux épaules). Vitrage légèrement teinté et réfléchissant, plage arrière et plaque M.A.S.K. entre les réacteurs conservés. Les versions précédentes et les états intermédiaires sont conservés.

- Assemblage : `art_source/Thunderhawk/Thunderhawk_V14.blend`
- Véhicule indépendant avec habitacle et mécanismes : `art_source/Thunderhawk/Thunderhawk_V14_Vehicle.blend`
- Personnage indépendant : `art_source/Matt_Trakker/MattTrakker_V5.blend`
- Masque indépendant : `art_source/Matt_Trakker/Spectrum_V4.blend`
- Rendus inspectés : `art_source/Thunderhawk/renders/v14/`
- Compte rendu et limites : `docs/progress/2026-11-03-V14.md`
- Rapports : `art_source/Thunderhawk/validation_v14.json` et `standalone_validation_v14.json`
- Méthode réutilisable : `.agents/skills/mask-asset-production/SKILL.md` (également installée dans les skills personnels Codex)

Sur `MattTrakker_Rig`, `driving_pose` (0 debout, 1 conduite) et `mask_on` (faux/vrai) pilotent le même personnage articulé. Le visage est conservé sous Spectrum. Transformation du véhicule : images 1 à 193.

La V14 conserve le personnage et son armature, avec anatomie générique adaptée à l'interprétation du portrait explicitement autorisée par le porteur. Les sources anatomiques CC0 et leur provenance sont dans `art_source/AnatomyBase/`. La transition du cou et ses poids ont été reconstruits, avec correction de la compression en conduite. Spectrum conserve la coque et le front inclinés depuis les photos de répliques ; sa base élargie suit maintenant les épaules par ses poids. La plage arrière masque le coffre. La plaque reprend le mot-symbole M.A.S.K. de l'image fournie, par UV éditables.

Utiliser la connexion MCP Blender installée, conformément à `AGENTS.md`. Le client `art_source/Thunderhawk/scripts/inspect_live_mcp.py` communique avec l'add-on sur localhost:9876. Les scripts de Matt se trouvent dans `art_source/Matt_Trakker/` ; revue, validation et exports V14 dans `art_source/Thunderhawk/scripts/`. Les outils paramétrables sont dans `art_source/shared_tools/` et le skill. Les passes intermédiaires sont conservées ; ne pas rejouer un script de construction sur une source déjà affinée sans examiner ses préconditions.

Les rendus et l'audit utilisent des tâches Blender différées : la réponse MCP de démarrage ne signifie pas que le travail est terminé. Vérifier les marqueurs `renders/v14/COMPLETE` et `docs/qa/validation_v14_COMPLETE`, ainsi que les rapports JSON. Ne pas lancer plusieurs files simultanément.

Le portrait est dessiné et les photographies montrent des figurines/répliques. Anatomie, proportions non documentées et bottines restent interprétées. L'habitacle interprété a été explicitement autorisé le 2 novembre 2026. La fidélité photoréaliste n'est pas validée. Le contrôle des collisions porte sur des surfaces aux images entières, sans certification de volumes ou de mouvement continu. La combinaison pénètre certaines surfaces rembourrées du siège ; la compression des tissus n'est pas simulée. Retopologie, UV, finition du visage et des déformations restent à réaliser. Aucune nouvelle importation Unreal dans cette passe.

## Historique V8

Les chemins et commandes ci-dessous concernent la V8 antérieure : étude extérieure articulée fondée sur les dix images fournies, sans cockpit.

- Source : `art_source/Thunderhawk/Thunderhawk_V8.blend`
- Générateur : `art_source/Thunderhawk/scripts/build_thunderhawk_v8.py`
- Rendus : `art_source/Thunderhawk/renders/v8/` (face, arrière, profil, dessus, perspective, vol et poses intermédiaires)
- Vidéos : `renders/v8/transformation.avi`, `renders/v8/turntable.avi` ; images JPEG sources conservées.
- Contrat : `docs/art/THK_asset_contract.md`
- Analyse des photos effectivement examinées : `docs/art/THK_reference_review_v7.md`
- Validation : `art_source/Thunderhawk/validation_v8.json`, `unreal/MASK_AssetLab/import_v8_result.json`

Reconstruction depuis ce dossier :

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b --python art_source/Thunderhawk/scripts/build_thunderhawk_v8.py
```

Le script remplace uniquement les sources et sorties V8 ; il ne modifie pas les images fournies ni les autres versions. `THK_FAST=1` saute les rendus.

Dans Unreal, ouvrir `unreal/MASK_AssetLab/MASK_AssetLab.uproject`, la carte `/Game/Maps/THK_V8_AssetTest`, puis la séquence `/Game/Thunderhawk_V8/THK_V8_RoundTrip`. L'import est indépendant de VehicularCombat. Le test animé utilise des meshes rigides et Sequencer ; ce n'est pas encore le rig squelettique final.

Préférence du porteur enregistrée dans `AGENTS.md` : demander des références visuelles pour les prochains véhicules, personnages et environnements si elles ne sont pas déjà disponibles.
