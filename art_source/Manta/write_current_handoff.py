from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
text='''# Handoff — Manta / Vanessa / Whip — 14 novembre 2026

## Objectif, priorité et état réel

Modéliser Manta, Vanessa Warfield et Whip depuis les références fournies. Route / avion sans stationnaire. Fiche lue avant images ; compétence `.agents/skills/mask-asset-production/SKILL.md` et branches lues. Anatomie/cockpit interprétés avec autorisation générale. Ne pas confondre photos de jouets, Nissan Z31 réelle et illustrations/captures : registre `art_source/Manta/REFERENCE_NOTES.md`.

**Travail en cours, non approuvé.** L'utilisateur a répété plusieurs corrections insuffisamment appliquées et demande désormais de tout traiter en une fois. Liste canonique complète : `art_source/Manta/CORRECTIONS_UTILISATEUR.md`, à lire AVANT toute retouche. Ne pas cocher sur la seule réussite d'un script. Les versions V1–V14 ne sont pas des livraisons validées. V14 a des erreurs d'assemblage reconnues : roues sous la carrosserie, sièges/dossiers trop reculés, panneau de feux pas devant les jets, toit en pente. Sa file de rendu a été arrêtée proprement (callback désenregistré et état restauré), `renders/v14/CANCELLED.json`.

## Reprise consolidée

V15 (`art_source/Manta/Manta_V15_Assembly.blend`) réécrit les pivots en coordonnées LOCALES, inverses de parenté identité et drivers explicites des positions de repos. Cause diagnostiquée : les anciens changements de repères avaient été annulés à la réévaluation alors que les maillages/inverses étaient déplacés. Voir `diagnose_assembly_v14.json`. Réparer les contrôleurs, pas les arches. Arches maintenant circulaires, rayon .340 m ; cibles d'essieux dans `proportions_v13.json` : avant 1.30898, arrière -1.38808 m. Ratios nominaux 40/30/30 autour des portes [-.94,.47], extérieur environ 4.70 m.

V15 reconstruit aussi sièges plus avant, toit central horizontal, pare-brise bas trapézoïdal (base1.50/top1.20 m) avec vraie courbure 55mm, trois vitres arrière plus courbes et volume réduit. Conductrice/commandes +Y à gauche. Ailes davantage en arrière, +50% de largeur courante (racine .72 m), stockées |Y|<=.72 avant pneu intérieur .725, racines sous caisse ; roues entraînées en turbines et supports agrandis. Montants porte-feux doublés avant/arrière et minces gauche/droite.

Les autres demandes sont conservées depuis V14 : capot central avec quart arrière fixe, nez marteau plat mince sous canons courts indépendants, trous rectangulaires sans blanc, absence de pare-chocs/bandes noires, missiles courts à 30 degrés, cheveux raccourcis. Elles doivent TOUTES être revérifiées sur la version consolidée : pas encore de déclaration de fidélité ni d'absence universelle de collisions.

## Outils, contrôles, limites

Blender MCP 9876 répond ; transport `python3.12 .agents/skills/mask-asset-production/scripts/mcp_client.py execute_code --code-file <script> --timeout 120 --output <json>`. `python` seul est un alias inaccessible. Blender GUI lancé par l'agent avec l'add-on installé ; aucun remplacement de la production MCP par du background. Toutes les anciennes sources conservées. Base féminine CC0 dans `art_source/AnatomyBase`, même corps/face/rig pour quatre états, Whip séparé.

Au moment de cette note : validation V15 lancée par `validate_v15.py`, résultat `validation_v15_result.json` et rapport `validation_v15.json` à lire. Script suivant préparé : `final_clearance_adjust_v16.py`, ajuste sommets des montants et garde les jets rentrés pendant le début de levée du panneau. Aucun export indépendant final encore. Les rendus V11 terminés sont périmés ; V14 annulés. Refaire les vues de la version consolidée et inspections avant export/réouverture des sources indépendantes. Aucun code, import ou gameplay Unreal touché.

## Git et continuité

Dépôt réel à la racine workspace, branche main, HEAD `bae5272 Added switchblade`, puis `837f48c` et `c0ef9cd`. Index vide au dernier contrôle. Préserver changements utilisateur : fiche Manta modifiée, références Switchblade déplacées vers `Images de reference/Terminés/Switchblade et Miles Mayhem`, dossier Firefly non suivi. Travail agent : `art_source/Manta/` non suivi, HANDOFF modifié ; pas de commit. Ancien handoff archivé `docs/progress/2026-11-14-handoff-before-manta.md`.

## Première action recommandée

Lire `art_source/Manta/CORRECTIONS_UTILISATEUR.md` puis `art_source/Manta/validation_v15.json`, vérifier MCP et la source réellement ouverte avant de poursuivre les contrôles et corrections de la version consolidée.
'''
(P/'HANDOFF.md').write_text(text,encoding='utf-8')
print('HANDOFF_PARTIAL_UPDATED')
