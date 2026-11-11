# Commandes Xbox

Thunderhawk est choisi par défaut. Matt porte Spectrum par défaut ; le même personnage et le même squelette servent aux poses assis/debout.

| Commande | Route | Vol |
|---|---|---|
| RT | Accélérer | Augmenter la vitesse cible |
| LT | Freiner / marche arrière | Réduire la vitesse cible, jusqu'au minimum de l'avion |
| Stick gauche horizontal | Diriger | Virer en inclinant l'appareil |
| Stick gauche vertical | — | Cabrer / piquer (avion) ; monter / descendre (hélicoptère) |
| Stick droit | Caméra libre | Caméra libre |
| RB | Tirer, maintenir pour l'arme automatique | Tirer |
| LB | Frein à main | — |
| X | Transformer en mouvement, avec de la place | Descendre automatiquement, puis replier au sol |
| Y | Changer d'arme | Changer d'arme |
| A | Sortir du véhicule arrêté, au sol, avec un côté libre | Sortie refusée : atterrir d'abord |
| B | Frein à main | Piquer / commande de descente |
| Clic L3 | Recentrer la caméra | Recentrer la caméra |
| Clic R3 | Cockpit / vue extérieure | Cockpit / vue extérieure |
| Croix gauche / droite | Armes 1 / 2 | Armes 1 / 2 |
| Croix haut / bas | Véhicule IA suivant / précédent ; l'IA reprend celui quitté | Idem |
| View, maintenir | Tableau des scores | Idem |
| Menu | Pause et menu | Idem |

Dans la pause : A ou B reprend ; Y retourne au menu principal. En multijoueur, l'écran de pause est local : la partie continue pour les autres joueurs.

## À pied

| Commande | Action |
|---|---|
| Stick gauche | Marcher dans les directions de la caméra |
| Maintenir L3 + stick gauche | Courir |
| Stick droit | Regarder et viser |
| A | Sauter |
| Y | Mettre / enlever le masque, visage conservé |
| RT ou RB, maintenir | Tirer avec le fusil ; rechargement automatique |
| X | Remonter dans son véhicule, à proximité et au sol |
| Menu | Pause et commandes |
| View, maintenir | Scores |

Le même conducteur quitte son siège et y retourne. Le véhicule reste garé, réservé à ce conducteur ; la croix haut/bas reprend son rôle de changement de véhicule après être remonté. Rhino ne peut pas rappeler son module pendant qu'Alex ou Bruce est à pied. Les masques n'ont pas encore de pouvoirs de combat.

Clavier à pied : W/S pour avancer/reculer, A/D pour les côtés, Maj pour courir, Espace pour sauter, E pour remonter, M pour le masque, clic gauche pour tirer. La manette suffit pour toutes les actions ci-dessus.

Dans le menu principal : stick/croix pour naviguer, A pour valider, X pour choisir Thunderhawk, Rhino, Hurricane ou le véhicule d'origine, Menu pour lancer directement le solo contre trois bots, B pour revenir. Les commandes détaillées sont accessibles avec Menu pendant la partie.

Rhino et Hurricane restent au sol dans leurs deux modes ; A ne les fait pas voler ou sauter. Rhino conserve Alex/Jackrabbit dans le camion et Bruce/Lifter dans son module arrière. X éjecte rapidement le même module vers l'arrière en conservant l'élan du camion. Le module devient sélectionnable ; l'autre partie reste conduite par un allié IA. Pour les réunir, X sur Rhino rappelle et attache immédiatement le module, même à distance et en mouvement. X depuis le module rend automatiquement le contrôle du camion puis rappelle le module. Un camion occupé par un autre humain ne lui est pas retiré.

Hurricane conserve Hondo/Blaster : il se lève pour le double canon pendant la transformation. En mode combat, **LB maintenu + Y** éjecte la même roue de secours vers l'arrière, une fois par véhicule. Y seul change toujours d'arme. Les transformations prennent la moitié du temps des pistes artistiques : 2 s pour Thunderhawk, 2,5 s pour Rhino et Hurricane.

## Validation

Le contrôle XInput du 7 novembre 2026 ne détecte aucune manette connectée (quatre emplacements : code 1167). Les essais à événements de manette injectés dans Unreal sont suivis dans `THUNDERHAWK_IMPLEMENTATION.md`. Ils ne constituent pas un essai physique des boutons ou des vibrations.

Le bouton Xbox central reste géré par Windows. Thunderhawk utilise le profil avion : **LT réduit progressivement la cible jusqu'à 50 km/h ; RT l'augmente progressivement jusqu'à 300 km/h**. Relâcher RT conserve la vitesse de croisière ; LT ne permet pas de stationner en avion. Roulis et tangage restent physiques. X lance l'atterrissage sans devoir descendre manuellement ; RT peut rester maintenu. Le profil hélicoptère accepte une vitesse cible nulle et le vol stationnaire. Aucun nouvel asset d'hélicoptère n'est ajouté : le profil est testé avec un véhicule de substitution. Voir [AIRCRAFT_SPEED_RANGE.md](AIRCRAFT_SPEED_RANGE.md).
