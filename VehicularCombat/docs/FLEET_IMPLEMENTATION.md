# Flotte M.A.S.K. — Rhino et Hurricane

**Mise à jour du 8 novembre : [transformations en mouvement et nouvelle dynamique](DYNAMICS_IMPLEMENTATION.md).** Elle remplace les anciennes restrictions d'arrêt, le vol stationnaire de Thunderhawk et l'ancien stationnement du module. Les résultats ci-dessous conservent le périmètre de la livraison du 7 novembre.

Branche `feature/rhino-vehicle-switch`, Unreal Engine 5.8.2. Les sources artistiques originales et les anciennes distributions sont conservées. Aucun module n'est renommé.

## Utilisation

Dans le menu principal, **X** fait défiler Thunderhawk, Rhino, Hurricane et le véhicule original ; **Menu** lance le solo contre trois bots. La flotte M.A.S.K. mélange les trois véhicules. En partie, **croix haut/bas** passe au véhicule IA suivant/précédent : le joueur et l'IA échangent les mêmes véhicules, avec leurs équipages, armes, munitions, dégâts et mode courant. Les véhicules contrôlés par un autre humain sont exclus. **Menu** affiche les commandes ; elles n'occupent plus l'écran de conduite.

**X** transforme à faible vitesse et avec assez d'espace. Durées : Thunderhawk 2 s, Rhino/Hurricane 2,5 s, soit la moitié des pistes artistiques. Les refus de vitesse ou de dégagement restent actifs.

Rhino : Alex Sector/Jackrabbit reste dans le camion. Bruce Sato/Lifter est le même personnage, placé dans la cabine en route et transféré vers le siège du module pendant le déploiement. Les dix pneus restent répartis entre les deux parties ; le module possède six roues Chaos et devient un véhicule indépendant sélectionnable après séparation. Le compagnon partage l'équipe du camion, suit son partenaire et tire sur les adversaires ; les dégâts entre les deux parties alliées sont filtrés. **Aucune des deux parties ne vole.**

Hurricane : Hondo MacLean porte Blaster par défaut. Le même corps/squelette suit les 97 poses évaluées de la source V7 entre conduite et canonnier. Le toit, la levée modérée de 30 cm, les phares-canons, les canons bas, le canon à droite du pare-brise et le disque arrière suivent les pièces originales. Quatre roues participent à Chaos en route, six en combat ; les six pneus sont persistants. **LB maintenu + Y** projette l'acteur unique de la roue de secours vers l'arrière, une fois par véhicule ; Y seul conserve le changement d'arme. Hurricane reste au sol.

Commandes complètes : [XBOX_CONTROLS.md](XBOX_CONTROLS.md).

## Corrections de rendu et conservation

Les rectangles noirs de Thunderhawk provenaient du proxy physique encore présent dans la passe de profondeur. Il quitte désormais les passes couleur/profondeur, les ombres et le ray tracing. Les captures A/B ne changent que cette passe pour démontrer la cause. Les blocs techniques des scènes dérivées restent cachés en rendu et en vue normale.

Les masques Rhino étaient exportés dans un repère périmé quand leurs objets étaient cachés. Les copies dérivées ont été recalées et rendues à nouveau. Les sources V3 ne sont pas altérées. Les matériaux de tous les personnages ont aussi été réaffectés et leur persistance contrôlée après réouverture : l'API Python copiait les structures sans les réécrire dans le tableau.

Les sources indépendantes et les empreintes sont dans [SourceArt/MASK/Editable](../SourceArt/MASK/Editable/FLEET_README.md). Les FBX, atlas et pistes sont conservés dans `SourceArt/MASK/Rhino` et `SourceArt/MASK/Hurricane`. Les scripts d'export/revue utilisent le MCP Blender installé ; les scripts d'import utilisent l'éditeur Unreal complet. La méthode capitalisée est décrite dans [UE_ART_PIPELINE.md](UE_ART_PIPELINE.md).

## Limites connues

