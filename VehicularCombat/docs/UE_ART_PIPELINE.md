# Export Blender vers Unreal : méthode vérifiée

Les sources originales restent dans `../art_source`. Les copies inchangées du véhicule, de Matt et de Spectrum, ainsi que la scène de préparation, sont conservées dans `SourceArt/MASK/Editable` avec leurs empreintes SHA-256. Les images de référence et certains chemins de textures restent liés à l'espace de travail d'origine ; ces copies ne sont pas présentées comme un paquet Blender entièrement autonome.

## Géométrie et textures

Travailler sur une scène dérivée par le MCP Blender installé. Garder les sources indépendantes. Exclure références, cages et anciennes mains. Préserver les groupes de déformation en évaluant les autres modificateurs avec l'armature en repos. Une réduction par effondrement ne garantit pas le budget demandé sur des milliers d'îlots de cheveux : mesurer le résultat.

Regrouper les pièces rigides par articulation ; conserver un maillage et un pivot distincts pour chaque mécanisme. Ici, 16 composants et 97 échantillons décrivent l'aller de la transformation, sans envoyer un paquet réseau par pièce et par image. Les quatre pneus persistants suivent les quatre roues Chaos.

Cuire la couleur procédurale par émission temporaire, puis restaurer le shader. Une cuisson diffuse assombrit fortement les métaux. Créer un atlas UV distinct, conserver les UV source du logo pendant la cuisson, puis exporter cet atlas en UV0. Les valeurs de métal et de rugosité servent aux instances PBR ; les petits reliefs procéduraux ne sont pas tous reproduits par des textures normales. Le verre utilise un matériau translucide distinct, légèrement teinté et réfléchissant.

## Squelettes et physique

Conserver les scènes artistiques en mètres. Pour le FBX squelettique, créer des copies en centimètres : géométrie, positions des os et translations des poses multipliées par 100, scène à 0,01 m/unité, transformations d'objet unitaires. Exporter les clips debout/assis séparément sur le même squelette. Ne pas exporter toutes les actions de la scène : elles incluent aussi des actions du véhicule.

Vérifier dans Unreal que la racine importée a une échelle `(1,1,1)`. Une racine à 100 n'est pas anodine : Chaos inverse sa matrice pour calculer les positions de suspension, ce qui réduit les offsets de roues par 100. Les valeurs de référence de Thunderhawk sont X=140/-142 cm, Y=±81,8 cm, Z=32,8 cm, rayon 32,8 cm ; ce sont des dimensions de travail issues du modèle.

Le corps simulé doit piloter l'os racine réellement importé, ici l'os d'armature supplémentaire conservé par FBX. Les formes de collision et sockets sont exprimés dans son repère. Ne pas utiliser le nom `root` sans vérifier la hiérarchie. Ne pas remettre à l'identité la transformation du composant racine d'un acteur déjà placé : cela modifie sa position dans le monde.

Après remplacement du mesh, du PhysicsAsset et des définitions de roues, recréer la simulation à partir de la configuration finale. Conserver un seul corps physique pour route/vol et échanger les fournisseurs de forces, sans écraser sa transformation à chaque image.

## Import et contrôles

1. `prepare_thunderhawk_game.py` : scène de jeu dérivée, géométrie, atlas et pistes.
2. `export_normalized_skeletons.py` : FBX en centimètres et deux clips explicites, racine unitaire.
3. `import_thunderhawk.py` : import, enregistrement explicite des squelettes, matériaux, LOD et Blueprint dédié.
4. `finalize_thunderhawk.py` : châssis et sockets cohérents avec la racine, étiquette de cuisson explicite.
5. Compilation, réouverture des assets, tests réels de contact au sol, conduite, masque, transformation et vol ; puis deux processus réseau et distribution Windows.

