# Journal de migration UE 5.8

## 2026-11-06 — état initial

- `git rev-parse --show-toplevel`, `git status --short --branch`, `git remote -v`, `git log -1` : clone propre dans `VehicularCombat/`, origine DanialKama/VehicularCombat, commit `8d56e16`.
- `git switch -c migration/ue58` : branche créée. Aucun fichier existant supprimé ou écrasé.
- Lecture du descripteur, des cibles, dépendances, configurations, systèmes C++ et inventaire du contenu. Conclusions : `MIGRATION_AUDIT.md`.
- Moteur 5.8.2 et MSVC détectés. Disponibilité effective du SDK Windows à établir par UBT.

Les logs bruts locaux seront conservés dans `Saved/Migration/`. Aucun test de compilation, Blueprint, carte ou jeu n'est encore déclaré réussi.

## Compilation 01 — référence sans modification du code

Commande PowerShell (depuis le dépôt) :

```powershell
& 'G:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' VehicularCombatEditor Win64 Development '-Project=G:/DEV/mask-project-mayhem/VehicularCombat/VehicularCombat.uproject' -WaitMutex -NoHotReloadFromIDE -Unattended -NoUBA '-Log=G:/DEV/mask-project-mayhem/VehicularCombat/Saved/Migration/build-01-baseline.log'
```

