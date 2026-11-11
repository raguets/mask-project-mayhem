# Menu et entraînement solo — 6–7 novembre 2026

Suite au retour utilisateur après la migration UE 5.8. Les essais précédents validaient les API réseau, pas le parcours complet des boutons.

## Problèmes reproduits

- Host affichait « Session Name » comme hint sombre, sans valeur. Le Blueprint refusait le champ vide avant l'appel C++ et affichait seulement `EMPTY`. Avec un nom saisi, la création réussissait et la voiture finissait par apparaître, sans retour clair pendant l'attente.
- Join ouvrait un panneau vide ; la recherche ne démarrait qu'avec Refresh. Sans autre partie LAN, aucun adversaire n'était disponible.
- Le prototype original ne proposait aucun mode contre des bots.

## Corrections

Le menu `WBP_MainMenu` conserve son arbre Designer et ses graphes Host/Join/Settings. Il dérive maintenant de `UMainMenuWidget`, une extension native ajoutant le bouton **Solo contre 3 bots**, les messages de recherche/chargement/échec, un nom d'hôte prérempli lisible et une explication si ce nom est effacé. Join lance la recherche immédiatement ; Refresh reste disponible. Une recherche déjà en cours n'est pas remplacée par une seconde requête.

Le GameInstance utilise le sous-système Online associé au monde, notamment en PIE, et ferme la session précédente avant une nouvelle création ou un retour au menu. L'ouverture du terrain initial utilise explicitement `OpenLevel` avec l'option `listen`. Le mode solo ouvre la même carte avec `Bots=3`, sans créer de session réseau.

`AVehicleBotController` pilote les véritables véhicules Chaos et vise le joueur. Il utilise les armes, munitions, projectiles, dégâts et réapparitions d'origine. Une période de grâce et des tirs espacés rendent ce mode adapté à l'essai des commandes. Les bots portent une étiquette avec leur santé ; le HUD affiche également celle du joueur. **F10** retourne au menu. Échap garde son comportement original de sortie/arrêt PIE.

L'IA reste une IA d'entraînement simple : poursuite, arrêt à distance de tir, visibilité et récupération en marche arrière. Ce n'est pas un système tactique avec navigation routière, équipes, missions ou difficulté complète. Les bots sont activés uniquement par l'option `Bots`, pas dans les parties LAN ordinaires.

## Lancer une partie

Dans MainMenu, cliquer **Solo contre 3 bots**. Aucun autre joueur ni service réseau n'est nécessaire.

Lancement direct depuis PowerShell dans le dépôt :

```powershell
.\Tools\Migration\Invoke-UE58.ps1 -Task Solo
```

WASD ou flèches : conduire ; Espace : frein à main ; clic gauche : tirer ; 1/2 : armes ; V : caméra ; F10 : menu. Dans l'éditeur, cliquer dans la vue pour lui donner le clavier ; Maj+F1 libère le curseur.

Pour le LAN : Host → garder ou modifier le nom prérempli → Create Session ; attendre le chargement du terrain. Un **autre processus/joueur** utilise Join, puis clique sur la ligne de la partie trouvée. Join n'est pas nécessaire après Host et ne crée aucun bot.

## Validation

Les rapports d'intégration et captures sont conservés sous `Saved/Migration/`. Les résultats finaux et preuves sélectionnées sont ajoutés à `docs/validation/` après inspection.

