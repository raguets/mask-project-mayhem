# Raven — corrections de carrosserie, toit et cassette

Lot du 11 novembre 2026, exécuté dans Blender ouvert par MCP local9876. V11 utilisateur non enregistrée préservée dans `art_source/Raven/Session_before_V12_20261111_195221.blend`. V12 à V16 conservées, sans écrasement de V11, du personnage V1 ou du masque V1.

## Changements

- Capot rigide lissé au niveau des épaules, retours et joints repris. Tableau de bord rentré ; plancher fixe arrêté àX0,425m, tunnel à0,405m pour dégager l'avant complet pivotant.
- Portes incurvées et doublées, retours de panneaux et joints de jambages. Quatre canons diamétraux élargis de45 à90mm, logements élargis, encastrement et charnières45° conservés.
- Cassette commune de quatre réacteurs : tout le bloc monte de0,197m. Carrosserie noire seulement dessus/flancs avec coins arrondis. Dessus horizontal fermé àZ0,79m. Buses au-dessus de la façade fixe de9mm en fin de course. Correction supplémentaire en profondeur : les deux buses extérieures traversaient visuellement la façade bombée au repos en V13 ; métal rentré de18mm en V14 et rendu fermé revérifié.
- Pare-brise au contour trapézoïdal courbe, d'après la photographie du jouet `s-l500.jpg`, sans confondre cette édition avec la Corvette réelle. Petit raccord avant toit/pare-brise, réduit après rejet de l'arrondi excessif V12.
- Toit central fixe et deux parties latérales solidaires des portes. Répartition initiale en tiers, puis ailes légèrement rétrécies à l'avant selon la correction utilisateur. Raccord formé arrondi entre vitrage latéral et aile de toit. Coins des vitrages fixes et joints repris en V16 pour supprimer les extrémités saillantes vues en V15.
- Lunette allongée jusqu'àX−1,815m près de la cassette, contour arrondi et matériau distinct très sombre. Montants noirs derrière les portes, raccords de custode et plage intérieure.

Les dimensions, profils cachés et raccords non cotés restent des interprétations. Les nouvelles précisions sont dans `AGENTS.md` et la fiche de transformation. Les contrôles d'animation existants restent inchangés.

## Validation

V14 :21 contrôles géométriques passés,33 états pneus/carrosserie,12 PNG Cycles GPU terminés. V15/V16 : nouvelles vues ciblées du raccord vitre/toit, ailes déployées, toit vu du dessus et lunette/montants. Voir les rapports JSON et manifests réels sous `art_source/Raven`. Un rendu ou une sauvegarde ne valide pas à lui seul toute l'animation.

Résultat final V16 :24 contrôles passés (`validation_v16.json`), aucune intersection dans les paires pneus/carrosserie sur33 états ni nouvelles pièces de toit/vitrages fixes sur31 états après départ. Huit PNG1280×960 Cycles GPU28 échantillons, tous réellement ouverts et inspectés ; `renders/v16_review/COMPLETE` présent, aucun ERROR. Les arêtes d'accostage à l'état fermé sont exclues du test mobile de toit ; pas de certification exhaustive des volumes balayés.

Exports réellement sauvegardés puis rouverts : `Raven_V16_Vehicle.blend`, `../Calhoun_Burns/CalhounBurns_V2.blend`, et masque inchangé `CalhounMask_V1.blend`. `standalone_validation_v16.json` passe pour les trois : dépendances, drivers, pneus persistants, cassette sans rotation/course0,197m, même personnage/poids dans les quatre états. `checkpoint_v16.json` décrit l'assemblage restauré et enregistré frame1, hauteur de présentation0, Raven_Control sélectionné. Aucun rendu essentiel encore actif.

## Limites conservées

Pas de retopologie/UV finale ou intégration Unreal. Personnage encore stylisé : peau, cheveux, plis et contact des mains/pédales à raffiner. Les bornes du dessus des bottes en conduite descendent àZ0,126m pour un plancher haut à0,160m : contact pied/plancher non validé et à reprendre par coupe dédiée, sans prétendre qu'un contrôle pneus/carrosserie couvre le pilote. Orientation mondiale du tir des canons arrière à vérifier après bascule des roues ; le contrôle45° local ne suffit pas à la certifier.