- L'IA est celle du prototype, enrichie d'une escorte et de points de contournement locaux. Le stationnement autonome du module vers le camion reste peu fiable près des obstacles. Pour réunir Rhino, rapprocher manuellement le module du point arrière droit de déploiement, immobiliser les deux véhicules, reprendre le camion puis X. Un module occupé par un autre humain, trop éloigné ou encore mobile empêche le rassemblement.
- Le test local de réunion utilise un placement explicite après les contrôles de conduite/escorte. Le test réseau avec `-DockFixture` fait de même côté autorité après la conduite répliquée. Ces placements isolent le contrôle du mécanisme ; ils ne valident pas un stationnement autonome. Les essais sans ce placement et leurs blocages sont conservés.
- Les tirs, dégâts et armes restent ceux du système original. Les canons artistiques ne sont pas encore autant d'armes indépendantes ; les pouvoirs des masques, les dégâts spécifiques de la scie et de la roue projetée ne sont pas implémentés.
- Le transfert de Bruce est une transition de pose/placement, sans animation de déplacement à pied. Le rattachement d'un module survivant à un nouveau camion après destruction reste à définir.
- Les masses, ressorts, freinages, enveloppes et vitesses de projection sont des réglages estimés de prototype. La conduite arcade et la navigation ne constituent pas une simulation fidèle de chaque véhicule.
- Les tests injectent les événements Xbox dans Unreal. Le contrôle XInput ne détecte aucune manette physique connectée (1167 sur les quatre emplacements) ; aucun essai matériel n'est revendiqué.

## Distribution vérifiée

`Saved/Packages/MASK-Fleet-Development-r2/Windows`, construite avec succès (BuildCookRun : 65,89 s). La première distribution r1 a également été conservée ; r2 corrige uniquement la réfraction des vitres minces. Les exécutables r1/r2 ont exactement la même empreinte SHA-256 : `024AB030BAC59238784AA92006BBDBD59B0E54615AFBB92789CC7DBCB6D7F48C`.

| Essai exécuté | Résultat | Périmètre |
|---|---|---|
| Hurricane, r2 avec rendu | 22/22, sortie 0 | Conduite, masque/matériaux, 4/6 roues, canonnier, tir, roue persistante projetée, sélection et pause |
| Rhino, r1 avec rendu | 41/41, sortie 0 | Conduite des deux parties, escorte/tir IA, échanges, dégâts/munitions conservés, réunion avec placement explicite |
| Thunderhawk/Xbox, r1 avec rendu | 32/32, sortie 0 | Deux joysticks, tir, caméras, mode route/vol, masque, pause et menus |
| Solo, r1 avec rendu | 20/20, sortie 0 | Menu, recherche LAN vide, trois adversaires principaux, combat/dégâts/réapparition et retour au menu |
| Deux instances réseau r2, Host/Create/Join | 43 hôte + 32 client, deux sorties 0 | Déplacements, tirs, dégâts/réapparition, échanges Rhino/module, Hurricane/canonnier/six roues/éjection ; stationnement par fixture explicite |
| Blueprints / assets | Succès | 0 erreur/avertissement/échec de chargement Blueprint ; DataValidation réussi |

Les tests r1 de comportement restent applicables au même binaire de jeu en r2 ; Hurricane et le réseau ont aussi été exécutés sur r2. Les rapports complets, l'empreinte et les captures inspectées sont dans [validation/fleet](validation/fleet/). La liste précise des fichiers est donnée dans [FLEET_FILES.md](FLEET_FILES.md).

Pour jouer :

1. Lancer `G:\DEV\mask-project-mayhem\VehicularCombat\Jouer-MASK.cmd`.
2. Dans le menu, appuyer deux fois sur **X** depuis Thunderhawk pour afficher **Hurricane**, puis **Menu** pour lancer le solo. Ou naviguer au stick/croix et valider avec A.
3. **RT/LT** : avancer/freiner ; **stick gauche** : direction ; **stick droit** : caméra ; **RB** : tirer ; **X** : transformation ; **LB + Y** en combat : roue de secours ; **croix haut/bas** : changer de véhicule ; **Menu** : commandes.

Pour ouvrir le projet source : ouvrir `VehicularCombat.uproject` avec l'installation UE 5.8, puis la carte `/Game/Maps/TestMaps/Test`. Le menu principal est `/Game/Maps/MainMenu`. Pour reconstruire la distribution sur ce poste : `Tools/Migration/Package-Windows.ps1 -RunName NOUVEAU_NOM`, puis adapter le chemin du lanceur. Les distributions dans `Saved` ne sont pas versionnées ; les sources et preuves de validation le sont.

Suites techniques : fiabiliser le stationnement véhicule avec un parcours tenant compte des volumes et rayons de braquage ; relier les canons artistiques aux armes propres à chaque véhicule ; définir les dégâts de la scie/roue et les pouvoirs des masques ; traiter la récupération d'un module survivant après destruction du camion.
