# Silent Valley — première boucle de mission

État au 10 novembre 2026 : V0 validée par 14 contrôles solo automatisés (slice-r8, sortie 0), HUD inspecté en rendu. Cette étape ne termine ni le réalisme du niveau ni la poursuite mobile prévue dans la spécification.

La carte indépendante démarre un directeur de mission serveur. Il lit `DA_SilentValley_01` : briefing, départ Boulder Hill, Pinewood, reconnaissance Eagle Pass, interception à Old Quarry, combat, récupération du module à l'arrêt, extraction à North Ridge. Les objectifs, la distance et la progression sont affichés dans le HUD. Le lancement avec `?Mission=0` conserve un parcours libre pour les tests de conduite.

L'adversaire réutilise le véhicule et le contrôleur IA existants, équipe 2. Il attend à la carrière avant activation ; ce n'est pas encore un convoi suivant la route. Le module est un cube temporaire sans collision. Aucun nouveau véhicule, personnage ou décor de référence n'a été modélisé.

Le serveur attribue 25 `TechComponents` et enregistre le GUID de l'exécution dans `MASK_SilentValley_Progress`. Les tests utilisent exclusivement un slot `SV_MissionTest_*` distinct. X/F6 après succès ou échec recharge la carte et réinitialise l'exécution. Les temporisations et la récompense sont modifiables dans le DataAsset.

Code : `Source/VehicularCombat/Private/SilentValley/SilentValleyMission.h/.cpp`. Intégration : GameMode, PlayerHUD, RPC de reprise du pawn possédé, entrée du conducteur à pied et transformation Thunderhawk en état terminal.

Validation : `Tools/Migration/Test-SilentValley-Mission.ps1 -RunName <unique>` exécute la vraie mission sur la carte sauvegardée. Le placement du joueur et la visée sont des fixtures explicites, pas une conduite ou visée manuelle. Les entrées de tir passent par l'arme existante, ses munitions, ses projectiles et les dégâts. La navigation/physique adverse et le tick de visée caméra du joueur sont figés pendant cette seule fixture balistique. La coop de mission, les déconnexions, le convoi mobile et les performances de combat restent à tester/implémenter.

Voir le rapport de validation dans `docs/tests/SILENT_VALLEY_SLICE_REPORT.md` pour les résultats effectifs et les limites.
