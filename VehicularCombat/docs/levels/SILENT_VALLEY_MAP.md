# Silent Valley — carte pilote en cours

Carte : `/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout`. Ouvrir avec Unreal Engine 5.8.2 installé. Lancement local avec `Jouer-SilentValley-Editor.cmd`, ou passer `Rhino` / `Hurricane` en argument. Le lanceur du jeu existant reste intact. Cette carte n'est pas encore une mission complète ni une distribution Windows validée.

Le joueur apparaît à l'intérieur de Boulder Hill V6, importé en pose de défense ouverte statique. Le parcours quitte le garage, traverse Pinewood Road, franchit Eagle Pass, atteint Old Quarry, puis North Ridge. La route continue ensuite vers l'extérieur de la base. La boucle complète de 9,55 km a été parcourue par les trois véhicules réels, en conduite automatisée prudente (return-r3). Pente maximale 8,47 %. Les mesures et limites figurent au rapport de tests.

Landscape natif 2017 × 2017 sommets, pas de 2 m, 256 composants ; carte classique, pas de conversion des maps préexistantes à World Partition. Streaming NON TESTÉ. Route de 10 m par spline meshes subdivisés avec collision complexe statique. Le terrain est raccordé au profil longitudinal ; ses surfaces, accotements et coutures restent en validation G2. Les noms des cinq lieux sont des repères de blockout, pas la preuve d'un environnement final.

La route possède désormais un matériau double face, des marquages jaunes discontinus au centre et des rives blanches. Le défaut de visibilité provenait principalement du culling des faces ; le diagnostic n'a pas démontré un problème de LOD Landscape. Les dalles carrière/ridge ont été abaissées de 3 cm pour éviter des faces coplanaires. Dix captures réelles, jour/golden hour, sont disponibles dans [les preuves visuelles](../validation/silent-valley/views-roadpaint-r2/day-zone-0.png). La passe golden hour reste sombre et le terrain ne possède pas encore son habillage réaliste.

Coordonnées initiales en cm : Boulder Hill (-135000,-110000,8000), Pinewood (-75000,-78000,9000), Eagle Pass (70000,25000,15500), carrière (65000,95000,10000), North Ridge (-55000,125000,16000). Unités et positions de conception estimées. Matériaux temporaires, pas de pins/PCG photoréalistes à ce stade.

Première couche G3 : 39 instances du rocher déjà importé, réparties par un véritable graphe PCG sur les 500–1000 m du trajet, autour de Pinewood. Route entière, spawns et checkpoints exclus lors du calcul des points. Le graphe est éditable ; ses exclusions sont précalculées et doivent être reconstruites avec le script après un changement de tracé. Les rochers sont décoratifs sans collision. Le matériau de sol v2 est une base procédurale originale, sans déplacement du terrain. Il manque encore arbres, herbe, falaises détaillées et signalisation lisible.

Les limites de prototype sont des colliders statiques invisibles à 2011 m du centre et à 1995 m d'altitude. Treize rayons de collision après réouverture vérifient leur présence ; le comportement d'un avion les heurtant reste NON TESTÉ. Ces limites ne sont pas un décor final.

## Essai local avec une manette Xbox

1. Double-cliquer `Jouer-SilentValley-Editor.cmd` pour Thunderhawk, `Jouer-SilentValley-Rhino.cmd` ou `Jouer-SilentValley-Hurricane.cmd`.
2. Le véhicule apparaît dans le garage ouvert. Suivre la sortie puis la chaussée vers Pinewood, Eagle Pass, Old Quarry et North Ridge ; la route revient ensuite près de la base.
3. RT accélère, LT freine, stick gauche dirige, stick droit contrôle la caméra. Menu affiche les commandes existantes ; X transforme le véhicule. Les essais automatiques du parcours ont été effectués en mode routier.

Cette version sert à explorer le niveau. La mission scénarisée et ses adversaires ne sont pas encore implémentés. Les deux petits lanceurs dédiés utilisent les mêmes options de véhicule que les essais physiques, sans compilation ni installation supplémentaires.

La création est reproductible par `Tools/Art/build_silent_valley.py` **dans Unreal Editor** ; avant reprise, le script copie la map générée sous `Saved/SilentValley/backups`. Les sources Boulder Hill V6 originales et les trois véhicules restent inchangés. Voir [checklist](../SILENT_VALLEY_CHECKLIST.md) et [tests](../tests/SILENT_VALLEY_TEST_REPORT.md) pour l'état réel des passages.