- Première passe solo : échec conservé. Elle a révélé l'absence de recherche au clic Join, des bots trop agressifs pour l'entraînement et le conflit Échap avec la sortie d'origine. Ces points ont été corrigés ; F10 sert au retour.
- `gentle-render` : **19 contrôles réussis**, sortie 0, environ 39 s. Menu d'origine étendu, nom prérempli, recherche vide expliquée, trois bots possédant des véhicules et PlayerStates, conduite physique, tirs et dégâts réels, tir joueur, destruction/réapparition d'un bot, retour F10 et seconde partie sans duplication. Six projectiles de bots, deux du joueur ; santé minimale du joueur 850. Captures du menu et du combat inspectées.
- `final-render` : **mêmes 19 contrôles réussis après les dernières corrections**, sortie 0, 39,17 s ; six projectiles de bots, deux du joueur, santé minimale 850. Les captures finales montrent aussi la santé du joueur et les instructions F10.
- `frontend-buttons` : **deux processus LAN réussis**, sorties 0. L'hôte passe par les delegates des boutons Host puis Create Session ; le client passe par Join puis par la ligne de serveur créée par les Blueprints. Aucun appel direct CreateSession/FindSessions/TryJoinSession n'est utilisé comme entrée par cette variante du test. Conduite, contacts, réplication, fusil, lance-roquettes, dégâts et réapparition validés ensuite par la sonde d'intégration existante.
- Dernières cibles Editor et Game : **Succeeded** (`VehicularCombatEditor-20261107-082929.log`, `VehicularCombat-20261107-083255.log`). **28 Blueprints, 0 erreur, 0 avertissement, 0 échec de chargement** ; **545 ressources valides**, sorties 0 des deux commandlets (`Blueprints-20261107-083335.log`, `Assets-20261107-083350.log`).
- Vérification graphique supplémentaire : les graphes d'origine masquaient le bandeau sur Host ; sa première disposition recouvrait aussi la première ligne de serveur. Le panneau est désormais conservé visible sur Host et placé au-dessus de la navigation gauche, sans empiéter sur les formulaires ou serveurs.
- Passe finale après cet ajustement : `sidebar-final`, **19 contrôles réussis**, sortie 0, 39,59 s ; captures finales inspectées. Builds Editor/Game réussis (`VehicularCombatEditor-20261107-084641.log`, `VehicularCombat-20261107-084653.log`), nouvelle compilation des **28 Blueprints sans erreur ni avertissement** (`Blueprints-20261107-084821.log`). Le contenu reste celui des 545 ressources validées précédemment.
- Parcours graphique par vrais clics et touches Windows : lancement solo, F10, Host avec nom prérempli et LAN coché, Create Session, deuxième fenêtre Join, ligne `Partie locale` visible et cliquable, connexion acceptée et véhicule affiché, puis F10 côté client et hôte. Logs `manual-host-sidebar.log` et `manual-client-sidebar.log`. Le deuxième processus est fermé ; une seule fenêtre de jeu reste au menu pour l'utilisateur. Il s'agit d'une interaction UI automatisée inspectée visuellement, pas d'une longue recette humaine de conduite/visée.
- Le scénario automatisé active les véritables delegates des boutons UMG. La mort d'un bot est une injection explicite de dégâts pour vérifier son cycle de réapparition ; les tirs des bots et leurs dégâts sur le joueur utilisent les projectiles réels. L'audio est désactivé dans les scripts.

Commandes de reproduction :

```powershell
.\Tools\Migration\Test-Solo.ps1 -RunName nouveau-solo -Render
.\Tools\Migration\Test-TwoPlayers.ps1 -RunName nouveau-lan -MenuButtons
```

## Sources et contenu concernés

- `AI/VehicleBotController.*`, `UI/MainMenuWidget.*` : nouveaux contrôleur et extension de menu.
- `Core/CustomGameMode.*` : option Bots, placement sur sol libre et réapparition des bots.
- `Core/OnlineGameInstance.*` : lancement solo, statut, recherche et cycle des sessions.
- `Pawns/BaseWheeledVehiclePawn.*`, `PlayerWheeledVehiclePawn.*`, `UI/PlayerHUD.*` : commandes IA et garde des accès réservés au joueur, entrée F10 et affichage d'entraînement.
- `Content/UI/WBP_MainMenu.uasset` : reparentage conservant le menu original ; ancienne version dans Git au commit `32143c1`.
- `VehicularCombat.Build.cs` : dépendances AIModule/SlateCore.
- `Tests/TrainingSmoke.cpp`, `Tests/MigrationSmoke.cpp`, `Tools/Migration/Test-Solo.ps1`, `Test-TwoPlayers.ps1`, `Upgrade-Frontend.py`, `Invoke-UE58.ps1` : validation et lancement reproductibles. La commande `-Task TestSolo` lance le test avec rendu.

Les chemins C++ ci-dessus sont relatifs à `Source/VehicularCombat/Private/`, sauf Build.cs. Aucun asset M.A.S.K., fichier Blender ou véhicule artistique modifié. Aucun logiciel installé ; PythonScriptPlugin est fourni avec le moteur existant et chargé seulement pour le reparentage.

Preuves sélectionnées : [résumé machine](validation/training-frontend-validation.json), [menu et recherche vide](validation/training-menu.png), [combat solo](validation/training-combat.png). Le LAN comporte 24 contrôles hôte et 20 client, tous réussis ; l'IA des bots est validée en solo uniquement.
