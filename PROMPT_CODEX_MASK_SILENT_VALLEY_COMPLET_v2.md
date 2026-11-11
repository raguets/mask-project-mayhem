# PROMPT COMPLET POUR CODEX — M.A.S.K. PROJECT MAYHEM / SILENT VALLEY

## INSTRUCTION PRINCIPALE — À EXÉCUTER

Tu es un développeur senior Unreal Engine 5.8 C++ / Blueprints, technical level artist et spécialiste d'automatisation de l'éditeur Unreal. Tu travailles **dans le dépôt local `mask-project-mayhem`**. L'ancien projet VehicularCombat est **déjà fonctionnel** sous UE 5.8 ; **trois véhicules ont déjà été intégrés et doivent être conservés et réutilisés**. **Ne migre pas de nouveau le jeu, ne remplace pas les véhicules et ne refonds pas son gameplay.**

**Objectif immédiat :** construire une **nouvelle carte réellement jouable** dans laquelle le joueur démarre dans la base secrète Boulder Hill, franchit sa sortie, arrive en extérieur dans une vallée rurale américaine (prairies, montagnes, pins, falaises, routes de campagne), puis rejoint Eagle Pass et Old Quarry à bord de l'un des trois véhicules existants. Procéder d'abord par blockout / parcours pilotable, puis habillage photoréaliste et seulement ensuite logique de mission et combat. La spécification détaillée ci-dessous fait partie intégrante de ce prompt.

La spécification est dans docs\Spécifications missions.

### État réel déjà confirmé par le propriétaire — NE PAS REDÉMARRER LA CONFIGURATION

