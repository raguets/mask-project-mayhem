# Une entrée de jeu M.A.S.K. Project Mayhem

Demande du 11 novembre : une seule carte jouable Pinewood et un seul lanceur. La flotte initiale de trois véhicules est désormais étendue à quatre avec Raven. Le nom artistique Pinewood désigne actuellement la carte technique `L_SilentValley_Blockout` ; aucun doublon de carte créé.

Le lanceur normal est `../../../Jouer-MASK.cmd`. Il utilise le projet Editor compilé et la carte actuelle, Thunderhawk et trois contrôleurs IA : Rhino, Hurricane et Raven. `CustomGameMode` exclut le véhicule initial de la liste des équipiers pour éviter de le dupliquer quand on démarre avec Raven. Les anciens lanceurs sont archivés en texte sous `Tools/LegacyLaunchers`. Les scripts de tests restent des outils de diagnostic. L'essai `Saved/Art/smoke-raven-r1` passe14 contrôles, dont les quatre familles présentes et le changement de Thunderhawk vers Raven sur cette carte.

## Mécanismes hérités

| Mécanisme | État du code / action |
|---|---|
| Physique Chaos, armes, munitions/rechargement, projectiles, dégâts, santé | Partagés par héritage ; déjà utilisés sur Silent Valley. Mission physique 14 contrôles passée dans `mission-natural-ballistic-r3`. |
| IA et changement de véhicule persistant | Déjà dans `CustomGameMode` ; la nouvelle entrée demande les deux équipiers. Vérifier les positions de spawn, leur équipe, les trois échanges et les états conservés. |
| Personnages, sortie/rentrée, transformation et module Rhino | Code partagé, pas de nouvelle copie nécessaire. Nouvelle régression de flotte et à pied sur la carte à effectuer. |
| Réapparition et pause | Hérités ; vérifier interaction avec l'échec/retry de mission avant de modifier leurs règles. |
| Bonus/armes posés dans l'ancienne carte | Les classes sont disponibles, leur implantation n'est pas automatiquement transférée. Inspecter les acteurs de l'ancienne carte avant de choisir des emplacements dans Pinewood. |
| Sessions LAN et retour au menu | `OnlineGameInstance` charge encore `MainMenu` et `Test` explicitement. Adapter ces transitions avant de retirer ces cartes du package. |

Le titre affiché a été changé en **M.A.S.K. Project Mayhem**. Le déplacement du projet à la racine reste à faire : résoudre les collisions README/LICENSE/docs, actualiser les chemins des outils et des exports, puis tester chargement, compilation et lancement. Conserver pour l'instant le nom du module C++ `VehicularCombat` évite des redirections inutiles de toutes les classes Blueprint. Ce nom interne peut rester distinct du titre du jeu. Ne pas supprimer les cartes historiques avant l'audit des références et transitions.

## Audit multijoueur du 11 novembre

Vérification du code et de la configuration, sans nouveau test réseau : `SilentValleyGameMode` hérite de `CustomGameMode` ; `DefaultEngine.ini` conserve `OnlineGameInstance`, avec le service `Null` par défaut. Création/recherche/jonction LAN et serveur hébergé par un joueur existent déjà. Les armes possédées, véhicules et états de mission utilisent réplication/RPC. Cela établit la réutilisation de l'architecture, pas la validation de la coopération sur Pinewood. Le lanceur actuel n'a pas `listen` : il démarre en solo.

À intégrer avant d'annoncer le multijoueur principal opérationnel : remplacer les destinations `Test`/`MainMenu` dans les parcours Solo/Host/retour ; garder les choix de flotte lors des voyages ; vérifier arrivée/départ d'un client, attribution de véhicules libres, switch sans prise du véhicule d'autrui, transformations/personnages, objectifs partagés, mort/réapparition/retry et récompenses. La sauvegarde de récompense actuelle est locale au serveur ; aucun partage individuel de progression client validé. Le support Internet/Steam ne découle pas du fonctionnement LAN.

Correctif du 11 novembre : `SilentValleyMission::Retry` conserve maintenant le nombre `Bots` configuré dans le GameMode, borné0–6, avec le véhicule choisi et `listen` si nécessaire. Le test de mission compte les équipiers réellement contrôlés par l'IA avant/après voyage (module arrière de Rhino exclu). `retry-fleet-r2` :16 contrôles passés,2 équipiers avant ET après, sortie0. [Rapport](../validation/silent-valley/retry-fleet/bots2.json). La compilation native r17 passe les4 actions exportées. Test réseau listen non exécuté dans ce lot.

Régression complémentaire `retry-solo-r3 -Bots 0` :16 contrôles passés,0 équipier avant ET après, sortie0. [Rapport sans équipiers](../validation/silent-valley/retry-fleet/bots0.json). Les slots de sauvegarde de test restent isolés ; aucune progression utilisateur modifiée par ces fixtures.

Les classes héritées de ravitaillement sont identifiées : `WeaponPickupActor`, `AmmoPickupActor`, `HealthPickupActor`, `SpeedBoostPickupActor` et `SpawnManagerActor` (réapparition temporisée). Leur présence dans le code ne démontre pas leur implantation dans Pinewood. Choisir ensuite les points d'armes/munitions/réparation ; l'accélération temporaire peut rester optionnelle selon le gameplay M.A.S.K. Aucun acteur de l'ancienne carte déplacé lors de cet audit.
