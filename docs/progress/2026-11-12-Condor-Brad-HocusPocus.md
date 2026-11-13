# Condor, Brad Turner et Hocus Pocus — passe éditable V15

Fiche transformation lue avant les onze images utilisateur, toutes inspectées. Jouet ancien prioritaire pour Condor, réédition, cartoons et fiche illustrée distingués. Interprétation réaliste de Brad expressément autorisée ; anatomie CC0 générique copiée indépendamment depuis Calhoun V2, sans modification des anciens assets. Échelle et mécanismes cachés estimés.

Les corrections successives sont mémorisées dans AGENTS.md et implémentées dans les scripts `art_source/Condor/scripts`. Bloc arrière unique, plus court et progressivement étroit ; dessous diagonal vers siège. Pales rangées le long des montants convergents ; vrai moyeu tournant et porte-pales. Roue arrière persistante et fourche ancrée au châssis. Selle/patins dans une même descente0,12m. Avant/pavillon affinés, pare-brise à trois facettes jusqu'au vert, nez court suivant sa pente, face de l'ouverture carrée inclinée vers le haut, canon escamotable, sans phares.

Hocus Pocus : un maillage connecté ; face entièrement couverte, visière de plongée opaque uniquement frontale, transition avant/côtés plus carrée, grille vocale en relief. Bas sans pincement, collerette projetée sur les épaules et pondérée au vêtement avec transition tête. Cette souplesse est interprétée. Même Brad/tête/rig pour debout/conduite avec ou sans masque.

## Sources et preuves

- Assemblage `art_source/Condor/Condor_V15_Assembly.blend`, versions V1–V14 conservées.
- Autonomes réellement réouverts : `art_source/Condor/Condor_V15_Vehicle.blend`, `art_source/Brad_Turner/BradTurner_V1.blend`, `art_source/Brad_Turner/HocusPocus_V1.blend`.
- `standalone_validation_v15.json` : trois sources passent, aucune dépendance manquante, un rig pour Brad et mêmes maillages aux quatre états.
- `renders/v15_review` : neuf PNG1100×900 Cycles24samples, COMPLETE, tous ouverts et inspectés, y compris arrière et gros plan du masque.
- `validation_v15.json` :21 phases pales contre surfaces sélectionnées pilote/carénages ; zéro intersection de triangles, garde verticale de0,0693m au-dessus du pilote rotor déployé, deux pneus et aucun driver invalide.
- `mechanisms_v11.json` a été régénéré sur V14 (nom historique, appel `mechanisms_call_v14.json`) :41 positions de fourche, erreur d'ancrage maximale0,000000377m, descente selle0,12m, siège/patins même parent, masque un objet/un composant connecté. V15 ne change que matériaux de grille et fermeture des extrémités des courbes structurelles.

## Limites

Première passe artistique ; plis, peau, coiffure, lunettes, doigts et détails de grille restent stylisés. Les tests couvrent des surfaces explicitement sélectionnées, pas toutes les intersections/volumes ni la souplesse du vêtement. Contact de la collerette et pilote inspecté dans les rendus, sans certification globale de collision. Pas de retopologie/UV finale ni d'intégration Unreal.

Route/hélicoptère mémorisé : stationnaire au freinage maximal et nez baissé en avance, contrairement à route/avion. `forward_flight` donne une inclinaison d'environ6° ; `hover_height` est un contrôle de présentation. Aucun comportement physique de jeu n'est validé par ces contrôles Blender.

## Intégration Pinewoods et corrections dynamiques — 12 novembre 2026

Source courante V20, Brad et masque V2 ; versions antérieures conservées. Imports Unreal Condor/Brad/finalisation passés (Saved/Art/condor-import.json, condor-locomotion-import.json, condor-finalize.json). 12 groupes visuels, 2 roues, 97 échantillons, 18 clips Brad. Un même personnage pour conduite/transformation/marche, masque séparé. LOD statique réduit de source conservé en commandlet ; pas de génération de LOD statique supplémentaire prétendue.

Premier test complet corrigé `smoke-condor-r3/summary.json` :25 contrôles passent, sortie moteur0. Transformation demandée à11,9m/s, acceptée en roulant. Stationnaire résiduel0,0034m/s ; 16,66m/s après5s d’avance ; inclinaison accélération22° ; retour au sol et rétraction6,34s. Ce scénario ne couvre pas toutes les vitesses, pentes et collisions.

Corrections : équilibre de roulis amorti36/12 par couples ; direction progressive adoucie ; dégagement rotor moto indépendant du roulis pour ne pas intersecter la chaussée ; commande vitesse10m/s² et inclinaison22° en vol ; freinage retour10m/s², inclinaison temporaire30° ; descente6m/s Condor et8m/s avions, arrondi final. Données réellement enregistrées via Tune-AirLandings.ps1.

Nouveau test rendu EN COURS : condor-render-r1 ; ajoute virages alternés, pic de roulis et garde conservatrice des coins de boîte du support au-dessus du terrain. Géométrie statique importée : support à33,7cm, pneu à0,109cm ; cette mesure seule ne valide pas la garde dynamique. Blender MCP indisponible au dernier essai ; utilisateur informé et reconnexion demandée. Source V20 non modifiée pendant ce lot.

### Contrôle de virages — résultat intermédiaire

`condor-render-r1` a échoué : pic roulis86,88°, support boîte−32,63cm, sortie sur pente forte, retour19,61s. Ce test plus exigeant a révélé un signe de couple erroné dans le NOUVEAU correcteur de roulis : FRotator.Roll positif correspond à une rotation physique locale X négative. Correction du signe en cours de compilation ; ne pas présenter r3 droit comme validation des virages. Images route/hover/forward r1 inspectées ; contrôle source Blender toujours indisponible.

### Équilibre et support après correction du signe

Rendu `condor-render-r2` : virages alternés passent, pic roulis11,25° et garde conservatrice support7,90cm (contre86,88°/−32,63cm avant correction). Captures route/hover inspectées. Le cycle échoue encore à l’atterrissage : arrêté à8,46cm au-dessus du terrain, châssis droit, critère d’alignement au terrain non rempli. Correction spécifique rotor : autoriser un châssis droit sur terrain de normaleZ>0,65 au lieu d’exiger que la moto s’incline parallèlement au flanc. Avions gardent le critère d’alignement original. Fixture suivante déplacée de800m montagne à200m approche vallée pour comparer un cycle routier ; déplacement initial uniquement, aucun repositionnement en vol.