- Unreal Engine 5.8 et le projet `mask-project-mayhem` fonctionnent déjà.
- Trois véhicules sont intégrés et fonctionnent dans le projet existant ; découvrir leurs noms, classes et niveaux sans les inventer.
- **Plugins déjà activés dans Unreal** : Procedural Content Generation Framework (PCG), Python Editor Script Plugin, Editor Scripting Utilities et Modeling Tools Editor Mode. **Vérifie leur présence/compatibilité, mais ne demande pas à l'utilisateur de les réinstaller ou de les activer de nouveau.**
- L'utilisateur **est déjà connecté à Fab à l'intérieur d'Unreal Engine et a importé avec succès un rocher Megascans**. Vérifie sa présence dans le Content Browser et réutilise-le si pertinent.
- **Quixel Bridge ne peut pas être utilisé** sur cette installation (échec d'authentification « Your account does not yet meet the age requirements of this site »). **Ne dépends pas de Bridge et n'essaie pas de le réparer**. Les assets Quixel/Megascans doivent provenir de **Fab**.
- Budget d'**achat de plugins et d'assets : 0 €**. Aucun achat, aucune activation de licence ou acceptation de conditions contractuelles au nom de l'utilisateur.
- Landscape et Landscape Splines sont des outils intégrés au moteur ; World Partition est un système de gestion de carte, à utiliser si adapté, pas une dépendance obligatoire à installer.

### Outils et méthode imposés

1. **Landscape** : relief macro de la vallée, crêtes, plaines et carrière ; Terrain/Landscape dans une **nouvelle carte**, sans écraser les maps existantes.
2. **Landscape Splines ou Spline Meshes** : route asphaltée à deux voies, chemins de terre, bordures. Choisir la technique qui donne une chaussée réellement praticable et des collisions fiables, documenter le choix.
3. **PCG** : distribution non destructive des arbres, broussailles, herbes et pierres, avec exclusion au voisinage des routes, points de spawn, garage et arènes. Commencer après validation de la conduite.
4. **Modeling Tools Editor Mode** : blockout et éléments géométriques simples ; **Python Editor Script Plugin** et **Editor Scripting Utilities** : automatisation via l'éditeur si l'API réellement disponible le permet. Utiliser C++ ou les outils d'édition Unreal lorsque Python ne couvre pas l'action voulue.
5. **World Partition** : évaluer pour la carte de 4 × 4 km ; utiliser sans imposer de migration irréversible des cartes préexistantes. Profiling et streaming à tester.
6. **Fab et Quixel Megascans via Fab** : priorité aux rochers, falaises, sols, matériaux, arbres et végétation photoréalistes **gratuits et compatibles avec la licence du projet**. Ne prétends jamais avoir téléchargé ou ajouté un asset si ce n'est pas effectivement fait. N'assume pas que tout Megascans soit gratuitement disponible dans le compte. Si une acquisition manuelle est requise, donne **le lien précis vers l'asset**, explique comment l'ajouter au projet et poursuis le blockout avec un placeholder sans bloquer.
7. **Lumen/Nanite** uniquement si adaptés au matériel et aux meshes, avec optimisation mesurée ; régler le budget de performance plutôt que tout activer aveuglément.
8. **Aucun MCP Unreal obligatoire** : commence avec Unreal Editor, UnrealEditor-Cmd, scripts éditeur, UBT/UAT et les interfaces disponibles. Un MCP n'est à envisager que s'il apporte un avantage concret, après explication et accord de l'utilisateur.

### Règles de sécurité et d'exécution

- Au départ, inspecte `git status`, le vrai fichier `.uproject`, les chemins UE 5.8 et les maps/Blueprints existants. Ne suppose ni noms de modules ni chemins absolus.
- Ne détruis ni les créations Blender, ni les véhicules, ni les maps, ni les assets actuels. Préserve les changements non commités ; propose une branche `feature/silent-valley-mission-01` et des points de contrôle Git sans écraser le travail présent.
- **Ne fabrique jamais de fichiers `.uasset` ou `.umap` textuels simulés** : utilise Unreal Editor, ses APIs et les outils de sauvegarde appropriés. Les scripts Python externes ne remplacent pas l'exécution de l'éditeur pour créer ces assets.
- Avant un changement risqué, sauvegarde le projet et détaille les impacts. Ne télécharge ni pack payant ni outil tiers sans accord. Ne transfère pas de secrets ou d'identifiants vers des services externes.
- Consigne pour chaque asset externe son nom, lien source, licence visible, statut gratuit et destination locale dans `docs/ASSET_MANIFEST.md`. Distingue ce qui est **déjà importé**, **disponible dans Fab**, **à acquérir manuellement**, ou **placeholder**.
- Pour les vérifications, renseigne `VÉRIFIÉ / NON TESTÉ / BLOQUÉ` ; une compilation réussie ne prouve pas qu'un itinéraire ou une mission sont jouables. Joins captures réelles de l'éditeur, logs, étapes de reproduction et limites identifiées. Ne présente pas des images de concept comme captures du jeu.

### Ordre de réalisation et livrables obligatoires

**G0 — Audit ciblé (rapide) :** confirmer versions, plugins actifs, Fab/Megascans déjà importé, trois véhicules, système de spawn et map de référence ; produire `docs/SILENT_VALLEY_IMPLEMENTATION_PLAN.md` avec chemin des fichiers et risques.

**G1 — Priorité absolue : carte pilote.** Créer `L_SilentValley_Blockout` dans `Content/MASK/Maps/SilentValley/` (ou chemin adapté au dépôt) : garage/sortie de Boulder Hill en géométrie simple, paysage vallée/contreforts, route continue Boulder Hill → Pinewood Road → Eagle Pass → Old Quarry → North Ridge, points de repère et aire de retournement. Vérifier qu'un véhicule existant peut sortir et rouler jusqu'à la carrière ; puis tester les trois.

**G2 — Collisions et pilotage :** tester largeurs selon gabarits réels, raccords chaussée/terrain, courbes, pentes, lignes de collision et limites de carte. Corriger les défauts avant toute décoration massive.

**G3 — Première passe environnement réaliste :** choisir un tronçon vitrine d'environ 500 mètres. Utiliser les assets gratuits déjà présents, puis proposer des ressources gratuites Fab/Megascans précises ; créer matériau de terrain, rochers/falaises, pins, herbe, PCG, lumière golden hour, signalisation. Tester lisibilité et performance. Étendre ensuite progressivement.

**G4 — Gameplay de mission :** implémenter briefing, sortie de base, checkpoints, reconnaissance, interception, combat dans Old Quarry, récupération et extraction en réutilisant le système VehicularCombat. Réutiliser l'IA et le HUD existants si possible ; alternatives explicites si absents. Respecter autorité serveur et réplication si le mode coop est disponible.

**G5 — Validation :** fournir rapport `docs/tests/SILENT_VALLEY_TEST_REPORT.md`, état de chaque jalon, captures **in-engine** des cinq lieux, commandes exécutées, logs, comparaison avant/après et comment jouer ; si possible test PIE 2 joueurs, clairement indiqué comme non testé sinon.

**Commence tout de suite par G0 puis G1. Continue dans la mesure où les outils locaux le permettent ; ne bloque pas sur Quixel Bridge, l'acquisition d'assets ou un MCP. Ne déclare jamais une fonctionnalité achevée sans test réel.**

---

## SPÉCIFICATION DÉTAILLÉE DE MISSION — RÉFÉRENCE INTÉGRÉE

Le texte suivant fournit les lieux, objectifs, contraintes de level design et critères d'acceptation ; en cas de divergence, les instructions mises à jour ci-dessus (état des plugins et accès Fab, priorité au parcours pilotable, budget 0 €) priment.

# M.A.S.K. PROJECT MAYHEM — MISSION 01 : OPÉRATION SILENT VALLEY

**Spécification de mission et de création d'environnement — v1.0 — 8 novembre 2026**  
**Destinataires :** Codex / Claude Code / développeur Unreal Engine 5.8 / level artist  
**État :** proposition de conception, non implémentée, à adapter au projet existant `mask-project-mayhem`.

## 0. Directive aux agents

Le projet **VehicularCombat a déjà été porté et fonctionne dans Unreal Engine 5.8** d'après le propriétaire du projet ; **trois véhicules y ont été intégrés**. Ne pas recommencer la migration, renommer les modules existants ou remplacer le contrôleur de véhicule sans audit des fichiers locaux. Faire une sauvegarde/branche Git avant les modifications ; préserver tous les assets, scènes et Blueprints existants. La création du niveau et la logique de mission doivent être **ajoutées** proprement à l'architecture réelle du dépôt.

**Ne jamais annoncer que le niveau, le build, le multijoueur ou les collisions fonctionnent sans test effectif.** Rapporter `VÉRIFIÉ`, `NON TESTÉ`, `BLOQUÉ`. Ne pas télécharger silencieusement des packs payants, copier des éléments protégés ou installer des plugins inconnus. Demander validation pour les changements destructifs et les nouveaux logiciels.

## 1. Vision et objectif de la vertical slice

Créer un premier environnement rural **cinématique, semi-ouvert, réellement pilotable** qui relie le quartier général Boulder Hill à une vallée montagneuse. Le joueur quitte une station-service apparemment ordinaire et découvre un paysage ouvert de prairies, forêts éparses, massifs rocheux et routes secondaires. La mission passe de la découverte à la poursuite puis à un affrontement contre une escouade V.E.N.O.M.

**Nom :** Opération Silent Valley  
**Format :** campagne narrative jouable solo, coopération 2–3 joueurs si l'architecture actuelle le permet ; ambition ultérieure 4–6.  
**Durée cible :** 12–18 minutes ; à mesurer.  
**Carte de prototype :** 4 km × 4 km, route principale 5–7 km, densité élevée seulement près des trajets et lieux d'action. Dimensions hypothétiques, à affiner après blockout.  
**Saison / météo :** fin d'été, après-midi vers golden hour, temps sec, légère brume atmosphérique ; météo dynamique différée.  
**Style :** montagnes et contreforts d'une région américaine fictive inspirée de l'ouest du Colorado ; réalisme UE5, identité légèrement rétro-1980s dans l'architecture et la signalétique.  
**Principe artistique :** grands paysages lisibles, routes agréables, reconnaissance immédiate de Boulder Hill, aucune cité à construire pour le MVP.

## 2. Périmètre et exclusions

### Inclus en V0
- Niveau séparé `L_SilentValley_Blockout` sans détruire la carte VehicularCombat existante.
- Terrain jouable avec relief d'essai ; quelques voies de circulation principales et bretelles.
- Tu as déjà modélisé Boulder Hill sous Blender : tu as juste à l'inclure dans le niveau
- Route continue, sans interruption, depuis la base jusqu'à la zone de combat et retour/extraction.
- 3 à 5 points d'intérêt construits à partir d'éléments temporaires.
- Checkpoints, HUD mission minimal, déclencheurs, objectifs et conditions de réussite/échec.
- Ennemi IA simple ou rencontre scriptée (selon IA existante) ; si indisponible, cibles fixes avec alternative explicite.
- Collision, barrières, terrain et vérification de l'absence de chute hors carte.

### Inclus en V1
- Paysages finalisés par couches : terrain, matériaux, PCG de végétation et rochers, route détaillée, signalisation, ambiance lumineuse et sonore.
- Boulder Hill inclus
- Convoi V.E.N.O.M., poursuite, interception, combat, récompense locale, réinitialisation et rejouabilité.
- Coop 2–3 joueurs si capacités réseau vérifiées ; sinon jalon réseau séparé.

### Exclus
- Vaste ville, monde ouvert continu national, six joueurs garantis, IA routière complexe, météo totale, photographie 1:1 de lieux réels, destruction complète du terrain, économie en ligne, ennemis volants obligatoires, cinématiques facialement animées AAA.

## 3. Carte — zones et connexions

| ID | Zone | Fonction | Géométrie et direction artistique | Gameplay |
|---|---|---|---|---|
| SV-01 | Boulder Hill / Roadside Station | Départ / retour | Station-service isolée, parking, roche, entrée secrète en contrebas, antenne, panneau routier | briefing, sortie du garage, checkpoint zéro |
| SV-02 | Pinewood Road | Prise en main | Route à 2 voies, prairies, clôtures, ranch lointain, bosquets, ligne électrique | conduite, instructions radio, prise en main |
| SV-03 | Eagle Pass | Suspense / reconnaissance | Épingles, parois rocheuses, pins, belvédère, petit tunnel ou passage rocheux | observation, embuscade facultative, choix d'itinéraire |
| SV-04 | Old Quarry | Arène de combat | Carrière abandonnée, pistes de terre, blocs, bâtiments industriels modestes, conteneurs | barrage, neutralisation ennemis, extraction de matériel |
| SV-05 | North Ridge | Extraction / perspective | Crête ouverte, aire de repos, route secondaire, vallée panoramique | extraction, évacuation et boucle de retour |

**Topologie :** boucle principale ou trajet principal avec route de retour non bloquante ; 1 raccourci facultatif en terre ; 2 points de retournement ; pas de cul-de-sac involontaire. Aucun point d'intérêt ne doit obliger les joueurs à traverser une zone inaccessible aux véhicules normaux. Prévoir un véhicule large (camion) dans les enveloppes de route, à partir des dimensions réelles des trois véhicules intégrés.

## 4. Bible visuelle / références

- Références environnementales : plaines d'altitude, vallées forestières, roche grise/ocre, bords de route poussiéreux, pins et peupliers épars, végétation de fin d'été ; ni désert total ni forêt tropicale.
- Boulder Hill : fidélité de silhouette à la base M.A.S.K. en fonction des références autorisées ; prototype de façade librement créé. Références de jouets et dessins animés à observer uniquement.
- Conduite : chaussées lisibles même à vitesse élevée ; éviter végétation opaque directement aux sorties de virages.
- Photo/rendu de contrôle obligatoire aux zones SV-01, SV-02, SV-03, SV-04, SV-05 en lumière de jour et au coucher du soleil.
- **Important :** des images générées de concept art ne sont pas des preuves de géométrie de niveau implémentée.

## 5. Déroulement détaillé de mission

**Mission ID :** `MSN_SilentValley_01`. États : `Unavailable`, `Briefing`, `Departure`, `Travel`, `Recon`, `Intercept`, `Combat`, `Recover`, `Extract`, `Success`, `Failed`.

### Phase 0 — Alerte / briefing (60–90 s ciblées)
- Lancement depuis carte mission ou premier spawn Boulder Hill.
- Audio radio/textes temporaires : « V.E.N.O.M. transporte un module de guidage expérimental dans Silent Valley ; intercepte le convoi avant qu'il ne franchisse North Ridge. »
- Choix du véhicule parmi les trois déjà intégrés ; ne pas présumer de leurs noms / capacités exactes.
- Coop : départ validé par l'hôte, clients possèdent leurs véhicules respectifs ; pas de blocage si le jeu n'a pas encore de lobby.
- **Achèvement :** un véhicule possédé passe la zone de départ.

### Phase 1 — Sortie de Boulder Hill (1–2 min)
- Porte de garage/hangar s'ouvre via déclencheur si asset disponible, sinon portail temporaire clairement marqué.
- Déplacement depuis cour/base vers route départementale ; caméra élargie au panorama ; objectif HUD « Rejoins Pinewood Road ».
- Moment mémorable : sortie de la station-service discrète vers la grande vallée et les montagnes.
- **Achèvement :** chaque joueur actif rejoint la voie principale ou le système gère les retardataires sans téléportation brusque.

### Phase 2 — Traversée / découverte (2–3 min)
- Parcours balisé mais conduite libre ; 2 grandes courbes, 1 ligne droite rapide, 1 virage technique.
- Conversation radio optionnelle et premier repère topographique ; checkpoint `CP_Pinewood`.
- Pas d'ennemi obligatoire avant le premier belvédère.
- **Achèvement :** au moins un membre de l'escouade atteint le volume Eagle Pass ; le reste peut rejoindre sans casser la mission.

### Phase 3 — Reconnaissance au col (1–2 min)
- À Eagle Pass, zone d'observation du convoi visible à distance. Indicateur visuel et radio ; approche directe ou par petit chemin de terre.
- Dans le prototype, le convoi peut être simulé par 1 véhicule ennemi mobile et 1 véhicule cible non combattant ; à défaut, cibles avec déplacement spline et règles explicites.
- **Achèvement :** déclenchement du scan/recon ou entrée dans un volume de proximité ; l'événement ne peut se déclencher qu'une fois côté serveur.

### Phase 4 — Interception / poursuite (2–4 min)
- V.E.N.O.M. accélère sur une route vers Old Quarry ; les joueurs le suivent.
- Spawn dynamique **hors du champ immédiat** et suffisamment éloigné pour éviter pop-in ; le serveur autorise les positions et déclenchements.
- Objectif « Stoppe l'escorte avant la carrière ». Si le convoi atteint la carrière, la mission continue en combat avec difficulté accrue plutôt qu'échec brutal.
- **Achèvement :** l'escorte est neutralisée OU le convoi est entré dans Old Quarry.

### Phase 5 — Combat dans la carrière (2–4 min)
- Zone claire et suffisamment large pour 3 véhicules ; relief et blocs servant de couvert mais sans pièges de collision.
- 1–3 ennemis selon capacité de l'IA et nombre de joueurs ; phase initiale à 1 ennemi.
- Endommagement/destruction avec système VehicularCombat réutilisé ; si les PV ne sont pas présents, objectif de contact/zone comme fallback, documenté.
- Objectif « Sécurise le module » après neutralisation des menaces.
- **Achèvement :** toutes les menaces requises sont neutralisées et interaction de récupération terminée.

### Phase 6 — Récupération et extraction (1–3 min)
- Objet récupérable/acteur proxy en carrière ; interaction côté serveur, une seule attribution.
- Suivre une route secondaire vers `CP_NorthRidge`; extraction par déclencheur.
- Le retour complet à Boulder Hill peut être optionnel en V0 (bouton retour au QG) mais doit devenir pilotable en V1.
- **Achèvement :** tous les joueurs concernés ou le chef d'équipe franchissent extraction selon règle de groupe configurée ; UI succès.

### Phase 7 — Débrief / récompense (30–60 s)
- Affichage : mission achevée, dégâts subis, ennemis neutralisés, temps, récompense garantie `TechComponents` (valeur placeholder), bonus non aléatoire si convoi capturé intact.
- Enregistrer la progression en local avec identifiant de mission ; éviter toute double attribution au cours d'une même session. Persistance en ligne plus tard.

### Échecs et récupération
- Si tous les joueurs sont immobilisés : `Failed`, proposer recommencer depuis checkpoint valide (v0 : recommencer mission).
- Sortie de carte : limites physiques progressives, retour sécurisé ou reset, jamais sortie de niveau catastrophique.
- Déconnexion en coop : le serveur revalide les participants ; si gameplay impossible, propose retry/retour plutôt qu'un état bloqué.
- Convoi bloqué/renversé : timeout de récupération et retour sur spline/cible d'étape validée, tracé dans logs.

## 6. Système mission data-driven

Ne pas inventer une nouvelle architecture si le projet contient déjà un gestionnaire d'objectifs. Auditer, puis intégrer l'équivalent de :

- `AMASKMissionDirector` (autorité serveur, progression d'état, points de contrôle, événements idempotents).
- `UMASKMissionDefinition` (PrimaryDataAsset si pertinent : étapes, textes, spawn sets, checkpoints, règles de récompense).
- `AMASKMissionTrigger` (volume côté serveur, filtrage véhicules et joueurs, anti-double-trigger).
- `AMASKEnemySpawner` (spawn par distance, contrôles d'obstruction et limites d'IA).
- `UMASKMissionHUD` ou widgets compatibles système UI existant.
- `AMASKExtractionZone` (récompense et fin).

Ces noms sont **proposés**, pas garantis présents dans le dépôt. Ne pas renommer l'existant inutilement. Prévoir point d'entrée extensible pour la deuxième mission.

## 7. Production technique de l'environnement UE 5.8

### 7.1 Carte et relief
- Créer une nouvelle carte prototype ; envisager un niveau `Open World` et **World Partition** si la carte finale le justifie, sans migration irréversible de la carte actuelle.
- Terrain `Landscape`, relief macro d'abord : plaine, collines, crêtes, vallée, carrière, cours d'eau décoratif. Pentes de route adaptées à la conduite (à mesurer sur les véhicules réels).
- Utiliser des heightmaps sous licence contrôlée si nécessaire ; pour le prototype, sculpt natif suffisant.

### 7.2 Routes et collision
- Utiliser `Landscape Splines` ou spline meshes explicitement validés pour sculpter les routes et y placer la chaussée, l'accotement et les barrières.
- Largeur de base indicative : 7–9 m pour route à 2 voies, plus large dans les zones d'action ; ajuster aux gabarits réels de véhicule.
- Vérifier coutures du terrain, dévers, virages, garde-fous, intersections et accroches de roues. Routes finies en matière asphalte rugueux avec usure légère et marquages discrets.
- Surfaces `Asphalt`, `Gravel`, `Dirt`, `Grass` connectées à la physique/effets si possible.

### 7.3 PCG et dressing
- Graphes PCG non destructifs pour arbres, broussailles, herbe, pierres, clôtures, pylônes, débris ; exclusion près routes/spawns/arènes.
- Densité élevée uniquement le long de la route et des points de vue ; générer en couches pour garder maîtrise des performances.
- Instanced Static Mesh / HISM et règles LOD/Nanite selon assets ; éviter collisions sur toute l'herbe.

### 7.4 Lumière et atmosphère
- Lumière directionnelle, Skylight, Sky Atmosphere, nuages, Exponential Height Fog, réglage d'exposition/couleur.
- Rendu Lumen si budget GPU le permet ; profil de qualité ajustable. Brouillard subtil, pas d'impact excessif sur la lisibilité.

### 7.5 Ressources
- Prioriser assets natifs Unreal/projet existant, meshes originaux Blender et contenus Fab/Megascans disposant de droits d'usage appropriés. **Consigner toute provenance et toute licence**, ne pas copier des packs depuis d'autres jeux.
- L'agent doit signaler les éléments bloqués par une installation/connexion externe et utiliser des placeholders lisibles.

## 8. Réseau et AI — limites explicites

- La logique de mission, l'apparition des ennemis, les PV et les récompenses sont **autoritaires serveur**.
- Les effets sonores/visuels, animations de portails et HUD peuvent réagir à l'état répliqué ; le client ne décide pas des succès.
- Pour tester 2–3 joueurs, utiliser 2 instances/PIE multi-client et vérifier les déclencheurs et état synchronisés.
- L'IA automobile représente un risque technique fort : privilégier `follow spline` + avoidance simple en première passe ; intégrer conduite autonome avancée après preuve de fonctionnement. Ne pas promettre une poursuite IA réaliste en V0.

## 9. Tâches, ordre et gates

| Gate | Livraison | Condition de passage |
|---|---|---|
| G0 | Audit du dépôt réel et des trois véhicules | Classes, cartes, assets, noms et entrées de mission documentés ; aucune régression |
| G1 | Carte `L_SilentValley_Blockout` et sortie Boulder Hill | Spawn et conduite continue depuis QG jusqu'à arène puis extraction |
| G2 | Routes et relief utilisables | Trois véhicules testés : pente, largeur, virages, collisions et no-fall |
| G3 | Mission objective graph | Étapes départ→route→recon→poursuite→combat→extraction→résultat sans blocage |
| G4 | Ennemi et combat | Au moins un adversaire actif/cible validée ; logs d'événements |
| G5 | Passe visuelle | 5 lieux distincts reconnaissables, végétation PCG contrôlée, atmosphère cohérente |
| G6 | Test 2 joueurs | Objectifs synchronisés, spawn, progression, dégâts et récompenses vérifiés |
| G7 | Build jouable | Packaging Windows ou procédure locale reproductible, screenshots et rapport de performance |

Ne pas lancer G5 sur la totalité de la carte tant que G1/G2 ne sont pas convaincants ; une zone finie haute qualité de 500 m est préférable à 16 km² d'assets mal répartis.

## 10. Critères d'acceptation et tests

### Tests minimaux
1. Une session commence à Boulder Hill avec un véhicule sélectionné parmi les trois existants.
2. Le garage/la base donne accès à l'extérieur sans bug de collision ni changement de véhicule involontaire.
3. Le trajet jusqu'à Eagle Pass peut être terminé sans perdre le contact physique du véhicule avec la route, sans fossé infranchissable ni tremplin involontaire.
4. La carrière peut accueillir trois véhicules joueurs et au moins un adversaire ; trajectoires et collisions valides.
5. Chaque étape HUD est déclenchée exactement une fois ; aucun état mission bloqué.
6. La mission est rejouable et revient dans un état initial propre.
7. En mode 2 joueurs, les deux clients voient la même phase de mission et la même progression d'ennemis.
8. Le projet préexistant compile/s'ouvre comme avant ; aucune régression des trois véhicules intégrés.
9. Les erreurs UE/Blueprint/PCG sont consignées et traitées ; pas de déclarations de réussite sur simple capture d'écran.
10. Profiler FPS, frame time, mémoire, nombre d'acteurs instanciés ; capturer machine, résolution et paramètres graphiques.

### Conditions de performance provisoires
- Viser 60 images/s sur une machine de test connue ; relever configuration, taille paysage, densité, distance de vue et effets. Ne pas inventer des performances théoriques.
- Prioriser collisions routes et gameplay ; adapter PCG, feuillage, ombres et Lumen d'après mesures.

## 11. Organisation des fichiers proposée (adapter à l'existant)

```
Content/MASK/
  Maps/SilentValley/
    L_SilentValley_Blockout.umap
    L_SilentValley_Gameplay.umap
  Environment/SilentValley/
    Landscape/
    Materials/
    Roads/
    Rocks/
    Vegetation/
    Structures/
    PCG/
    Lighting/
  Missions/SilentValley/
    Data/
    Triggers/
    UI/
  Audio/Ambience/
Docs/ (ou docs/)
  levels/SILENT_VALLEY_MAP.md
  missions/MSN_SILENT_VALLEY_01.md
  tests/SILENT_VALLEY_TEST_REPORT.md
```

## 12. Instructions spécifiques à Codex — lancement immédiat

1. Ouvre le dépôt `mask-project-mayhem` déjà fonctionnel sous UE5.8 ; identifie son `.uproject` et ses cartes sans supposer les noms.
2. Crée une branche `feature/silent-valley-mission-01` si Git le permet et si le working tree est protégé.
3. Audit en priorité : mécanismes de spawn des trois véhicules, niveau existant, code d'armes et dégâts, réseau/PIE, Blueprints et assets de terrain disponibles.
4. Produis le blockout de **Boulder Hill extérieur → Pinewood Road → Eagle Pass → Old Quarry → North Ridge** dans une **nouvelle carte**, pas dans celle du jeu initial.
5. Dans le premier lot, crée le `Landscape`, les splines routières, des volumes de spawn et de checkpoint et une extraction temporaire ; implémente une conduite de bout en bout.
6. Génère des captures in-engine des cinq zones et documente les commandes/tests réellement exécutés.
7. Ensuite seulement, active les graphes PCG, puis implémente objectifs, adversaires et coop selon les gates.
8. Si l'automatisation sans interface ne peut pas créer des `.umap/.uasset` fiables, utilise l'éditeur, Python Editor Scripting ou un outil adapté **après validation**. N'écris pas de faux fichiers `.uasset` ni de contenu de niveau en texte arbitraire.
9. N'installe pas de MCP Unreal par défaut. Utilise d'abord éditeur, outils Unreal officiels et scripts Python ; propose MCP seulement si la création/inspection d'assets reste une limite importante.

## 13. Prompt court à copier dans Codex

> Lis `MASK_Mission_01_Silent_Valley_Spec_v1.md`. Le dépôt `mask-project-mayhem` fonctionne déjà sous Unreal Engine 5.8 et contient trois véhicules intégrés. Ne refais pas sa migration. Commence par inspecter le code et les cartes réelles, puis crée **sans casser l'existant** un nouveau niveau rural `L_SilentValley_Blockout` avec une sortie visible de Boulder Hill, une route de campagne sinueuse, une vallée, un col, une carrière et une zone d'extraction. Vérifie le spawn et la conduite des véhicules existants entre ces points, puis ajoute des checkpoints. Évite tout dressing lourd avant validation de la conduite et des collisions. Utilise les mécanismes Unreal réels pour produire les fichiers `.umap/.uasset`, teste ce qui est testable et publie des captures et logs. Ensuite, implémente les phases de `MSN_SilentValley_01` et la passe PCG selon les gates du document. N'affirme aucune validation non effectuée et signale tout blocage sur assets ou outils.

## 14. Documentation Epic utile

- PCG framework : https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-framework-in-unreal-engine
- Landscape Splines : https://dev.epicgames.com/documentation/unreal-engine/landscape-splines-in-unreal-engine
- World Partition : https://dev.epicgames.com/documentation/unreal-engine/world-partition-in-unreal-engine
- PCG generation modes : https://dev.epicgames.com/documentation/en-us/unreal-engine/using-pcg-generation-modes-in-unreal-engine
