# Silent Valley — mission V0 et matériaux

État vérifié le 10 novembre 2026. La maniabilité précédente, confirmée par l'utilisateur, reste conservée : [rapport dédié](HANDLING_TEST_REPORT.md). Aucun commit créé pour ce lot.

## Mission

`Tools/Migration/Test-SilentValley-Mission.ps1 -RunName slice-r8 -Render` : **14 contrôles réussis, sortie Unreal 0**. [Rapport brut](../validation/silent-valley/mission-v0/mission-r8.json). Vraie carte sauvegardée, directeur et données de mission de production, vrais projectiles/munitions/dégâts. Placement et visée de test explicites ; adversaire immobilisé pendant la fixture balistique. Ce résultat ne prouve pas une partie conduite à la manette ni une poursuite mobile.

Ordre des objectifs, extraction anticipée refusée, reconnaissance/spawn/activation IA, neutralisation, récupération à l'arrêt, extraction, récompense locale de 25 composants attribuée une fois, reprise par rechargement et échec après mort passent. Le slot `SV_MissionTest_slice-r8` isole entièrement la progression du joueur.

La roquette pouvait occulter ses propres traces de dégâts radiaux pendant `OnHit`. Le projectile est désormais ignoré par ces traces, l'origine étant décalée d'un centimètre hors de la surface touchée ; les autres obstacles continuent de bloquer les dégâts. Les essais précédents sont conservés sous `Saved/SilentValley/mission-slice-r2` à `r7`. Le test r7 a atteint la mort de l'adversaire puis a planté en lisant son composant de santé détruit : lecture optionnelle corrigée dans le test, r8 passe jusqu'au bout.

HUD récupération/succès inspecté en rendu. Les captures r8 montrent encore un avertissement de priorité des lumières et du chargement de ressources ; priorité soleil/fill séparée dans la passe asphalte suivante. Coop de mission, déconnexion, durée manuelle, reprise d'un convoi bloqué et package Windows **non testés**. Escorte issue du véhicule existant, module cube temporaire, convoi mobile non implémenté : [périmètre V0](../missions/MSN_SILENT_VALLEY_01.md).

## Niveau et surfaces

`refine_silent_valley_readability.py` : matériau terrain v4 adouci après inspection de v3, cinq panneaux recto/verso, dix poteaux sans collision, skylight/fill. Réouverture par `validate_silent_valley_readability.py` : matériau, route 9550,66 m, 39 instances PCG et alignement des textes passent. Dix vues `views-readability-r3` jour/soir ouvertes et inspectées ; trois exemples et les rapports sont sous [readability-v4](../validation/silent-valley/readability-v4).

Régression Rhino sur la passe v3 : 9548 m, écart maximal 0,923 m, aucun intervalle sans contact roue. V4 et asphalte ne changent aucune géométrie ni collision : pas de nouvelle validation physique revendiquée pour ces seules modifications de surface.

Passe suivante : `refine_silent_valley_asphalt.py`, matériau original `M_SV_RoadMarked_v3`, grain en coordonnées monde et rugosité, marquage existant conservé. 476 segments affectés, anciennes versions et sauvegarde map préservées. La validation visuelle de cette passe est consignée ci-dessous après captures.

Le niveau reste un blockout : grandes parois artificielles, carrière/ridge en dalles, accotements abrupts, végétation absente. Le matériau terrain procédural est une base. **G3 artistique non terminé ; aucun photoréalisme revendiqué.** Références/photos et ressources de végétation restent à préciser avant une nouvelle modélisation. Aucun achat, téléchargement ou installation.

## Compilation

UBT standard bloqué dans cette session par les écritures UBA AppData. Export UHT/actions avec `-NoUBTMakefiles`, puis commandes MSVC/lien/métadonnées exécutées par `Saved/SilentValley/run-exported-build.ps1`. L'export termine code 1 au nettoyage UBA ; ce n'est pas un build UBT standard réussi. Les commandes exportées passent : dernier lot `mission-actions-r11`, quatre sorties 0, DLL Editor à jour. [Preuve](../validation/silent-valley/mission-v0/build-r11.json). Packages non reconstruits. `git diff --check` passe.

Validation asphalte terminée : `Capture-SilentValley.ps1 -RunName asphalt-r1 -WorkspaceCache -TimeoutSeconds 600`, dix PNG 1600×900, sortie 0, tous inspectés jour/soir. Grain discret continu, marquage lisible ; limites artistiques du terrain inchangées. Réouverture indépendante réussie : asphalte v3 sur tous les segments et priorité soleil/fill distincte. Preuves sous `docs/validation/silent-valley/asphalt-v3`.