Les opérations Blender passent par MCP et les scripts d'export n'écrasent pas V14/V5/V4. Le sous-système StaticMeshEditor doit être initialisé pour créer les LOD : le commandlet Python minimal ne suffit pas. Utiliser l'éditeur complet avec son rendu normal pour cet import. L'éditeur complet avec NullRHI a échoué dans cet environnement ; le commandlet minimal reste utilisable pour la petite finalisation.

Les captures de revue sont dans `Saved/Art/game-review`. Les tests et leurs échecs historiques restent dans `Saved/Art` et `Saved/Migration`. Les limitations de collision, de pilotage et de validation humaine sont consignées dans `THUNDERHAWK_IMPLEMENTATION.md`. Une sauvegarde ou un export seul ne valide pas la fidélité artistique.

## Retours de l'intégration Rhino et Hurricane

- Un proxy physique caché doit quitter **les passes couleur et profondeur**, les ombres et le ray tracing. Le laisser dans la profondeur produit des rectangles noirs sur les vrais capot/coffre. Comparer deux captures en ne changeant que cette passe permet d'en établir la cause ; ne pas ajouter des caches ou recolorer la carrosserie.
- Dévoiler temporairement les objets pilotés par `hide_viewport`, mettre à jour le graphe puis capturer leur matrice de repos. Un masque masqué pouvait conserver une ancienne matrice et subir deux fois le décalage du personnage à l'export. Corriger les copies dérivées, conserver les originaux et rendre les deux poses.
- Une remorque jouable possède son propre repère de physique. Recentrer ses os de roues autour de son origine pour que le centre de masse soit dans le polygone des suspensions. Décaler séparément la présentation évite de modifier les pièces artistiques. Les dix pneus Rhino restent persistants et sont répartis entre camion et module.
- Chaos crée moteur et transmission seulement si la simulation mécanique est activée lors de la création physique. Réactiver les fournisseurs de forces **avant** de recréer la simulation d'un module détaché. Vérifier régime moteur, contacts et distance réellement parcourue, pas seulement le nombre d'os.
- Adapter freinage, frein à main et ressorts à la masse du véhicule. Le frein à main doit neutraliser les entrées accélérateur/marche arrière. Pour une escorte proche, calculer aussi un cap de marche arrière plutôt que braquer à fond en continu autour du point à rejoindre.
- Le même Hondo passe par les 97 poses évaluées de la source, avec une piste de placement du squelette. Quatre roues participent à Chaos en route, six après déploiement ; les six pneus visibles restent les mêmes objets. Composer le mouvement des roues après leur piste de déploiement.
- Une roue de secours projetable est un seul acteur persistant : attaché d'abord, détaché et simulé ensuite. Tester son identité avant/après et sa réplication ; ne pas faire disparaître un mesh pour créer un projectile de remplacement.
- UE 5.8 initialise le mode de réfraction des matériaux à `None`. Définir explicitement un mode avant de connecter/compiler le verre, puis enregistrer. Pour ces vitres minces, utiliser `RM_PIXEL_NORMAL_OFFSET` : un indice volumique sur une simple surface plane décale l'image hors écran et peut produire des aplats gris après cuisson. Opacité 0,22, teinte sombre et reflets sont conservés. L'assertion de propriété inactive dans `Material.cpp` n'est pas un avertissement à masquer.
- L'itération Python sur un `unreal.Array` de structures retourne des copies. Après modification d'un `SkeletalMaterial`, réaffecter `slots[index] = slot` puis le tableau au mesh. Forcer l'enregistrement du mesh, contrôler la valeur de retour, fermer les jeux qui verrouillent les assets et vérifier dans **un nouveau processus** que les matériaux/atlas sont effectivement présents. Un état correct en mémoire n'établit pas la persistance sur disque.
- Ne pas trier la sélection de véhicules sur `GetUniqueID()` : ces identifiants sont recyclés après destruction/GC. L'ordre de familles puis les noms d'acteurs donne une sélection stable pour l'autorité réseau.

Les essais à événements Xbox injectés valident le chemin d'entrée Unreal. Ils restent distincts d'une manipulation physique d'une manette et d'un jugement artistique humain.
