# Thunderhawk — intégration jouable et commandes Xbox

Travail autorisé le 7 novembre 2026 par « Réalise toutes ces étapes », puis précisé par la demande de commandes Xbox et de Matt masqué. Branche `feature/thunderhawk-playable`, issue de `13b02d6` sur `migration/ue58`. Unreal Engine installé : 5.8.2. Aucun moteur ou outil système installé, aucun module renommé, aucun asset original supprimé.

## Ouvrir et jouer

Double-cliquer `Jouer-MASK.cmd` à la racine de ce dépôt. Le lanceur ouvre la distribution Windows Development locale ; Unreal Editor n'est pas nécessaire pour cette distribution. Brancher la manette Xbox reconnue par Windows avant le lancement.

Thunderhawk est sélectionné par défaut et Matt porte Spectrum. Dans le menu, **Menu** lance une partie solo contre trois bots. Stick/croix naviguent, **A** valide et **B** revient. **X** dans le menu choisit Thunderhawk ou le véhicule original. Pour le réseau local : Host/Create Session sur une instance, Join puis ligne du serveur sur l'autre. Les statuts restent affichés.

En jeu : **RT/LT** accélération/frein et marche arrière, **stick gauche** direction, **stick droit** caméra, **RB** tir, **Y** arme, **X** transformation. Une fois transformé, **A/B** montent/descendent et le stick gauche vertical contrôle aussi l'altitude. Revenir près du sol avant X pour repasser en voiture. L'arrêt ou une faible vitesse et un volume libre sont requis ; le refus est affiché.

**R3** change de vue, **L3** recentre, **croix haut** affiche l'aide complète, **croix bas** montre le même Matt debout/assis à l'arrêt. **Menu** ouvre la pause ; A/B reprennent et Y retourne au menu principal. Le monde continue en multijoueur. Toutes les affectations sont dans `XBOX_CONTROLS.md` et dans l'aide du jeu.

Pour travailler dans Unreal : ouvrir `VehicularCombat.uproject` avec UE 5.8.2 ; compilation reproductible par `Tools/Migration/Invoke-UE58.ps1 -Task Build`. Les commandes et résultats de la migration initiale restent dans `MIGRATION_LOG.md` et `MIGRATION_RESULTS.md`.

## Implémentation

- `UMaskVehicleDefinition` conserve les références des meshes, les 16 groupes rigides, 97 échantillons de transformation, les deux poses et les paramètres du châssis.
- `UMaskVehicleModeComponent` valide les demandes côté serveur et réplique mode/heure de départ. Les clients évaluent les articulations localement. Le même corps Chaos sert à la route et au vol.
- `AThunderhawkPawn` dérive du véhicule original. Quatre pneus persistants suivent direction, rotation et suspension Chaos. Les modes route/vol échangent les fournisseurs de forces sans imposer la position du corps à chaque image.
- Le même Matt, son visage et son squelette sont utilisés assis/debout. Spectrum est un mesh distinct attaché à la pose, visible par défaut et répliqué. Aucun Matt supplémentaire pour les variantes. Le visage est conservé dessous ; les composants du pilote ne masquent pas la vue cockpit de leur propriétaire.
- Le menu original, le véhicule original, ses armes, projectiles, dégâts et réapparitions sont conservés. Thunderhawk possède son Blueprint et son dossier `/Game/MASK/Thunderhawk` ; une étiquette explicite garantit sa cuisson.
- Les deux sticks, les gâchettes et les boutons Xbox ont des affectations natives. La caméra conserve l'orbite choisie jusqu'à L3. Les menus et l'aide permettent le parcours solo sans souris.

## Sources et revue artistique

Les fichiers V14 du véhicule, V5 de Matt et V4 de Spectrum restent inchangés dans `../art_source`. Copies éditables et empreintes SHA-256 dans `SourceArt/MASK/Editable`, exports FBX/atlas/manifeste dans `SourceArt/MASK/Thunderhawk`. Les scripts sous `Tools/Art` ont été exécutés par le MCP Blender installé pour la préparation et les revues.

