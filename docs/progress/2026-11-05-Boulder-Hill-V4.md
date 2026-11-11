# Boulder Hill V4 — 5 novembre 2026

Base modélisée et inspectée dans Blender via MCP. Sources : `art_source/Boulder_Hill/BoulderHill_V4_Assembly.blend` et `BoulderHill_V4_Base.blend`. Versions et sessions précédentes conservées.

La devanture est un prisme triangulaire unique qui pivote de 90° : sa vitrine va au sol, la face inclinée blindée devient visible. La montagne reprend la forme approuvée, réduite à environ 32 m, avec un contrefort rejoignant son flanc. Les raccords latéraux et le couvre-joint derrière le toit ferment les vides. Dalle rectangulaire compacte, sans route rapportée.

Pompes, panneau GAS, deux canons d'enseigne, cap rocheux, canon/fauteuil et garage en quart de cercle sont animés avec des propriétés et drivers natifs. Les deux battants possèdent un axe déporté et un jeu par rapport à la coque. Quatre places et une allée utilisent l'échelle réelle des meshes Rhino V3 et Thunderhawk V14. Les copies de démonstration sortent successivement, Thunderhawk poursuivant sa route sur le terrain pour libérer le passage.

Contrôles finaux : quatre trajectoires de 241 échantillons avec gabarit Rhino et trois autres places occupées ; 41 phases d'ouverture des battants ; 81 phases pour chacun des sept groupes mobiles ; 541 images pour l'espacement des deux véhicules de démonstration. Aucune intersection signalée dans ce périmètre. La face vitrée du prisme reste au-dessus du sol dans les phases échantillonnées. Sources rouvertes ; drivers valides ; base indépendante sans véhicules ni dépendances manquantes. Huit rendus V4 inspectés après les dernières corrections.

Les contrôles discrets de surfaces ne prouvent pas l'absence de toute collision continue ni de volume entièrement contenu. Les dimensions, structures cachées, relief et aménagements restent des interprétations. La chute, les véhicules et leur passage sur le terrain ne sont pas des simulations physiques. Finition et fidélité sont documentées par les vues, sans revendication métrologique ou de préparation Unreal finale.

Commandes, fichiers de référence, méthodes et rapports détaillés : `art_source/Boulder_Hill/README.md`, `validation_v4.json` et `docs/qa/boulder_*final.json`.