Échec UBT avant compilation C++ : les defaults V2 changent des options partagées avec UnrealEditor (`bStrictConformanceMode` et niveaux d'avertissement). Correction minimale : cibles Game/Editor en `BuildSettingsVersion.V7` et ordre d'inclusion explicite `Unreal5_8`, association du projet en 5.8. Ne pas forcer un environnement partagé incompatible. L'avertissement MSVC 14.51 plus récent que les versions préférées est conservé ; pas de bannissement signalé.

## Compilations 02 et 03 — API et dépendances

Même commande UBT, logs `build-02-targets.log` puis `build-03-api.log`.

- 02 : UHT réussi ; compilation C++ échouée. Les `case 0/1/...` sur des `enum class` ne sont plus acceptés avec la conformité stricte. Remplacement par les noms d'énumération correspondants, sans changer leurs valeurs sérialisées. `OnlineSessionSettings.h` et `Online/OnlineSessionNames.h` doivent être inclus explicitement ; `SEARCH_PRESENCE` n'existe plus dans le moteur installé.
- Correction : `SEARCH_LOBBIES` pour les recherches en ligne ; les recherches LAN restent des recherches LAN. Création en ligne avec les indicateurs lobbies/présence cohérents. Dépendances explicites UMG et OnlineBase. Accès au propriétaire via GetOwner().
- **03 : Editor Win64 Development compilé et lié avec succès**, code de sortie 0, 31,85 s. UBT utilise le SDK Windows 10.0.26100.0. Les avertissements du moteur, RawInput déprécié et MSVC non préféré sont conservés et ne constituent pas des tests de jeu.

Le module conserve le nom `VehicularCombat`. Aucun contenu binaire modifié dans ce point de contrôle.

## Validation des Blueprints — premières passes

- `UnrealEditor-Cmd.exe <projet> -run=CompileAllBlueprints -ProjectOnly ...` : interrompu après constat que ce moteur ne propose pas ce filtre. Il parcourait aussi des Blueprints du moteur.
- Lecture du commandlet installé, puis liste explicite des chemins d'objets du projet dans `Tools/Migration/project-assets.allowlist`. Un premier passage du paramètre non entièrement cité a été mal interprété par PowerShell ; corrigé en citant `'-AllowListFile=Tools/Migration/project-assets.allowlist'`.
- La passe projet suivante a chargé/compilé ses Blueprints mais est sortie avec le code 1 : **ensure de configuration** `r.Mobile.VirtualTextures` obsolète. Suppression de cette ancienne clé, équivalente à `r.VirtualTextures=False` déjà présent ; conversion de `r.Mobile.Forward.EnableLocalLights=True` en valeur numérique 1. Aucun avertissement masqué. Résultat final à établir après ces corrections.
- Les catégories des commandlets et LogTemp sont explicitement activées dans Core.Log ; l'ancien réglage global warning empêchait de voir leurs résumés et les étapes de la sonde.

## Corrections fonctionnelles et compilations 04 à 11

Toutes les compilations Editor 04–11 ont réussi. Logs bruts `build-04-runtime-tests.log` à `build-10-impact-fixture.log`, puis `VehicularCombatEditor-*.log` pour le wrapper reproductible de la passe 11. Aucune installation système.

- Sessions : Super::Init, delegates raccordés et retirés à Shutdown, nom unique `NAME_GameSession`, garde des interfaces/index/résultats, nombre de places correct et mêmes recherches pour les deux surcharges. Signatures Blueprint conservées.
- Hôte listen-server : initialisation de la vue, du dashboard et mise à jour UI pour `IsLocallyControlled()`, sans limiter le traitement au rôle AutonomousProxy. Accès UI protégés lorsque les widgets ne sont pas encore prêts.
- Collision : les profils `Weapon`, `Pickup` et `CollisionBound` utilisés par le C++ manquaient dans le clone. Profils restaurés, arme équipée en requêtes de type Vehicle (ignorées par les traces de suspension), attache sans soudure des corps. Les ramassables gardent leur physique de monde et leur trigger distinct.
- Tir : un cooldown/chargeur vide ne doit pas faire échouer la validation réseau et expulser un client. Les garde-fous de gameplay restent dans les implémentations serveur. Chargeur initial zéro rempli conformément au commentaire existant, valeurs positives conservées. Les balayages des projectiles ignorent le tireur et ses accessoires.
- Dégâts : vérification de la bonne table explosive au chargement. Les projectiles cosmétiques locaux des clients ne sont plus traités comme une autorité de dégâts, même si leur rôle local vaut Authority. Le prototype conserve son schéma de projectiles visuels multicast et leurs effets locaux sur chaque pair.
- Réapparition : consommation d'une copie de la file, contrôleurs uniques/valides, RestartPlayer natif, retrait d'un joueur sortant et garde pendant la destruction du monde.

## Essais réels à deux processus

Lancement : `Tools/Migration/Test-TwoPlayers.ps1`. Rapports et commandes exactes dans `Saved/Migration/runs/<nom>/`. Les marqueurs de fichiers ne servent qu'à synchroniser les étapes ; aucun état de jeu n'est transmis par eux. Le serveur et le client communiquent via OnlineSubsystemNull et IpNetDriver.

| Essai | Résultat exécuté |
|---|---|
| `baseline-net` | Création/recherche/connexion et deux pawns réussis. Échec : contrainte Chaos autoréférente, puis débordement réseau. Essai arrêté ; échec conservé. |
| `collisions-net` | Déplacement, quatre roues en contact et réplication bidirectionnelle réussis après correction des profils/attaches. Déconnexion sur validation de tir : corrigée. |
| `firing-net`, `projectile-net` | Connexions conservées, réapparition observée ; sonde de combat invalide : plusieurs phases avançaient dans la même image avant traitement des entrées. Mesures prises trop tôt ; résultats non déclarés réussis. |
| `sequenced-net` | Après correction du chronométrage : tirs client/serveur et munitions réussis. Échec du scénario d'impact : téléportation du pawn autonome provoquant ses corrections physiques. |
| **`impact-net`** | **Réussi, deux sorties 0, environ 34 s de scénario**. Conduite des deux véhicules, 4 roues en contact, mouvement reçu dans les deux sens, tirs du client reçus sur le serveur, munitions répliquées, projectile du fusil touchant réellement la cible, santé serveur 1000 → 915 et baisse observée sur le client, destruction et réapparition avec santé restaurée. |

Le scénario d'impact déplace uniquement le véhicule de l'hôte autoritaire, contrôle la direction du canon et appelle le vrai RPC de tir. Le tir client passe par les entrées du PlayerController. La mort suivante est un test distinct par injection de dégâts. Ce protocole ne constitue pas une validation humaine de la visée au réticule ou de l'ergonomie.

Les nouvelles vérifications du lance-roquettes et du rendu sont dans l'essai `final-render` ; ne pas les considérer réussies avant son rapport final et l'inspection des images. Steam/Internet, serveur dédié et pertes de paquets ne sont pas validés par ces essais LAN.

## Contrôles finaux exécutés

- `Invoke-UE58.ps1 -Task Assets` : **sortie 0**, `Assets-20261106-191120.log` ; 544 ressources validées, 544 messages de validité, y compris MainMenu et Test.
- `Invoke-UE58.ps1 -Task Blueprints` : **sortie 0**, `Blueprints-20261106-191355.log` ; **28 Blueprints, 0 erreur, 0 avertissement, 0 échec de chargement**.
- Cible Game Win64 Development : première passe échouée car `UBillboardComponent` n'était pas déclaré dans SpawnManagerActor.h (masqué par le PCH Editor). Déclaration anticipée explicite ; **passe 02 réussie**, `build-game-02.log`, 58,82 s. Editor reconstruit ensuite avec succès, 22,49 s.
- `final-render` : non réussi ; le premier démarrage graphique compilait les shaders plus longtemps que l'attente du client. Lanceur corrigé pour attendre le démarrage de la boucle de jeu de l'hôte.
- `warmed-render` : captures effectivement produites et inspectées. Hôte renversé au début du scénario, conduite non validée dans ce passage ; tirs, dégâts et réapparitions réussis, roquette créée sur les deux instances, chargeur consommé et données explosives reconnues. Ce passage n'est pas déclaré globalement réussi.
- **`graphics-confirm` : réussi avec rendu DirectX, sorties 0 des deux processus**, environ 46 s de scénario. Conduite/contact/réplication, fusil/impact/dégâts, roquette et réapparition réussis. `host-ready.png` et `host-after-fire.png` inspectés : carte et HUD visibles, véhicule debout. Le renversement du passage précédent n'a pas été reproduit dans cet essai après mise en cache ; pas de garantie de stabilité longue durée.
- Inspection graphique : la réserve de munitions affichait encore 999 sur l'hôte. Correction de la notification lors des changements d'arme côté autorité et de la synchronisation après création du HUD ; nouvelle vérification à effectuer. Les avertissements de captures de réflexion non construites restent visibles, sans `DisableAllScreenMessages`.

## Reconstruction des données de scène

Point de contrôle Git `f03e61e` avant conversion du contenu (sources et essais conservés). Commande réelle :

```powershell
& 'G:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' '<repo>/VehicularCombat.uproject' '-run=ResavePackages' '-Package=/Game/Maps/TestMaps/Test' -buildlighting -buildreflectioncaptures -quality=Preview -AllowCommandletRendering -ProjectOnly -MapsOnly -unattended -nosound -nosplash '-AbsLog=<repo>/Saved/Migration/build-scene-data.log'
```

Il s'agit d'une vraie reconstruction Unreal, pas de la création d'un registre vide pour masquer la référence manquante. Aucune installation de Swarm : l'exécutable fait partie du moteur déjà installé.

La reconstruction Lightmass et des captures de réflexion a terminé et sauvegardé `Test.umap` et un véritable `Test_BuiltData.uasset` de 19 931 782 octets. Le commandlet a néanmoins terminé avec le **code 1** : sa configuration, chargée au démarrage, contenait `MinimumiOSVersion=IOS_13`, valeur supprimée du moteur installé. Configuration corrigée en `IOS_15`, minimum effectivement défini dans ses en-têtes. Le code 1 de cette commande n'est pas présenté comme une réussite globale. Les contrôles suivants chargent la configuration corrigée et les données reconstruites.

Seule la carte de test a été resauvegardée ; ses données construites sont explicitement conservées dans Git malgré la règle générale `*_BuiltData.uasset`. Les versions originales restent dans l'historique, notamment `8d56e16` et le point de contrôle pré-conversion `f03e61e`. Éclairage de qualité Preview, pas une finition de production.

## Dernière passe après reconstruction

- `build-final-editor-console.txt` : Editor **Succeeded**, 22,89 s ; `build-final-game-console.txt` : Game **Succeeded**, 35,45 s.
- `release-candidate` : rapport automatisé vrai, deux sorties 0, 48 s ; dégâts réels 1000 → 925, 18 projectiles dont une roquette par pair, 14 événements d'impact locaux configurés et un effet d'expiration par pair. Aucun `LoadErrors` lié au cache manquant. Toutefois l'inspection des captures a révélé que l'arrangement de test plaçait l'hôte dans une rampe : ce passage ne constitue donc pas une validation graphique complète.
- Les captures confirment la correction du HUD : fusil, chargeur 30 puis 24, réserve 120 plutôt que le placeholder 999. L'avertissement de captures de réflexion non construites a disparu. L'image après tir montrait le véhicule sous la rampe : défaut de placement de la sonde à corriger, sans masquer l'image précédente.
- Sonde corrigée : recherche d'une empreinte de sol plane par cinq traces, à l'altitude de la cible ; repositionnement du seul hôte autoritaire ; nouveaux contrôles de contact au sol et d'orientation après le tir. Aucun changement de collision de la carte ou de physique du jeu pour faire passer le test.
- Dernière validation de contenu : `Assets-20261106-194050.log`, **545 ressources valides**, sortie 0 ; `Blueprints-20261106-194107.log`, **28 Blueprints, zéro erreur/avertissement/échec de chargement**, sortie 0.
- Compilation de la nouvelle sonde : `VehicularCombatEditor-20261106-194415.log`, **Succeeded**, 21,17 s.

## Validation finale conservée

- **`grounded-render` : réussi**, deux sorties 0, environ 47 s ; **23 contrôles hôte et 19 client**, tous vrais. Les nouveaux contrôles confirment le placement sur sol dégagé, les roues en contact et le véhicule droit après tir. Santé cible 1000 → 925 ; 18 projectiles dont une roquette sur chaque pair ; 17 événements locaux d'impact configurés et un effet d'expiration par pair. Aucun `Error:`, ensure ou `LoadErrors` dans les deux logs de cette passe.
- Les deux captures finales ont été inspectées puis copiées dans `docs/validation/`. Voiture droite au sol avant/après tir, carte et HUD visibles, fusil et munitions 30/120 puis 24/120. Aucun avertissement d'éclairage/réflexions non construits. Le test d'impact reste un arrangement automatisé, pas une visée humaine.
- Game reconstruit avec la dernière sonde : `VehicularCombat-20261106-194626.log`, **Succeeded**, 32,03 s. Aucun changement C++ ultérieur.

## Ouverture de l'éditeur et autotests du moteur

Les premiers lancements Editor avec `-ExecCmds=quit` ont initialisé le moteur mais ne se fermaient pas automatiquement ; ils ont été arrêtés explicitement, sorties -1, pas présentés comme des succès. `quit` convenait aux instances Game, pas à ce protocole Editor. La commande native Slate `CLOSE_SLATE_MAINFRAME`, confirmée dans `EditorServer.cpp`, permet l'arrêt normal.

Le diagnostic en français a identifié trois autotests du moteur en échec : `FUnifiedErrorTest_CreateErrorMessage`, `FUnifiedErrorTest_CreateErrorMessageWithContext`, `FStructuredLogFormatTest`. Leurs assertions comparent des textes/formatages anglais alors que la culture active est française ; exemple visible dans `UnifiedErrorTests.cpp` : comparaison exacte de `Empty error`, rendu localisé `Erreur vide`. Catégorie `LogAutomationTest=Log` activée pour conserver les noms/résultats, sans masquer les échecs.

Lancement vérifié avec culture anglaise **uniquement pour ce processus**, sans changer la langue du projet ni celle de Windows :

```powershell
$editor = 'G:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
$arguments = @('"<repo>/VehicularCombat.uproject"', '/Game/Maps/TestMaps/Test', '-unattended', '-nosound', '-nosplash', '-NullRHI', '-culture=en', '-ExecCmds=CLOSE_SLATE_MAINFRAME', '-LogCmds="LogInit Log,LogEditorServer Log,LogLoad Log,LogEngine Log"', '-AbsLog="<repo>/Saved/Migration/editor-open-en.log"')
$process = Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
$process.WaitForExit()
$process.ExitCode
```

Résultat : **sortie 0**, initialisation 14,49 s, MapCheck **0 erreur / 0 avertissement**, **429 autotests Smoke du moteur réussis, 0 échec, 0 erreur Automation** (`editor-open-en.log`). Le test anglais confirme le diagnostic de culture pour les trois échecs ; aucun moteur installé n'a été patché.

Une passe Editor avec rendu normal, mêmes projet/carte/culture et fermeture Slate a également atteint l'initialisation (22,17 s), MapCheck 0/0, puis fermé normalement (`editor-open-visible.log`). Son code de sortie n'a pas été récupéré par le lancement GUI direct PowerShell ; aucun code 0 n'est inventé pour cette passe. Les captures graphiques de jeu et la sortie 0 de la passe Editor NullRHI sont les preuves distinctes conservées. Aucun parcours manuel complet de l'interface Editor n'est revendiqué.

Les rapports synthétiques sont versionnés dans `docs/validation/ue58-validation.json`. Les logs bruts et essais intermédiaires demeurent sous `Saved/Migration/`. Aucune instance Editor ou Game de test n'est laissée ouverte.

## Correctifs après retour utilisateur — 6–7 novembre 2026

Le parcours des boutons Host/Join n'avait pas été couvert par la première sonde d'API. Reproduction dans l'éditeur : champ Host laissé vide, simple message `EMPTY` ; avec un nom saisi, création et chargement réussis mais sans retour clair. Join exigeait Refresh et ne proposait aucun adversaire sans autre serveur. Détails et fichiers dans `PLAYTEST_FIXES.md`.

- Menu d'origine reparenté à son extension native, sans remplacer son arbre Designer ; bouton Solo, nom prérempli et statuts ajoutés. Script reproductible via le PythonScriptPlugin déjà installé, chargé par `-EnablePlugins=PythonScriptPlugin -run=pythonscript -script=<repo>/Tools/Migration/Upgrade-Frontend.py`.
- Premières compilations : variable locale `Slot` masquant `UWidget::Slot` (C4458), renommée ; déduction `const auto*` sur un retour `TObjectPtr<APawn>` (C3535), remplacée par `const APawn*`. Avertissements non désactivés.
- Un avertissement UMG signalait un possible tick natif malgré le Blueprint configuré sans tick. La nouvelle classe n'implémente aucun NativeTick : métadonnée `DisableNativeTick` ajoutée conformément à son fonctionnement. Les 28 Blueprints compilent ensuite sans avertissement.
- La propriété Python `parent_class` n'est pas exposée sur ce WidgetBlueprint dans le moteur installé. Vérification d'héritage remplacée par `unreal.MathLibrary.class_is_child_of`, API confirmée dans `KismetMathLibrary.h`. Le script de reparentage termine avec sortie 0.
- Première sonde solo conservée en échec : recherche non déclenchée au clic Join, tirs IA trop fréquents, Échap quittant le jeu via les bindings d'origine. Recherche automatique ajoutée, période de grâce et cadence IA réduite, retour au menu affecté à F10.
- `Test-Solo.ps1 -RunName final-render -Render` : **19 contrôles réussis**, sortie 0, 39,17 s. Trois bots physiques, tirs/dégâts, tir joueur, réapparition d'un bot, retour au menu et relancement. Captures inspectées. La mort de test est une injection distincte explicitement déclarée.
- `Test-TwoPlayers.ps1 -RunName frontend-buttons -MenuButtons` : **réussi**, deux sorties 0, **24 contrôles hôte / 20 client**. Entrée par les vrais delegates des boutons Blueprint Host/Create Session et Join/ligne de serveur ; puis conduite, réplication, tirs/dégâts et réapparition. Aucun remplacement de cette entrée par l'appel direct au GameInstance.
- Derniers builds : Editor `VehicularCombatEditor-20261107-082929.log`, Game `VehicularCombat-20261107-083255.log`, réussis ; `Blueprints-20261107-083335.log` : 28, zéro erreur/avertissement/échec ; `Assets-20261107-083350.log` : 545 valides ; sorties 0.

Preuves de cette passe dans `docs/validation/training-frontend-validation.json`. Les limites Steam, packaging et licences de contenu de l'audit initial restent applicables. Aucun asset M.A.S.K. intégré.

### Ajustement visuel et clics réels

L'inspection d'une fenêtre normale a trouvé deux défauts supplémentaires : le graphe Host masquait le panneau ajouté aux enfants Canvas, et le panneau horizontal recouvrait une partie de la première ligne LAN. Restauration explicite de sa visibilité après le changement de page, ordre de dessin conservé au-dessus des panneaux, disposition verticale dans l'espace libre au-dessus des boutons de gauche.

Recompilations Editor/Game réussies : `VehicularCombatEditor-20261107-084641.log` (11,97 s), `VehicularCombat-20261107-084653.log` (24,56 s). `Test-Solo.ps1 -RunName sidebar-final -Render` : **19 contrôles réussis, sortie 0, 39,59 s**. `Blueprints-20261107-084821.log` : **28 Blueprints, zéro erreur/avertissement/échec**, sortie 0. Captures finales remplacées par cette passe dans `docs/validation/`.

Contrôle avec deux fenêtres normales et de vrais clics Windows : Host/Create Session puis Join/ligne `Partie locale`, connexion acceptée (résultat 0), véhicule client visible ; retour au menu avec F10 côté client puis hôte. Aucun `Error:`, fatal ou ensure dans leurs logs `manual-host-sidebar.log` et `manual-client-sidebar.log`. Ce parcours UI automatisé et inspecté complète les delegates testés en headless ; il ne constitue pas une recette humaine exhaustive. Le second processus est fermé et la fenêtre principale est laissée au menu pour l'essai utilisateur.

## Prototype Thunderhawk et manette Xbox — 7 novembre 2026

L'utilisateur a autorisé la réalisation des six étapes proposées, y compris l'intégration des assets, puis demandé les commandes Xbox et Matt masqué. Branche `feature/thunderhawk-playable` créée depuis le socle propre `13b02d6`. Sources originales conservées ; nouveaux assets isolés sous `Content/MASK/Thunderhawk`. Pas de changement de module, de suppression d'asset ou d'installation.

Commandes exécutées depuis le dépôt (les noms de rapports préservent les essais précédents) :

```powershell
& .\Tools\Migration\Invoke-UE58.ps1 -Task Build
& .\Tools\Migration\Invoke-UE58.ps1 -Task BuildGame
& .\Tools\Migration\Invoke-UE58.ps1 -Task Blueprints
& .\Tools\Migration\Invoke-UE58.ps1 -Task Assets
& .\Tools\Migration\Test-Thunderhawk.ps1 -RunName xbox-final-editor -Xbox -Render
& .\Tools\Migration\Package-Windows.ps1 -RunName MASK-Xbox-Development-r2
```

Dernière compilation Editor : `Saved/Migration/xbox-build-20.txt`, **Succeeded**, 14,38 s. BuildCookRun Win64 Development : `Saved/Migration/package-MASK-Xbox-Development-r2.txt`, **sortie 0 / BUILD SUCCESSFUL**, 87,32 s ; compilation Game, cuisson des deux cartes originales, stage/Pak/IoStore/archive réellement exécutés. Exécutable : `Saved/Packages/MASK-Xbox-Development-r2/Windows/VehicularCombat/Binaries/Win64/VehicularCombat.exe`. Lanceur local : `Jouer-MASK.cmd`.

Blueprints : `blueprints-mask-final.txt`, 29 compilés, 0 erreur, 0 avertissement, 0 échec de chargement. DataValidation : `assets-mask-final.txt`, 729 assets avec données valides, commandlet terminé normalement. Ces deux passes précèdent les derniers ajustements C++ de caméra/sonde ; le build et la cuisson finaux les complètent.

Erreurs importantes corrigées : conversion explicite de `TObjectPtr` ; DLL Editor verrouillée par une cuisson concurrente (opérations ensuite sérialisées) ; export FBX avec racine à 100 qui réduisait les offsets de suspension ; mauvais repère de corps/sockets ; transformation à l'identité du composant racine qui téléportait le véhicule ; deux caméras actives et spring arms sans tick ; double initialisation HUD. L'import LOD requiert le sous-système StaticMeshEditor de l'éditeur complet ; l'éditeur complet NullRHI a échoué dans cet environnement, tandis que le commandlet NullRHI convient à la petite finalisation. Les métaux noirs de la cuisson diffuse ont été corrigés par cuisson de couleur en émission temporaire, puis restauration PBR.

La sonde Xbox a été corrigée indépendamment du produit : constructeur d'événement `CreateSimulated`, un échantillon analogique absolu par axe/image, conduite pendant au moins 60 images malgré les captures, mesure de la caméra affichée relativement au véhicule. `packaged-xbox-01` reste enregistré comme **échec 32/33**, sans requalification ; `xbox-final-editor` passe **33/33, sortie 0**, orbite réellement mesurée 142,88°. Le protocole injecte des événements Unreal/Slate ; aucune manette physique détectée par XInput (4 emplacements, statut 1167).

Le premier retour route réseau rencontrait un vrai volume bloquant de l'arène. Le parcours de test a été déplacé dans l'espace libre ; les obstacles et le refus de transformation restent actifs. L'essai `thunderhawk-network-03` passe 31 contrôles hôte et 25 client dans deux processus. Les derniers résultats sur la distribution Windows sont conservés dans `docs/validation/thunderhawk-xbox-validation.json` et `THUNDERHAWK_IMPLEMENTATION.md`.

Avertissements restants compris et conservés : MSVC 14.51 n'est pas la version préférée par UBT mais les compilations réussissent ; RawInput installé est annoncé déprécié par UE 5.8, tandis que les commandes Xbox utilisent XInput ; les plateformes non Windows ne disposent pas de SDK et ne sont pas ciblées. Les DLL optionnelles de profilage Intel sont absentes ; aucun profilage Intel n'est nécessaire au lancement. Aucun de ces messages n'est supprimé arbitrairement.

Les scripts d'art, les enseignements d'export et les limites du prototype sont documentés dans `UE_ART_PIPELINE.md` et `THUNDERHAWK_IMPLEMENTATION.md`. Le réseau validé reste LAN/local ; le vol est arcade, les canons de porte ne sont pas encore deux émetteurs dédiés et la pose debout n'est pas un personnage jouable à pied.

Distribution finale `MASK-Xbox-Development-r2`, commandes effectivement exécutées :

```powershell
$maskExe = (Resolve-Path 'Saved\Packages\MASK-Xbox-Development-r2\Windows\VehicularCombat\Binaries\Win64\VehicularCombat.exe').Path
& .\Tools\Migration\Test-Thunderhawk.ps1 -RunName packaged-xbox-final -Xbox -Render -GameExecutable $maskExe
& .\Tools\Migration\Test-TwoPlayers.ps1 -RunName packaged-mask-network-final -MenuButtons -RenderHost -Thunderhawk -GameExecutable $maskExe
& .\Tools\Migration\Test-Solo.ps1 -RunName packaged-mask-solo-final -Thunderhawk -Render -GameExecutable $maskExe
& .\Tools\Migration\Test-Solo.ps1 -RunName packaged-original-solo-final -Render -GameExecutable $maskExe
```

Résultats : Xbox **33/33**, sortie 0, 60 images de conduite et 10,89 m parcourus ; réseau Thunderhawk **31 hôte + 25 client**, deux sorties 0 ; solo Thunderhawk **20/20**, 6 projectiles IA, santé minimale 825/1000 ; solo original **19/19**, 6 projectiles IA, santé minimale 900/1000. Le démarrage graphique à froid a retardé la découverte LAN dans le premier parcours ; les nouvelles recherches ont trouvé la session et le test a terminé sans correction ni contournement de Join.

Les logs de ces essais ne contiennent ni fatal, ni ensure, ni erreur de ressorts superposés. Les deux processus sous le même compte Windows partagent l'identité NULL et produisent un avertissement d'appartenance de session au raccordement ; création, découverte, connexion et réplication ont néanmoins été vérifiées. Ce test ne certifie pas deux identités Steam. Le message Steam désactivé correspond au `-nosteam` explicite du protocole LAN. Les captures de route, masque debout, transformation, vol, cockpit et aide Xbox sont archivées sous `docs/validation/thunderhawk-*.png`.

Point de contrôle d'implémentation : `632f58a` (`Integrate playable Thunderhawk, masked Matt and Xbox controls`). Les empreintes des cinq fichiers éditables/provenance ont été recalculées et correspondent toutes à `SourceArt/MASK/Editable/source-checksums.json`.

Non-régression réseau du véhicule original sur la même distribution :

```powershell
& .\Tools\Migration\Test-TwoPlayers.ps1 -RunName packaged-original-network-final -MenuButtons -GameExecutable $maskExe
& .\Tools\Migration\Test-TwoPlayers.ps1 -RunName packaged-original-network-render -MenuButtons -RenderHost -GameExecutable $maskExe
```

Première passe, deux processus sans rendu : **échec**, mouvement initial hôte, observation de ce mouvement côté client et contact d'au moins trois roues côté client non validés (41/44). Le combat, les dégâts et la réapparition passent. La cause de cette différence n'est pas établie ; ne pas présenter cette passe comme réussie ni conclure sans preuve à une panne du matériel ou du réseau.

Seconde passe, hôte avec rendu et client sans rendu, même code/contenu : **réussie, 24 hôte + 20 client, deux sorties 0**. Le véhicule original roule et le mouvement est répliqué. Ces deux résultats distincts sont versionnés dans le rapport de validation ; aucune fonction n'a été désactivée pour les obtenir. Tous les processus lancés par les sondes sont fermés après les essais.

## 2026-11-07 — Rhino, Hurricane et sélection de la flotte

Branche `feature/rhino-vehicle-switch`, depuis l'état propre `cfab049`. Aucun original artistique ni asset supprimé. Détails : [FLEET_IMPLEMENTATION.md](FLEET_IMPLEMENTATION.md).

Commandes : `Invoke-UE58.ps1 -Task Build` (dernière passe 17 réussie), `Test-Fleet.ps1 -RunName editor-06 -Render` (réussite), `Test-Hurricane.ps1 -RunName editor-04 -Render` (22/22), `Test-TwoPlayers.ps1 -RunName fleet-network-editor-06 -Hurricane -DockFixture -RenderHost` (deux sorties 0), `Invoke-UE58.ps1 -Task Blueprints` (0 erreur/avertissement/échec de chargement), `Invoke-UE58.ps1 -Task Assets` (succès), `Package-Windows.ps1 -RunName MASK-Fleet-Development-r1` (distribution en cours de validation).

Les exports/revues `Tools/Art/prepare_*`, `repair_rhino_character_export.py` et `review_*` passent par le MCP Blender installé, port 9876. Les imports `import_rhino.py` et `import_hurricane.py` passent par l'éditeur complet GPU. Les deux finalisations de matériaux et `inspect_fleet_materials.py` utilisent des commandlets successifs, jeux fermés pour éviter leurs verrous de lecture.

Échecs conservés dans Saved : Rhino locaux 01–04 (dégagement, repère des roues, création moteur/transmission, freinage), 05 (comparaison de santé sur toute une période de jeu : remplacée par des mesures autour du transfert) ; réseaux 01–05 (obstacles, tri sur identifiants UObject recyclés, stationnement autonome). L'essai réseau 06 place explicitement le module au point d'amarrage APRÈS la conduite répliquée ; il ne valide pas un stationnement automatique. Les collisions et gardes de transformation restent actives.

Le rendu a révélé des matériaux squelettiques non persistés : réécriture des copies de structures dans le tableau, sauvegarde forcée avec retour contrôlé, puis relecture dans un NOUVEAU processus. Les huit corps/masques contrôlés ont tous leurs matériaux et atlas ; les deux meshes de cheveux sont aussi réaffectés. L'activation explicite de la réfraction corrige l'assertion Material.cpp du verre. Le proxy Thunderhawk quitte aussi la profondeur : captures A/B avant/après conservées.

Le contrôle XInput ne détecte aucune manette physique (1167 × 4). Les tests utilisent les événements Xbox dans le vrai jeu. Les avertissements moteur/MSVC/SDK des autres plateformes sont conservés ; aucun logiciel système n'est installé.

Distribution finale `MASK-Fleet-Development-r2` : BuildCookRun réussi, 65,89 s. r1 : 214,94 s. r2 corrige les vitres minces avec PixelNormalOffset ; le mode IOR volumique créait des aplats gris après cuisson. Les deux exécutables ont le même SHA-256 (voir validation/fleet/package-binaries.json). Contrôles : Hurricane r2 22/22 ; Rhino r1 41/41 ; Xbox/Thunderhawk r1 32/32 ; solo r1 20/20 ; réseau r2 via boutons Host/Create/Join, 43 contrôles hôte + 32 client, deux sorties 0, avec stationnement explicitement placé. Commande finale réseau : `Test-TwoPlayers.ps1 -RunName fleet-network-packaged-final -Hurricane -DockFixture -MenuButtons -RenderHost -GameExecutable <EXE_R2>`.

Le lanceur Jouer-MASK.cmd pointe vers r2. Point de contrôle validé : b05553b. Rapports et captures inspectées versionnés dans docs/validation/fleet ; limites et procédure dans FLEET_IMPLEMENTATION.md. Aucune instance de jeu/éditeur lancée par les tests n'est laissée ouverte.

## 2026-11-08 — Transformations en mouvement et dynamique

Branche `feature/moving-transform-dynamics`, créée depuis l'état propre `af3c168`. Aucun asset artistique ni fichier Blender modifié. Les paramètres de vol sont ajoutés aux définitions existantes sans renommer les modules ou les classes Blueprint. Détails : [DYNAMICS_IMPLEMENTATION.md](DYNAMICS_IMPLEMENTATION.md).

Commandes de compilation : `Invoke-UE58.ps1 -Task Build` (passes 01–09 réussies), puis `Invoke-UE58.ps1 -Task Blueprints` (0 erreur, 0 avertissement, 0 échec de chargement). Les avertissements moteur C4996, RawInput et compilateur MSVC plus récent que la version préférée sont conservés. Aucun logiciel installé.

Corrections issues des essais :

- Premier contrôle local : inclinaison hélicoptère aplatie par la priorité donnée au vecteur avant ; `MakeFromZX` conserve maintenant l'axe de poussée incliné. Le signe du roulis avion a été contrôlé avec le vecteur de l'aile droite et la trajectoire réelle.
- Premier réseau : le placement initial du corps prédit devait aussi être initialisé par le client de la sonde. Second réseau : le serveur attachait le module, mais le client pouvait conserver un ancien état de corps libre après le changement de possession. L'état monté répliqué rétablit maintenant attache, transformation relative et physique désactivée.
- Hurricane en mouvement : assertion Chaos `index 4 into array of size 4` en changeant le nombre de roues avec des résultats asynchrones encore en file. Six emplacements stables remplacent la reconstruction 6/4 ; la paire centrale rentrée est inactive. Les collisions restent actives.
- Collecteur PowerShell solo : le rôle scalaire était indexé comme une chaîne ; la liste des rôles est maintenant toujours un tableau.
- Ancien test Xbox : l'événement X est traité après l'injection ; la vérification observe maintenant l'état `Landing` lors des trames suivantes. Une grande plateforme temporaire remplace le sol limité de la carte d'acrobaties pour cette séquence où l'avion avance continuellement. Les essais en échec restent dans Saved.

Validation Editor : `Test-Dynamics.ps1 -RunName editor-04 -Render` (29/29 natifs ; collecte corrigée ensuite), `Test-Dynamics.ps1 -RunName network-editor-03 -Network -Render` (7 hôte + 22 client, deux sorties 0), `Test-Hurricane.ps1 -RunName moving-editor-02 -Render` (23/23), `Test-Thunderhawk.ps1 -RunName dynamics-editor-fixed -Render -Xbox` (32/32, sortie 0).

Première distribution `MASK-Dynamics-Development-r1` : `Package-Windows.ps1`, BuildCookRun réussi en 132,80 s. Essais sur cet exécutable : dynamique solo 29/29, réseau 7+22, Hurricane 23/23. L'ancien essai Xbox termine en échec avant son adaptation décrite ci-dessus ; il n'est pas compté comme une réussite.

Distribution finale `MASK-Dynamics-Development-r2` : BuildCookRun réussi en 95,71 s, puis `Test-Dynamics.ps1 -RunName packaged-r2 -Render` (29/29), `Test-Dynamics.ps1 -RunName network-packaged-r2 -Network -Render` (7 hôte + 22 client), `Test-Thunderhawk.ps1 -RunName dynamics-packaged-r2 -Render -Xbox` (32/32) et `Test-Hurricane.ps1 -RunName moving-packaged-r2 -Render` (23/23), tous avec `-GameExecutable` vers r2. Cinq sorties de processus 0. Freinage mesuré : 817,03 cm à 10 m/s contre 3230,54 cm à 20 m/s. Rapports, commandes de lancement, empreinte et captures inspectées dans `docs/validation/dynamics`. Le lanceur vise r2 ; aucun processus de test ou d'éditeur ne reste ouvert. Aucun asset ou fichier Blender modifié.

## 2026-11-08 — Stabilité arrière d'Hurricane et vol moins rapide

Branche `fix/hurricane-wheel-flight-speed`, depuis l'état propre `cfaf65c`. Sonde avant correction : `Test-Hurricane.ps1 -RunName wheel-baseline -WheelProbe -Render`, échec des quatre fenêtres de stabilité, oscillation de 12 cm sur chaque roue arrière. Les pointeurs vers les configurations CDO de roues étaient partagés ; rentrer la suspension centrale modifiait aussi l'arrière. Le nouveau composant conserve des configurations privées par roue/véhicule et la topologie stable à six roues. Vitesse maximale par défaut : 30 m/s au lieu de 60.

`Invoke-UE58.ps1 -Task Build`, passe 01 : échec LNK2019, dépendance directe `ChaosVehiclesCore` manquante pour les structures de configuration. Ajout de la dépendance ; passe 02 réussie. Aucun fichier moteur modifié. `Invoke-UE58.ps1 -Task Blueprints` : 0 erreur, 0 avertissement, 0 échec de chargement.

Editor : `Test-Hurricane.ps1 -RunName wheel-fixed-editor -WheelProbe -Render` (6/6, variation arrière nulle dans les deux fenêtres, 0 perte de contact sur 90 images de conduite, deux Hurricanes dans des modes différents) ; `Test-Dynamics.ps1 -RunName handling-editor -Render` (31/31, nouvelle mesure de vitesse maximale) ; `Test-Hurricane.ps1 -RunName handling-editor -Render` (23/23). Tous les processus terminent avec le code 0. Distribution finale et rapports : [HANDLING_FIXES.md](HANDLING_FIXES.md).

`Package-Windows.ps1 -RunName MASK-Handling-Development-r1` : succès en 116,92 s. Sur cet exécutable : `Test-Hurricane.ps1 -RunName wheel-handling-packaged -WheelProbe -Render` (6/6, variation arrière 0 cm, contacts conservés sur 89/89 images), `Test-Hurricane.ps1 -RunName handling-packaged -Render` (23/23), `Test-Dynamics.ps1 -RunName handling-packaged -Render` (31/31), `Test-Dynamics.ps1 -RunName handling-network-packaged -Network -Render` (7 hôte + 24 client), tous avec `-GameExecutable` vers la nouvelle distribution. Cinq sorties 0. Consigne de vol maximale 30 m/s ; vitesse réelle en palier après dix secondes RT ≈ 106,4 km/h. Lanceur actualisé, rapports dans `docs/validation/handling`. Aucun asset artistique modifié, tous les processus de test fermés.

## 2026-11-08 — Clarification : avions de 50 à 300 km/h

Branche `fix/aircraft-speed-range`, depuis l'état propre `872a295`. Min/max avion : `50/3.6` et `300/3.6` m/s. Rampe de consigne inchangée (8 m/s²), forces bornées et physique conservées. Puissance 600 kW pour surmonter la traînée à 300 km/h ; poussée maximale toujours 10 kN. Plafond hélicoptère séparé à 30 m/s pour conserver son réglage précédent. Aide Xbox actualisée. Aucun asset artistique modifié.

`Invoke-UE58.ps1 -Task Build`, passes 01 et 02 réussies ; `-Task Blueprints` : 0 erreur, 0 avertissement, 0 échec de chargement. `Package-Windows.ps1 -RunName MASK-Airspeed-Development-r1` réussi en 114,33 s. Ses essais solo et réseau passent avec les tolérances initiales, mais révèlent une vitesse réelle vers 296 km/h : l'amortissement du corps n'était pas compensé par la poussée. Compensation ajoutée puis tolérances resserrées à ±1 km/h au maximum et ±0,5 au minimum. Le premier package et ses rapports sont conservés ; ils ne sont pas la livraison finale. Résultats finaux : [AIRCRAFT_SPEED_RANGE.md](AIRCRAFT_SPEED_RANGE.md).

Distribution r2 : BuildCookRun réussi en 93,45 s, solo 35/35 ; réseau en échec sur les relevés client au minimum et au maximum (environ 51,6 et 303,2 km/h). R3 distingue les points physiques serveur (tolérances strictes inchangées) des relevés client (±2,5/±6 km/h), avec consignes exactes. Le gameplay ne change pas entre r2 et r3 ; seuls les contrôles réseau et la collecte de mesures changent.

R3 : compilation et cuisson réussies ; la copie d'archive manque d'espace disque. UAT affiche pourtant un succès après ses tentatives (226,67 s), mais le wrapper détecte l'exécutable absent. Compression NTFS sans perte des seuls EXE/PDB générés dans les packages airspeed r1–r3, le staging et Binaries/Win64 ; aucun fichier supprimé. Copie de l'EXE manquant depuis le staging terminé, puis comparaison SHA-256 des **50 fichiers** de l'archive avec le staging : tous identiques. La distribution n'est testée qu'après cette réparation vérifiée ; détail dans `docs/validation/airspeed/archive-verification.json`.

Validation finale sur r3 : `Test-Dynamics.ps1 -RunName airspeed-r3 -Render -GameExecutable <EXE_R3>` (35/35), `Test-Dynamics.ps1 -RunName airspeed-network-r3 -Network -Render -GameExecutable <EXE_R3>` (10 hôte + 28 client), trois sorties 0. Les trois points 50 → 300 → 50 passent les contrôles stricts sur le serveur ; les relevés côté client sont conservés séparément. Toutes les autres vérifications de la sonde passent aussi. Mesures et rapports dans `docs/validation/airspeed`. Lanceur actualisé vers r3 ; aucune instance de jeu/éditeur lancée par ces essais ne reste ouverte. Aucun asset artistique modifié.

## 2026-11-08 — conducteurs à pied

Branche `feature/on-foot-drivers` depuis le point propre `06ceb0a`. A quitte désormais un véhicule arrêté au sol et dégagé ; le même acteur, corps et masque sert au siège et à pied. Matt, Alex, Bruce et Hondo : marche/course/saut, caméra Xbox, masque visible/masqué et fusil existant. Le véhicule reste réservé/garé ; X remonte. Autorité serveur pour sortie/entrée, munitions, cadence et dégâts ; CharacterMovement pour le déplacement réseau. Les véhicules et sources Blender d'origine sont préservés. Les cinq assets Fab modifiés dans la session Editor de l'utilisateur ont été sauvegardés avant sa fermeture, puis exclus du commit de fonctionnalité.

Compilation Editor : passes 01–03 avec erreurs UHT/paramètres et includes corrigées ; passe 04 lien bloqué par la DLL de l'éditeur ouvert, après compilation C++ réussie ; sauvegarde puis fermeture normale de cet éditeur ; passes 05–11 réussies. Dernière compilation Editor 11 : 62,91 s, code 0. Les accesseurs de fréquence réseau remplacent les accès dépréciés du nouveau personnage. Les avertissements provenant des en-têtes moteur, MSVC 14.51 et RawInput restent visibles.

Blender MCP connecté sur le port installé 9876 : inspection des quatre rigs existants, conservation de session, création de 18 clips par rig et de quatre sources indépendantes. Les premiers rendus ont nécessité de créer explicitement les nœuds World et d'utiliser `view_layer.objects.active` depuis le callback timer Blender 5.2 ; les erreurs et sauvegardes intermédiaires restent dans Saved. L'import Unreal a d'abord échoué avec un chemin de projet relatif puis des propriétés FBX Python sans accesseurs directs ; chemin absolu et `set_editor_property` corrigent ces appels. `import-04` réussit : 72 séquences, quatre BlendSpaces et quatre références de définition. Les 20 rendus sont conservés et les captures Blender/jeu ont été inspectées. Contrôle supplémentaire sans modification d'asset : mêmes racines et positions des chevilles dans Blender/Unreal ; pas de décalage d'échelle d'import détecté.

Première sonde locale : retour Rhino impossible car la position latérale utilisait l'enveloppe complète de transformation. Les sorties suivent maintenant la largeur des roues et la position de cabine, avec capsule libre et contrôle de hauteur du sol. La sonde utilise le temps simulé pour ses durées de déplacement, et les noms d'os importés avec underscores. `editor-r3` : 40/40 ; `network-editor-r1` : 10 hôte + 20 client, sorties 0. La capsule et les projectiles bloquent désormais les conducteurs exposés ; balle hostile réelle, filtrage allié et mort/réapparition sont vérifiés en solo. CompileAllBlueprints : 0 erreur, 0 avertissement, 0 échec de chargement. DataValidation : succès.

Commandes de distribution : `Package-Windows.ps1 -RunName MASK-OnFoot-Development-r1` (176,12 s, succès), puis adaptation de la sonde Xbox historique : l'entrée de montée utilise le stick gauche, A est réservé à la sortie. `Package-Windows.ps1 -RunName MASK-OnFoot-Development-r2` (149,97 s, succès). Un manque de place durant l'archive r2 a provoqué des reprises automatiques de copie. Compression NTFS sans perte des archives/symboles/fichiers de compilation, aucune suppression ; contrôle final des 50 fichiers du staging contre l'archive par taille et SHA-256 : tous identiques. Rapport `docs/validation/onfoot/archive-integrity.json`. Pas de réparation artificielle par suppression d'assets et aucune installation.

Tests sur l'exécutable r2, tous avec rendu et sorties 0 : `Test-OnFoot.ps1 -RunName packaged-r2` 40/40 ; `Test-OnFoot.ps1 -RunName network-packaged-r2 -Network` 10 + 20 ; `Test-Dynamics.ps1 -RunName onfoot-packaged-r2` 35/35 ; `Test-Fleet.ps1 -RunName onfoot-packaged-r2` 41/41 ; `Test-Hurricane.ps1 -RunName onfoot-packaged-r2` 23/23 ; `Test-Thunderhawk.ps1 -RunName onfoot-xbox-packaged-r2 -Xbox` 32/32. Chaque commande inclut `-Render -GameExecutable <EXE_R2>` ; les arguments complets restent dans les launch.json et journaux de Saved. Rapports pérennes : `docs/validation/onfoot`. La manette XInput du slot 0 est détectée ; les essais de boutons restent injectés, pas manuels. Réseau local à deux instances, sans latence WAN artificielle.

Lanceur `Jouer-MASK.cmd` actualisé vers r2. Documentation, limites artistiques et procédure : `docs/ON_FOOT_IMPLEMENTATION.md`, `docs/XBOX_CONTROLS.md`. Entrée/sortie immédiates, doigts non articulés et prise de fusil approximative, pas de pouvoirs de masque ni d'IK de pieds sur terrain accidenté. Aucun test annoncé réussi sans exécution.