Les photographies fournies `images (9).jpg` et `images (2).jpg` montrent des jouets/répliques. Le visage humain est une interprétation autorisée du portrait illustré de Matt. Les références n'établissent pas des dimensions officielles : empattement de travail 2,82 m et rayon de pneu 0,328 m mesurés sur le modèle. La scène dérivée et cinq vues ont été rouvertes, rendues et inspectées dans `Saved/Art/game-review` ; les captures Unreal sont contrôlées séparément.

Le véhicule exporté contient environ 103 980 triangles au LOD0. Matt/cheveux/masque représentent environ 288 656 triangles au LOD0 ; les cheveux sont masqués quand Spectrum est équipé. Trois LOD sont générés pour les géométries concernées. Ce premier budget reste élevé pour une foule de pilotes. Les copies Blender contiennent encore des chemins d'images liés à l'espace de travail : elles ne constituent pas une livraison entièrement portable.

Les enseignements réutilisables sont dans `UE_ART_PIPELINE.md` : export squelettique en centimètres avec racine unitaire, poses explicites sur un seul squelette, atlas UV séparé et couleur cuite en émission temporaire avant restauration du PBR, import LOD dans l'éditeur complet et contrôle des sockets dans le repère de la vraie racine.

## Validation

La distribution finale est `Saved/Packages/MASK-Xbox-Development-r2/Windows` : BuildCookRun réussi en 87,32 s, sortie 0. Les résultats sont consignés dans `validation/thunderhawk-xbox-validation.json`. Les logs bruts locaux restent sous `Saved/Art` et `Saved/Migration`, ignorés par Git. Les événements Xbox injectés dans Unreal et Slate ne sont pas présentés comme un essai d'une manette physique : les contrôles XInput initial et final ne détectent aucun périphérique connecté.

| Essai sur cette distribution finale | Résultat | Preuve locale |
|---|---|---|
| Xbox : conduite, deux sticks, caméra, tir, masque, modes, altitude, pause et menu sans souris | 33/33, sortie 0 | `Saved/Art/smoke-packaged-xbox-final/summary.json` |
| Thunderhawk réseau : deux processus, vrais boutons Host/Create et Join/ligne, combat et transformation/vol/masque répliqués | 31 hôte + 25 client, deux sorties 0 | `Saved/Migration/runs/packaged-mask-network-final/summary.json` |
| Solo Thunderhawk et trois bots | 20/20, sortie 0, 6 projectiles IA, santé minimale 825/1000 | `Saved/Migration/training-packaged-mask-solo-final/summary.json` |
| Solo véhicule original et trois bots | 19/19, sortie 0, 6 projectiles IA, santé minimale 900/1000 | `Saved/Migration/training-packaged-original-solo-final/summary.json` |
| Réseau véhicule original : hôte avec rendu, client sans rendu | 24 hôte + 20 client, deux sorties 0 | `Saved/Migration/runs/packaged-original-network-render/summary.json` |

Captures inspectées : `validation/thunderhawk-road.png`, `thunderhawk-standing-mask.png`, `thunderhawk-transformed.png`, `thunderhawk-flight.png`, `thunderhawk-cockpit.png` et `thunderhawk-xbox-controls.png`. Le cockpit permet la vue sur la route, mais son tableau de bord reste sombre dans cette arène. Les avertissements d'identité NULL partagée par deux processus locaux sont conservés et expliqués dans le journal. Aucun avertissement de ressorts superposés ne subsiste dans ces essais après correction de l'ordre de configuration.

Contrôles déjà terminés avant la distribution finale :

| Essai | Résultat réellement obtenu | Preuve locale |
|---|---|---|
| Solo distribution initiale, véhicule original | 19 contrôles réussis, sortie 0 | `Saved/Migration/training-packaged-baseline-01/summary.json` |
| Réseau après correction caméra, véhicule original | 24 hôte + 20 client réussis | `Saved/Migration/runs/editor-camera-drive-01/summary.json` |
| Thunderhawk : physique, poses, masque, transformation, vol | 21 contrôles réussis | `Saved/Art/smoke-unit-root-04/summary.json` |
| Thunderhawk : deux processus réseau, sessions et combat, modes/masque/altitude | 31 hôte + 25 client réussis | `Saved/Migration/runs/thunderhawk-network-03/summary.json` |
| Compilation des Blueprints incluant Thunderhawk | 0 erreur, 0 avertissement, 0 échec de chargement | `Saved/Migration/blueprints-mask-final.txt` |
| Validation des données | 729 assets valides, commandlet terminé normalement | `Saved/Migration/assets-mask-final.txt` |

