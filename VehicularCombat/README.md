# Vehicular Combat (Multiplayer)

## Unreal Engine 5.8 migration

La branche `migration/ue58` utilise Unreal Engine **5.8.2** et conserve le module `VehicularCombat` et le contenu original. Aucun asset M.A.S.K. n'est intégré.

Depuis ce dossier, avec le moteur installé :

```powershell
.\Tools\Migration\Invoke-UE58.ps1 -Task Build
.\Tools\Migration\Invoke-UE58.ps1 -Task Editor
```

Pour lancer directement le jeu : `-Task Play`. Dans le menu, créer une session LAN ou rejoindre celle d'un autre joueur. Conduite avec W/A/S/D ou les flèches ; frein à main Espace ; tir clic gauche ; armes 1/2 ; caméra V ; saut Maj gauche.

Pour tester seul : cliquer **Solo contre 3 bots**, ou lancer `-Task Solo`. **F10** retourne au menu. Host crée une partie pour les autres joueurs ; Join recherche leurs parties et n'est pas nécessaire après Host. [Correctifs du menu, mode solo et validation](docs/PLAYTEST_FIXES.md).

Tests reproductibles : `-Task Blueprints`, `-Task Assets`, `-Task Network` et `-Task NetworkRender`. Le premier démarrage graphique peut compiler les shaders pendant plusieurs minutes. Les scripts n'installent rien et conservent les résultats de chaque essai dans `Saved/Migration/`.

État réellement vérifié, limites et liste des fichiers : [résultats](docs/MIGRATION_RESULTS.md). [Audit](docs/MIGRATION_AUDIT.md), [journal](docs/MIGRATION_LOG.md), [proposition M.A.S.K. / Thunderhawk](docs/MASK_ARCHITECTURE_PROPOSAL.md).

## Introduction
Multiplayer Vehicular Combat prototype game developed in Unreal Engine with Chaos vehicles.  
This is not a production-ready project.

## Additional Notes
<!--- You can access the demo and pictures of the project [here](TODO).  -->
If you have any questions or suggestions, please feel free to [message me](https://github.com/DanialKama#-connect-with-me).

## Credits
- [Military Weapons Silver](https://www.unrealengine.com/marketplace/en-US/product/military-weapons-silver)
- [FPS Weapon Bundle](https://www.unrealengine.com/marketplace/en-US/product/fps-weapon-bundle)
- [FlatIcon](https://www.flaticon.com/)
