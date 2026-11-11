# Matt Trakker V5 et Spectrum V4

Sources Blender indépendantes : `MattTrakker_V5.blend` et `Spectrum_V4.blend`.
Assemblage dans `../Thunderhawk/Thunderhawk_V14.blend`. Les versions précédentes restent conservées.

V5 : tête abaissée au repos, cou reconstruit en surface continue dans la tête existante, poids et compression en conduite corrigés. Spectrum V4 : coque abaissée et bas élargi, collerette rouge évasée ajustée aux épaules dans les deux poses. Les cotes et la jupe souple sont une interprétation. Vues et contrôles : `../Thunderhawk/renders/v14/`, `../Thunderhawk/validation_v14.json`, `../Thunderhawk/standalone_validation_v14.json`. Compte rendu détaillé : `../../docs/progress/2026-11-03-V14.md`.

V4 : interprétation humaine réaliste du portrait fourni, explicitement autorisée par le porteur le 2 novembre 2026, sans ressemblance à une personne précise. Anatomie générique de Blender Human Base Meshes adaptée au même personnage ; le même objet tête, la même combinaison pondérée et la même armature sont conservés. Gants continus et prise de conduite pilotée, casque Spectrum V3 bombé avec front incliné et mâchoire resserrée. Sources anatomiques CC0 et provenance dans `../AnatomyBase/` et `anatomy_provenance_v4.json`.

La passe V3 antérieure avait repris les bottines noires à revers rouges depuis la photographie de figurine `images (3).jpg`. Elles restent présentes dans V5. Les dimensions et parties non montrées sont estimées.

## Commandes du personnage

Sélectionner `MattTrakker_Rig`, puis ouvrir Propriétés de l’objet > Propriétés personnalisées.

- `driving_pose = 0` : debout ; `driving_pose = 1` : conduite.
- `mask_on = False` : visage visible ; `mask_on = True` : Spectrum par-dessus le même visage.

Un seul corps, une seule tête, une seule armature. Le casque est une collection séparée : coque rigide liée à `head`, collerette souple influencée en bas par les poids du vêtement (poitrine/épaules). Les cheveux sont masqués sous le casque. Les poses ne dépendent pas de la timeline de transformation de la voiture.

La collection `MT_EditableLoftCages` contient les cages de vêtements d’origine, masquées et préservées. `MT_PreviousHandSources` conserve les anciens composants des gants, masqués. Ces sources ne sont pas des variantes de personnages affichées. La combinaison visible est une surface continue pondérée. Le fichier Spectrum seul n’a ni dépendance à Matt ni dépendance à Thunderhawk ; son origine `Spectrum_HeadSocket` correspond à l’origine de l’os tête au repos (`rest_bind_origin` conservé). Les groupes de poids de la collerette sont conservés pour le remontage sur une armature compatible ; une parenté rigide à la tête seule ne reconstruit pas son ajustement aux épaules. La version attachée est incluse dans le fichier Matt.

## Références et limites

Les huit références fournies ont été inspectées. Le portrait dessiné `images (7).jpg` guide le visage blond à mâchoire carrée. Les autres sources comprennent illustrations, photographies de figurines de différentes éditions et répliques du masque ; elles ne constituent pas un scan ou un turnaround photographique officiel. La géométrie anatomique, les surfaces non montrées et certaines dimensions sont estimées.

Cette passe est une interprétation semi-réaliste, pas une ressemblance photoréaliste certifiée. La combinaison conserve une topologie de sculpture ; retopologie, UV et affinage de déformation restent nécessaires pour un asset de jeu final. La fidélité artistique reste à apprécier sur les rendus, pas à déduire du succès des scripts.

## Reproduction de la passe V2 d'origine

Dans Blender, partir de la V10 préservée et exécuter successivement les scripts du dossier Thunderhawk/scripts :

1. `build_thunderhawk_v11.py`
2. `refine_thunderhawk_v11.py`
3. `finish_thunderhawk_v11.py`
4. `finalize_thunderhawk_v11.py`

Utiliser ensuite `export_characters_v11.py` dans un processus séparé ouvert sur la V11. Ce script réduit sa scène en vue de l’export et ne doit pas être exécuté dans la scène de travail sans la sauvegarder auparavant. `review_thunderhawk_v11.py` produit les vues ; `verify_characters_v11.py` vérifie les fichiers indépendants.

La passe V3/V12 se trouve dans les scripts `build_thunderhawk_v12.py`, `finalize_thunderhawk_v12.py`, `export_assets_v12.py` et `verify_assets_v12.py`, à exécuter par MCP Blender sur les sources adaptées. Les nouveaux exports ont été rouverts dans Blender ; rapport `../Thunderhawk/standalone_validation_v12.json`. Rendus dans `../Thunderhawk/renders/v12/`.
