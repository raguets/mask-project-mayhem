# Handoff — Condor dans Pinewoods — 12 novembre 2026

## Objectif et état réel

Intégrer Condor/Brad/Hocus Pocus et corriger les retours utilisateur : transformation en roulant, retour moto rapide avec freinage franc, accélération aérienne plus vive, suppression du balancement moto. Dernier signalement : support d’hélices semblant pénétrer la route. Route/hélicoptère : stationnaire au freinage maximal, nez légèrement baissé en avance ; Thunderhawk/Raven route/avion gardent leur vitesse minimale.

Art V20 enregistré et revu antérieurement : `art_source/Condor/Condor_V20_Assembly.blend`, véhicule indépendant V20, `art_source/Brad_Turner/BradTurner_V2.blend` et `HocusPocus_V2.blend`. Versions antérieures et Session_before_V16 préservées. Un même Brad/rig/tête, masque indépendant monobloc. Onze vues `renders/v20_review` inspectées, trois réouvertures indépendantes passent. `clearance_v20.json` vérifie 61 phases sélectionnées roue/support/carénage et patins solidaires. Limite connue : arc intermédiaire de roue sous le plan du sol ; garde au sol complète en transformation NON validée. Rapport historique : `docs/progress/2026-11-12-Condor-Brad-HocusPocus.md`.

Export jeu terminé : `art_source/GameReady/Condor/Condor_GameReady.blend`, `VehicularCombat/SourceArt/MASK/Condor` (12 groupes, deux pneus persistants, 97 échantillons), locomotion Brad18clips sous `SourceArt/MASK/OnFoot/Brad`. Import commandlet r3 passé : `Saved/Art/condor-import.json`, `condor-locomotion-import.json`, `condor-finalize.json`. Static LOD0 réduit conservé (sous-système LOD absent en commandlet), personnages LODs générés. Assets `/Game/MASK/Condor/BP_Condor`, DA_Condor et `/Game/MASK/OnFoot/Brad`.

## Code et réglages courants

Nouveau CondorPawn, deux classes de roue, équilibre par couples physiques, pose Brad suit la cassette siège, animation continue des deux rotors. Flotte/menu/retry et Jouer-MASK.cmd incluent Condor (Bots4). Sources principales : `Private/MASK/MaskDynamicsComponent.cpp`, `MaskVehicleModeComponent.cpp`, `ThunderhawkPawn.cpp`, `CondorPawn.*`, `MaskVehicleDefinition.h` ; scripts sous `Tools/Art` et `Tools/Migration`.

Dernières corrections compilées avec succès (build final16,13s) : correcteur roulis moto critique amorti36/12 plutôt que réponse aéronautique lente ; direction progressive adoucie ; volume de dégagement moto orienté selon le lacet pour éviter qu’il bascule dans la chaussée. Volume Condor relevé (centre150cm, demi-hauteur100cm), obstacles supérieurs/latéraux conservés. Pas de verrou de vitesse dans CanChangeVehicleMode de Condor.

Rotor : commande vitesse5→10m/s², inclinaison maximale12→22°, réponse horizontale doublée avec compensation amortissement, forces bornées. Retour : commande vitesse décroît au moins10m/s², inclinaison de freinage jusqu’à30° ; descente6m/s Condor,8m/s Raven/Thunderhawk, arrondi par distance de freinage près du sol. `Tools/Migration/Tune-AirLandings.ps1` exécuté avec succès ; `Saved/Art/air-landing-tuning.json` confirme8/8/6. Import Condor conserve ces paramètres.

## Vérifications et travaux en cours

Ancien smoke `smoke-condor-r2/condor.json` :19 contrôles passent (route, stationnaire, avance inclinée, virage, montée), mais timeout atterrissage ; donc intégration PAS entièrement validée. `condor-r3` PASSE25 contrôles, sortie0 : transformation à11,9m/s, stationnaire0,0034m/s, avance16,66m/s après5s, retour+rangement6,34s. Mais rendu avec virages alternés `condor-render-r1` ÉCHOUE (roulis86,88°, support−32,63cm), révélant le signe erroné du NOUVEAU correcteur. Signe corrigé (FRotator.Roll positif = rotation localeX négative), build13,49s réussi, log `Saved/Art/condor-balance-build.log`. `condor-render-r2` : équilibre et support PASSENT (pic11,25°, garde7,90cm), mais timeout Landing à8,46cm du sol, châssis droit sur pente. Nouveau critère rotor de contact : châssis droit (Up.Z>0,94), normale solZ>0,65, mêmes seuils hauteur/vitesse. Avions inchangés sur cet alignement. Build final13,40s réussi, `Saved/Art/condor-final-build.log`. `condor-render-r3` EN COURS exec29569 : fixture initiale200m en vallée au lieu800m en montagne. Aucun repositionnement en vol.

Support : `Saved/Art/condor-road-mesh-bounds.json` : bas support33,7cm, pneus0,109cm en position droite. Ne prouve pas sa garde en mouvement/suspension/pente. MCP Blender port9876 refusé (WinError10061) ; utilisateur informé et ouverture Blender/MCP demandée via question asynchrone. Ne pas substituer Blender batch ; inspecter la vraie source si reconnectée.

## Git et suite

Git réellement à la racine workspace, main, HEAD `c0ef9cd`. Aucun commit ni indexation. Changements code/launcher/AGENTS/HANDOFF + nouveaux Condor/Brad/sourceart/scripts. Nombreuses références déplacées par ailleurs vers `Images de reference/Terminés` (suppressions+nouveau dossier dans status) : préserver ces déplacements utilisateur.

Finir r3, diagnostiquer toute panne avec télémétrie. Vérifier virages moto alternés et garde support en jeu ; inspection rendue puis source MCP. Ensuite smoke rendu Condor, sortie/retour Brad (`Test-OnFoot.ps1 -Vehicle Condor`), régression Raven/Thunderhawk pour descente. Ne pas confondre compilation et validation dynamique/artistique.

## Première action recommandée

`Get-Content VehicularCombat/Saved/Art/smoke-condor-render-r3/progress.json; Get-Content VehicularCombat/Saved/Art/smoke-condor-render-r3/game.log -Tail 15`


