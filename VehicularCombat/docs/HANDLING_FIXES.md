# Hurricane : roues arrière et vitesse de vol

**Clarification suivante : [la plage avion est désormais de 50 à 300 km/h](AIRCRAFT_SPEED_RANGE.md).** La correction de suspension ci-dessous est conservée ; les chiffres 65–108 décrivent la livraison précédente.

8 novembre 2026, branche `fix/hurricane-wheel-flight-speed`, depuis `cfaf65c`.

## Corrections

La vitesse cible maximale du profil de vol partagé passe de **60 à 30 m/s**, soit **216 à 108 km/h**. Le minimum avion reste à 18 m/s (64,8 km/h). L'accélération et le freinage restent progressifs ; aucune vitesse de corps rigide n'est écrasée pour appliquer ce réglage. Une collision, une descente ou une vitesse routière initiale supérieure peuvent produire un dépassement transitoire, corrigé par les forces de vol.

Le tremblement arrière d'Hurricane est reproduit sur une plateforme plane : le décalage des deux suspensions arrière alterne entre **0 et −12 cm** à l'arrêt, avec pertes de contact. Les suspensions avant restent proches de −5,7 cm. Les sources UE 5.8 montrent que `SetupVehicle` utilise des pointeurs vers les configurations des objets par défaut des classes de roues. La même classe sert aux roues arrière et centrales ; `SetSuspensionParams` modifie donc aussi les suspensions arrière quand la paire centrale est rentrée.

`UMaskVehicleMovementComponent` copie les configurations de roue et suspension **par roue et par véhicule** à la création physique, avant les changements de mode. Les pointeurs restent stables pendant la simulation. La masse suspendue et l'amortissement sont recalculés sur ces copies. Aucun lissage visuel ne cache la perte de contact ; les six emplacements Chaos restent persistants. Les constructeurs transmettent `FObjectInitializer` pour remplacer le composant de mouvement uniquement dans la famille M.A.S.K. Le véhicule original conserve son composant. Dépendance native ajoutée : `ChaosVehiclesCore`. Aucun fichier moteur ou asset artistique modifié.

## Validation

La sonde `MASK.HurricaneWheelProbe`, accessible par `Test-Hurricane.ps1 -WheelProbe -Render`, mesure le débattement à chaque image sur une plateforme temporaire, avant et après conduite/freinage. La version corrigée ajoute un second Hurricane qui se transforme indépendamment pour contrôler l'absence de contamination entre véhicules. Les deux fenêtres d'arrêt doivent rester sous 1 cm de variation ; au moins 95 % des images de conduite sur sol plat doivent conserver les contacts arrière.

La sonde de dynamique maintient maintenant RT dix secondes en vol horizontal, mesure la vitesse cible et la vitesse réelle, puis contrôle l'atterrissage et le reste des transformations. Ces essais utilisent les vrais véhicules, avec événements de manette injectés ; aucun essai physique de manette n'est revendiqué.

Distribution finale : **`MASK-Handling-Development-r1`**, UE 5.8.2 Win64 Development, BuildCookRun réussi en 116,92 s. `Jouer-MASK.cmd` pointe vers cette version. Les précédentes distributions et les sources Blender sont conservées. Compilation Editor et Blueprints réussies (0 erreur, 0 avertissement de compilation Blueprint, 0 échec de chargement). [Métadonnées et empreinte](validation/handling/package.json).

| Essai sur l'exécutable Windows final | Résultat |
|---|---|
| Stabilité arrière et deux Hurricanes dans des modes différents | [6/6](validation/handling/packaged-wheel.json), sortie 0 |
| Transformation, roues, armes, pilote masqué et changement de véhicule Hurricane | [23/23](validation/handling/packaged-hurricane.json), sortie 0 |
| Dynamique solo, vitesse maximale, atterrissage, Rhino et profil hélicoptère de substitution | [31/31](validation/handling/packaged-dynamics.json), sortie 0 |
| Réseau, deux processus listen/client | [7 hôte + 24 client](validation/handling/packaged-network.json), deux sorties 0 |

Les quatre variations arrière mesurées à l'arrêt valent **0 cm**, contre 12 cm avant correction. Aucun contact arrière perdu sur **89 images** de roulage sur sol plat. Le premier relevé d'arrêt, avant toute commande, est directement comparable à la sonde [avant correction](validation/handling/wheel-baseline.json) ; le freinage de la nouvelle sonde utilise le frein à main pour éviter de repartir en marche arrière avec LT.

Après dix secondes RT en palier, Thunderhawk atteint environ **106,4 km/h** avec une consigne de **108 km/h**. Le minimum, l'inclinaison en virage et l'atterrissage automatique restent validés en local et en réseau. La capture d'Hurricane en route a été inspectée ; les mesures temporelles vérifient le tremblement que cette image fixe ne permet pas d'évaluer. Les résultats Editor passent également. Aucune instance de test/éditeur ne reste ouverte.

Reproduction depuis le dépôt, en choisissant un nouveau `RunName` à chaque passe :

```powershell
$maskExe = (Resolve-Path 'Saved/Packages/MASK-Handling-Development-r1/Windows/VehicularCombat/Binaries/Win64/VehicularCombat.exe').Path
& Tools/Migration/Test-Hurricane.ps1 -RunName new-wheel -WheelProbe -Render -GameExecutable $maskExe
& Tools/Migration/Test-Hurricane.ps1 -RunName new-hurricane -Render -GameExecutable $maskExe
& Tools/Migration/Test-Dynamics.ps1 -RunName new-dynamics -Render -GameExecutable $maskExe
& Tools/Migration/Test-Dynamics.ps1 -RunName new-network -Network -Render -GameExecutable $maskExe
```
