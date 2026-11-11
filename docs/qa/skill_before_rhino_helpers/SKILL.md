---
name: mask-asset-production
description: "Create or refine M.A.S.K. vehicle, articulated character and detachable mask assets in Blender MCP from inspected user references. Use for cars, trucks, planes and helicopters, including transformation fit reviews and reusable editable sources."
---

# Production d’assets M.A.S.K.

Objectif : obtenir une première passe cohérente à partir des références, puis une amélioration démontrée par les vues et contrôles. Une sauvegarde, un script réussi ou un test de timing ne prouvent pas la qualité artistique.

## Commencer par les bonnes contraintes

Lire les `AGENTS.md` et le compte rendu de la dernière version dans le projet actif. Examiner la scène réellement ouverte par MCP ; préserver son état non enregistré avant de charger une autre source. Ne pas supposer que l’assemblage est ouvert : le fichier peut ne contenir que le véhicule ou le masque.

Inspecter les images fournies/approuvées. Distinguer véhicule réel, édition de jouet, réplique et illustration ; ne pas fusionner leurs différences en prétendant disposer d’un plan officiel. Demander les vues manquantes avant de définir une silhouette ou un mécanisme non référencé. Une interprétation explicitement autorisée est possible : consigner l’autorisation et identifier les dimensions/kinématiques estimées. Ne pas redemander une autorisation déjà donnée.

Avant le détail, fixer les vues de comparaison, les repères d’échelle, les pièces mobiles et les zones de contact. Bloquer une silhouette et tester les assemblages avec des rendus simples avant de multiplier les accessoires, cheveux ou shaders.

## Choisir la branche utile

- Véhicule, camion, avion ou hélicoptère : lire [references/vehicles.md](references/vehicles.md).
- Personnage, pose, cou ou casque : lire [references/characters-masks.md](references/characters-masks.md).
- MCP, rendus, contrôles ou exports : lire [references/blender-operations.md](references/blender-operations.md).
- Réutilisation des résultats Thunderhawk/Matt/Spectrum : consulter [references/verified-lessons.md](references/verified-lessons.md). Ces résultats sont locaux au cas étudié ; ils ne valident pas les futurs véhicules.

## Principes qui restent communs

1. Un véhicule, un personnage et un masque ont chacun une source `.blend` éditable, plus l’assemblage. Conserver les anciennes versions.
2. Un seul personnage et une seule tête pour debout/assis et casque visible/caché. Conserver le visage sous le masque, les poids et l’armature ; utiliser des commandes explicites ou des poses nommées.
3. Déduire les pivots et dépendances des formes visibles. Les courses et séquences non documentées restent estimées. Ne pas appliquer la transformation de Thunderhawk à un camion ou un aéronef.
4. Contrôler les maillages évalués : silhouette, proportions, contacts et pièces mobiles, à plusieurs angles et phases. Séparer résultat géométrique, observation visuelle et limite non vérifiée.
5. Corriger les défauts visibles, rendre à nouveau les vues affectées, puis exporter et rouvrir réellement chaque source indépendante.

## Outils réutilisables

Les scripts s’exécutent **dans Blender par MCP**, sauf le client de transport local :

- `scripts/render_review_queue.py` : reçoit `RENDER_JOB`, rend une vue par callback, restaure l’état et écrit `COMPLETE` ou `ERROR.json`.
- `scripts/export_components.py` : reçoit `EXPORT_JOB`, recharge la source avant chaque isolation en mémoire, sauvegarde par l’opérateur ordinaire puis restaure la source. La source ne peut pas être une destination.
- `scripts/mcp_client.py` : transport de secours vers l’add-on local installé si les outils MCP dédiés ne sont pas exposés. Son port par défaut vient du projet d’origine ; vérifier le port de la connexion utilisée.

Les paramètres et précautions figurent dans [references/blender-operations.md](references/blender-operations.md). Adapter les noms/collections à la scène réelle ; les scripts n’autorisent pas de nouvelles actions externes. Ne pas lancer deux files qui modifient la même scène simultanément.

## Livrer avec des preuves utiles

Fournir la source active, les sources indépendantes rouvertes, quelques vues lisibles et un compte rendu indiquant ce qui est validé ou encore imparfait. Préserver les références et versions antérieures. Les checklists améliorent la première passe ; elles ne garantissent ni fidélité extrême, ni absence de toute collision, ni état final de jeu sans les vérifications correspondantes.
