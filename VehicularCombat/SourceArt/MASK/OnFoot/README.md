# Conducteurs à pied

Sources indépendantes dérivées le 8 novembre 2026 des fichiers `SourceArt/MASK/Editable`, sans modifier les originaux. Chaque dossier contient le même personnage, son squelette à 17 os, sa tête et son masque séparé, ainsi que les actions d'origine et 18 nouvelles actions. La propriété d'armature `mask_on` conserve le visage sous le masque.

Les allures et la posture de tir sont des interprétations humaines génériques créées pour le jeu, sans mocap ni ressource tierce ajoutée. Deux segments résolus analytiquement préservent la longueur des membres. Marche : 150 cm/s ; course : 400 cm/s ; huit directions par allure, clips sur place ; repos et saut séparés. La racine n'entraîne pas la capsule : CharacterMovement gère le déplacement, le sol et le réseau.

`Tools/Art/author_onfoot_motion.py` s'exécute par la connexion Blender MCP installée. Il sauvegarde un fichier éditable par conducteur, puis exporte une armature temporaire en centimètres correspondant exactement au nom de racine du squelette déjà importé. Ne pas appliquer le facteur 100 une seconde fois. `import_onfoot_motion.py` importe les animations seules sur les quatre squelettes existants et crée les BlendSpaces dans `/Game/MASK/OnFoot`.

Les rendus de contrôle Blender, masqués/démasqués et en marche/course/saut, sont conservés dans `Saved/Art/onfoot/review` ; le rapport d'import est dans `Saved/Art/onfoot/import.json`. Le rendu en jeu doit également être contrôlé : un FBX valide ne démontre pas la bonne déformation, la prise de l'arme ou la réplication.

Limites artistiques : rig existant sans doigts articulés, prise du fusil approximative, sans animation dédiée de rechargement, de mort ou d'ouverture de porte. La sortie et l'entrée sont des changements de position contrôlés. Les nouvelles actions ne constituent pas une amélioration des maillages ou une validation de réalisme photographique.
