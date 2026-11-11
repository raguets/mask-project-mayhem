# Avions : vitesse progressive de 50 à 300 km/h

8 novembre 2026, clarification utilisateur. Branche `fix/aircraft-speed-range`, depuis `872a295`.

- **LT** réduit progressivement la vitesse cible jusqu'à **50 km/h** (13,8889 m/s).
- **RT** augmente progressivement la vitesse cible jusqu'à **300 km/h** (83,3333 m/s).
- Relâcher les gâchettes conserve la cible. L'avion continue d'avancer.
- Le taux de variation de consigne reste à **8 m/s²**. La vitesse réelle évolue avec les forces bornées, la masse et la traînée ; aucune affectation instantanée de vitesse n'est ajoutée.

Le profil avion partagé reçoit ces valeurs par défaut. La puissance disponible passe de 280 à 600 kW pour permettre d'atteindre réellement la nouvelle vitesse malgré la traînée ; la poussée maximale reste à 10 kN. Le profil hélicoptère conserve son propre plafond de 30 m/s (108 km/h) dans `RotorcraftMaximumAirspeedMPS`, avec une vitesse minimale nulle. La conduite routière et la correction des roues arrière d'Hurricane restent inchangées.

Une première mesure Windows r1 donnait environ 296 km/h pour une consigne de 300 : les vérifications à tolérance large passaient, mais cette version n'est pas retenue comme livraison finale. La poussée compense maintenant aussi l'amortissement visqueux du corps Chaos. Les vérifications de simulation exigent une vitesse réelle à ±1 km/h de 300 et ±0,5 km/h de 50, en solo et sur le serveur, toujours sans imposer directement la vitesse du corps.

La sonde relève séparément le corps physique serveur aux trois points du cycle et la présentation côté client. Pour cette dernière, les tolérances sont ±6 et ±2,5 km/h ; les consignes répliquées doivent rester exactement à 300 et 50. Le réseau r2 avait échoué aux deux contrôles trop stricts appliqués aux relevés client ; cet échec est conservé dans [network-r2-failed.json](validation/airspeed/network-r2-failed.json). Les contrôles stricts du serveur ajoutés en r3 ne sont pas remplacés par ces tolérances de présentation.

L'aide de pause affiche les deux limites calculées depuis la définition du véhicule. Aucun asset `.blend`, `.uasset` ou `.umap` modifié.

La sonde de dynamique vérifie la vitesse réelle à 50, puis à 300 km/h, les phases intermédiaires d'accélération/freinage et le retour à 50 après freinage depuis 300. La plateforme temporaire de test est agrandie à 20 × 20 km pour cette séquence plus longue ; aucune carte de jeu persistante n'est modifiée. Les autres contrôles de transformation, atterrissage, Rhino et profil hélicoptère restent exécutés. Événements Xbox injectés, pas de test physique d'une manette.

Distribution finale : **`MASK-Airspeed-Development-r3`**, UE 5.8.2 Win64 Development. `Jouer-MASK.cmd` pointe vers cette version. Les 50 fichiers de l'archive ont été vérifiés par SHA-256 avec le staging après résolution d'un manque d'espace disque par compression NTFS des fichiers générés. Aucun fichier supprimé. [Empreinte de l'exécutable](validation/airspeed/package.json), [vérification de l'archive](validation/airspeed/archive-verification.json).

Tests sur cet exécutable : **[35/35 solo](validation/airspeed/packaged-solo.json)** et **[10 hôte + 28 client](validation/airspeed/packaged-network.json)** ; trois processus terminés avec le code 0. Les vitesses physiques aux trois bornes passent les tolérances strictes sur le serveur et en solo. Les phases intermédiaires d'accélération/freinage, les transformations, le rappel Rhino et le stationnaire du profil hélicoptère passent également. [Mesures numériques](validation/airspeed/measurements.json). Les instances de test sont fermées.

Reproduction : `Test-Dynamics.ps1 -RunName new-solo -Render -GameExecutable <EXE_R3>`, puis `Test-Dynamics.ps1 -RunName new-network -Network -Render -GameExecutable <EXE_R3>`. Choisir des noms de passe nouveaux pour préserver les rapports.
