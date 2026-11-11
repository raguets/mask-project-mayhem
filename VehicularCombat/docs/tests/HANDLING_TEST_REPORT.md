# Maniabilité et déplacement à pied — 9 novembre 2026

Les essais concernent les réglages natifs communs aux véhicules M.A.S.K. et le CharacterMovement des conducteurs. Aucun mesh, masque, véhicule, animation source ou niveau n'est remplacé. Branche : `feature/silent-valley-mission-01`, base `7ae7057` ; modifications non committées.

## Changements

- Direction : butée physique 45°, réponse plus rapide, pleine amplitude à basse vitesse puis réduction progressive. La configuration des roues reste propre à chaque simulation ; aucun CDO partagé n'est modifié.
- Motricité : premiers rapports et marche arrière plus courts, plage de couple bas régime élargie. La limite de puissance tient compte du multiplicateur de courbe appliqué ensuite par Chaos.
- Vol assisté : taux de rotation cible 55°/s à basse vitesse, 30°/s au maximum, avec force centripète correspondante. Toujours par forces/couples sur le corps existant ; aucun changement instantané de vitesse ou de rotation.
- Marche : 240 cm/s au lieu de 150 ; course conservée à 400 cm/s. Ancienne zone d'entrée conservée et accès supplémentaires près des points de sortie des portes.
- Atterrissage du conducteur : réacquisition par `FindFloor` et `ProcessLanded` uniquement en descente lente, sans propulsion de saut, sur un sol praticable dans `MAX_FLOOR_DIST`. Aucun repositionnement de capsule.

## Défaut à pied reproduit

[Avant correction à Pinewood](../validation/handling/pinewood-rhino-before-fix-r4.json) : marche et course normales, puis `MovementMode=3` après le saut, sol courant absent, glissade à environ 6,7 m/s malgré relâchement du stick. L'entrée renvoie « Approchez d'une porte du vehicule au sol pour remonter ». Le graphe reste chargé ; le mode Falling maintient la pose de saut non bouclée et supprime le freinage de marche. Le test plat initial ne reproduisait pas ce cas.

La cause précise du rejet de la première collision d'atterrissage n'est pas isolée. Les normales de sol avant saut sont proches de +Z : aucune modification spéculative du winding ou des assets routiers.

## Résultats vérifiés

| Essai | Résultat | Portée |
| --- | --- | --- |
| [Pente et braquage](../validation/handling/ground-r2.json) | Réussi, 6 contrôles | Trois Blueprints jouables, départ sur pente 10° pendant 8 s, virage plein braquage pendant 10 s à ~3 m/s |
| [Vol](../validation/handling/flight-r1.json) | Réussi | Virage >60° en 3 s à 300 km/h, trajectoire alignée à <25°, transformation/atterrissage, Rhino/module et proxy rotorcraft |
| [Route Thunderhawk](../validation/handling/route-Thunderhawk-r1.json) | Réussi | 9548 m, écart maximal 1,33 m, aucun intervalle sans contact roue |
| [Route Rhino](../validation/handling/route-Rhino-r1.json) | Réussi | 9548 m, écart maximal 0,93 m, aucun intervalle sans contact roue |
| [Route Hurricane](../validation/handling/route-Hurricane-r1.json) | Réussi | 9548 m, écart maximal 1,34 m, aucun intervalle sans contact roue |

Angles accumulés en dix secondes : Thunderhawk 331°, Rhino 165°, Hurricane 247°. Excursions maximales depuis le point de départ du virage : 7,97 m, 13,93 m et 8,37 m ; ce ne sont pas des rayons de braquage mesurés. Après huit secondes de montée : 33,1 / 53,9 / 19,0 km/h respectivement. Valeurs de gameplay, aucune spécification officielle de véhicule revendiquée.

La dernière correction CharacterMovement passe sur [Rhino à Pinewood](../validation/handling/pinewood-rhino-r5.json), [Hurricane à Pinewood](../validation/handling/pinewood-hurricane-r5.json), [Thunderhawk à Pinewood](../validation/handling/pinewood-thunderhawk-r5.json) et dans la [régression solo de tous les conducteurs](../validation/handling/onfoot-soak-r5.json). Marche douze secondes, course, saut restant en l'air à hauteur normale puis atterrissage, remontée dans le même véhicule. Avant le correctif, le même essai Rhino échoue ; après correction le personnage revient en Walking et freine normalement avant l'entrée.

La régression réseau à pied passe également, [hôte](../validation/handling/onfoot-network-host-r5.json) et [client](../validation/handling/onfoot-network-client-r5.json), deux sorties processus 0. Ce test utilise la plateforme historique, pas la route ni une mission coop Silent Valley.

## Reproduction

Depuis la racine du dépôt, utiliser les scripts existants :

```powershell
.\Tools\Migration\Test-Dynamics.ps1 -RunName <inédit> -Handling -WorkspaceCache
.\Tools\Migration\Test-Dynamics.ps1 -RunName <inédit> -WorkspaceCache
.\Tools\Migration\Test-OnFoot.ps1 -RunName <inédit> -Terrain -Vehicle Rhino -WorkspaceCache
.\Tools\Migration\Test-OnFoot.ps1 -RunName <inédit> -WorkspaceCache
.\Tools\Migration\Test-SilentValley.ps1 -RunName <inédit> -Vehicle Rhino -Fast -FullRoute -WorkspaceCache
```

`-Terrain` place explicitement le véhicule sur la route au mètre 800 ; il vérifie le terrain réel, sans plateforme de test, mais ne constitue pas un trajet piloté depuis le garage. `-Handling` utilise une plateforme inclinée puis plane et remet les véhicules en place entre scénarios. Les entrées Xbox sont simulées ; aucun essai à la manette physique ni FPS de conduite revendiqué. `-Fast` conserve son sens de temps fixe accéléré.

## Compilation et restrictions locales

Le build UBT standard n'a pas passé dans l'environnement restreint : écriture du journal UBA dans AppData refusée. UHT et export des actions produits par le dotnet UE installé, sans installation ni modification de profil. L'export se termine code 1 lors du nettoyage UBA ; ce n'est pas un build standard réussi.

Les commandes MSVC, lien DLL/lib et métadonnées exportées ont été exécutées avec leurs arguments et dépendances, [sorties vérifiées individuellement](../validation/handling/build-actions-r8.json), toutes sorties 0. Script de reprise local : `Saved/SilentValley/run-exported-build.ps1`, graphe `build-handling-actions.json`. Les lots antérieurs et échecs restent sous Saved. Les scripts de test offrent `-WorkspaceCache` pour leurs DDC/ShaderWorkingDir, sans changer les réglages globaux.

G2 manuel, carrière multivéhicule et comportement contre les limites restent ouverts. Les essais ci-dessus ne valident ni G3 artistique, ni mission Silent Valley, coop de mission, streaming, packaging ou rendu final.