Les dégâts par projectile sont observés séparément des dégâts mortels injectés par les sondes pour vérifier rapidement la réapparition. Le réseau testé est local, avec deux vrais processus ; Steam, Internet, pertes réseau et serveur dédié n'ont pas été validés. Les captures inspectées ne remplacent pas une appréciation humaine du pilotage.

La passe supplémentaire `packaged-original-network-final`, avec les deux processus sans rendu, reste en échec (41/44) : conduite initiale hôte, observation côté client et contact des roues client. La passe avec rendu ci-dessus réussit sans modification du code ou des assets. La cause exacte de cette différence reste à isoler ; le comportement entièrement headless du véhicule original n'est pas validé.

## Corrections et essais historiques

Les essais en échec sont conservés et ne sont pas comptés comme réussis. L'import squelettique initial avec racine à 100 réduisait les positions de suspension ; l'export normalisé à racine unitaire a corrigé la physique. Le reset de transform d'un composant racine déplaçait le véhicule à l'origine ; il a été supprimé. Les sockets des armes emploient maintenant la vraie racine importée. La configuration des roues est appliquée avant le remplacement du mesh.

La première cuisson diffuse rendait les métaux noirs ; cuisson de couleur par émission temporaire et UV de logo préservés. La première exportation de pose lisait le rig non évalué ; les deux clips utilisent maintenant les matrices évaluées et restent sur le même squelette.

Le premier test réseau Thunderhawk rencontrait un vrai BlockingVolume de l'arène lors du retour route : le parcours de la sonde a été corrigé pour rester dans un volume libre, sans désactiver les obstacles. Les requêtes utilisent le contrat de collision Vehicle pour respecter les pickups qui ignorent déjà les véhicules.

Les premières sondes Xbox utilisaient le mauvais constructeur d'événement et additionnaient plusieurs échantillons analogiques dans une image. Elles utilisent désormais `CreateSimulated`, un échantillon absolu par axe/image et au moins 60 images de conduite. L'essai Windows `packaged-xbox-01` termine avec 32 contrôles sur 33 : la mesure d'orbite comparait un contrôle initial différent de la vue et une rotation monde pouvant être compensée par le virage. La sonde finale compare la caméra affichée relativement au véhicule ; l'ancien résultat reste en échec. Le cadrage cockpit hérité du sedan est remplacé par celui du nouvel habitacle.

## Limites et suite

Le vol est un pilotage arcade stabilisé. La collision fonctionnelle est celle du châssis, pas une simulation indépendante de chaque porte/aile. La vérification de dégagement est conservatrice ; elle ne certifie pas chaque contact géométrique sur toute la course. La pose debout n'est pas un système de sortie du véhicule ou de marche à pied. Les pouvoirs de Spectrum, les missions coopératives et les appareils aériens dédiés restent à développer.

Le combat utilise les armes et modèles d'armes originaux, montés sur le véhicule ; les deux canons de porte restent des pièces distinctes mais ne sont pas encore deux émetteurs de tirs spécifiques. Les matériaux exportés ne reproduisent pas tous les petits reliefs procéduraux Blender. La fidélité des références illustrées et la déformation du personnage conservent les limites déjà relevées dans les sources. Les licences de contenus tiers et des images/logos M.A.S.K. restent à vérifier avant diffusion publique.

Prochaines étapes : essai humain de la manette et réglage de sensibilité ; tirs depuis les deux canons de porte ; affinement des collisions articulées et du vol réseau sous latence ; personnage possédable à pied et pouvoirs du masque ; réduction du coût des cheveux, empaquetage portable des sources et revue des droits avant publication. Les responsabilités extensibles et les futures familles de véhicules sont décrites dans `MASK_ARCHITECTURE_PROPOSAL.md`.

Point de contrôle du code et des assets : `632f58a`. Liste exhaustive des fichiers : [THUNDERHAWK_FILES.md](THUNDERHAWK_FILES.md). Les résultats et captures sont conservés dans un second point de contrôle documentaire, sur la même branche.
