# Thunderhawk — revue des dix images fournies

Date : 2026-11-01. Les dix JPEG du dossier `art_source/Thunderhawk/Images reference/` ont été **ouverts et examinés visuellement**. Ce fait remplace la limitation d'accès aux images signalée dans les itérations précédentes. Les images restent des références d'observation ; aucune n'est appliquée au modèle comme texture.

## Ce que montrent les fichiers

| Fichier | Observation exploitable | Limite |
|---|---|---|
| `images.jpg` | Trois-quarts avant en vol : forme coudée des portes, phares séparés, canons au bord des ailes, montant central de toit | Petite image d'un jouet contemporain ; édition non établie dans ce fichier |
| `images (1).jpg` | Trois-quarts route : nez de Camaro, trois zones du capot, bas de caisse argenté, roues à cinq ouvertures, découpe de vitre | Décorations du jouet ; pas une preuve des couleurs de la série |
| `images (2).jpg` | Porte ouverte : partie supérieure de toit et flanc solidaire à angle marqué ; long rail/canon chromé en bord inférieur | Vue promotionnelle, perspective et articulation non mesurables exactement |
| `images (3).jpg` | Vue basse en vol : dessous des portes, canons, lèvre inférieure du nez et pièces latérales | Les accessoires de présentation et le pilote ne font pas partie de cette étape |
| `images (4).jpg` | Comparaison de dessus explicitement légendée « Ramen » et « Loyal Subjects » ; variantes du capot, toit et spoiler | Ces deux formes ne doivent pas être fusionnées en prétendant disposer d'un seul plan officiel |
| `images (5).jpg` | Trois-quarts arrière en route : volume du hayon vitré, panneau arrière et aileron bas | Très faible résolution |
| `images (6).jpg` | Face/haut : deux groupes de phares, prises basses séparées, capot central et bandes latérales ; logo TLS/Hasbro et copyright 2025 visibles | Réédition identifiée, pas le jouet original de 1985 |
| `images (7).jpg` | Dessus en vol : bande centrale du toit, portes coudées, canons en bord extérieur, proportion du capot | Édition non déterminée ; perspective non orthographique |
| `images (8).jpg` | Trois-quarts arrière en vol, aileron sur support central | Image trop petite pour relever la forme exacte des tuyères |
| `images (9).jpg` | Vue arrière la plus utile : contour oblong à coins arrondis des sorties, panneau arrière horizontal relevé, aileron séparé à support central, coude des deux portes | Une photo fixe ne donne ni course exacte ni timing ; profondeur des tuyères partiellement masquée |

Provenance et empreintes des fichiers : `user_reference_manifest_v7.csv`. Les URLs originales et droits ne sont pas établis. Les noms/dates de produits ne sont pas déduits d'un simple nom de fichier.

## Changements V7 directement guidés par ces vues

- Carrosserie reconstruite avec nez en coin plus court, flancs et ceinture de caisse définis, passages de roue découpés, capot distinct et relief central.
- Suppression de la barre lumineuse : deux logements rectangulaires réellement découpés dans le nez, avec deux petites optiques dans chacun, et deux prises basses séparées.
- Une porte est une coque solidaire comportant une feuille de toit, un cadre de vitre incliné et une partie latérale presque verticale. Le pivot reste proche du centre du toit. Les deux plans ne sont plus une seule plaque diagonale.
- Canons associés au bord inférieur des portes : rail longitudinal, tube, bague de bouche et ouverture séparés. Extension provisoire de 20 cm ; timing inventé pour l'essai, à comparer à une séquence vidéo.
- Tuyères circulaires remplacées par deux contours oblongs à coins arrondis, cavités sombres et éléments internes simples. L'observation ne permet pas de certifier la profondeur ou tous les détails internes.
- Aileron sur un support central ; mouvement propre de l'aileron et translation verticale du panneau arrière conservés. Les montants latéraux indépendants de V6 ont été retirés.
- Jantes à cinq ouvertures, bas de caisse et accents argentés, petits répétiteurs et rétroviseurs attachés aux portes.
- Livrée de recherche construite en géométrie originale : aplats violets, quadrillage et éclairs jaunes approximatifs. Elle sert à la reconnaissance du jouet, sans revendiquer la fidélité du dessin animé.

## Comparaison visuelle réellement effectuée

Les premiers rendus V7 `preview_road`, `preview_flight` et `preview_rear` ont été ouverts et comparés aux observations ci-dessus. Ils ont révélé deux défauts corrigés dans le générateur : phares encore saillants, et panneau arrière initialement trop plein autour des tuyères. Les rendus de validation finaux sont dans `renders/v7/`.

**À reprendre** : courbure du nez et de ses coins, raccords de porte au pare-brise/C-pilier, dessin exact des canons et de leurs supports, contour définitif du panneau arrière, détails et profondeur des tuyères, proportions précises entre variantes. Les surfaces restent une étude extérieure intermédiaire, pas un asset Hero.

**Non établi** : aucune image locale n'a été authentifiée comme capture du dessin animé de 1985. La fidélité à la série, les angles exacts, l'ordre image par image de la transformation et les dimensions officielles restent non validés. Aucune géométrie de cockpit n'est modélisée.

## Accès dans Blender

La collection `Reference_Study_UserImages` contient les dix références liées en chemins relatifs. Elle est masquée dans le viewport et exclue des rendus et exports ; l'activer permet de consulter la planche à côté du modèle. Les JPEG d'origine restent intacts dans leur dossier.
