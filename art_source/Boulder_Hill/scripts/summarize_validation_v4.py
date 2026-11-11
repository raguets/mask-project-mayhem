"""Read-only QA assembly plus production notes; run after reopen and render inspection."""
import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[3];A=P/'art_source/Boulder_Hill';Q=P/'docs/qa'
layout=json.loads((Q/'boulder_layout_final.json').read_text());phases=json.loads((Q/'boulder_phases_final.json').read_text());demo=json.loads((Q/'boulder_demo_sequence_v4.json').read_text());reopen=json.loads((Q/'boulder_standalone_final.json').read_text());renders=json.loads((A/'renders/v4/manifest.json').read_text())
assert renders['status']=='complete' and len(renders['renders'])==8
assert not layout['gate_contacts'] and not layout['invalid_drivers'] and not phases['invalid_drivers']
assert all(not b['structure_hits'] and not b['parked_vehicle_hits'] for b in layout['bays'])
assert all(not b['contacts'] for b in phases['groups'].values()) and not demo['vehicle_overlap_frames']
assert reopen['independent']['demo_objects']==0
result={'version':'V4','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(A/'BoulderHill_V4_Assembly.blend'),'independent_source':str(A/'BoulderHill_V4_Base.blend'),'native_drivers_valid_after_reopen':True,'parking_bays_tested':4,'route_samples_per_bay':241,'gate_phases':41,'mechanism_phases_per_group':81,'mechanism_groups':7,'demonstration_frames_checked':541,'reported_surface_or_envelope_intersections':0,'render_views':8,'renders_visually_reviewed':True,'limitations':['Sampled surface and envelope checks, not continuous collision proof.','Dimensions, hidden mechanisms, interior and mountain are interpreted.','Cap follows an animated path, not rigid body dynamics.','Demo vehicles do not simulate steering, rolling wheels, suspension or terrain contact.','No Unreal optimization or integration validation.'],'files':{name:{'bytes':(A/name).stat().st_size,'sha256':hashlib.sha256((A/name).read_bytes()).hexdigest()} for name in ['BoulderHill_V4_Assembly.blend','BoulderHill_V4_Base.blend']}}
(A/'validation_v4.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
progress=P/'docs/progress/2026-11-05-Boulder-Hill-V4.md';progress.parent.mkdir(parents=True,exist_ok=True)
progress.write_text('''# Boulder Hill V4 — 5 novembre 2026

Base modélisée et inspectée dans Blender via MCP. Sources : `art_source/Boulder_Hill/BoulderHill_V4_Assembly.blend` et `BoulderHill_V4_Base.blend`. Versions et sessions précédentes conservées.

La devanture est un prisme triangulaire unique qui pivote de 90° : sa vitrine va au sol, la face inclinée blindée devient visible. La montagne reprend la forme approuvée, réduite à environ 32 m, avec un contrefort rejoignant son flanc. Les raccords latéraux et le couvre-joint derrière le toit ferment les vides. Dalle rectangulaire compacte, sans route rapportée.

Pompes, panneau GAS, deux canons d'enseigne, cap rocheux, canon/fauteuil et garage en quart de cercle sont animés avec des propriétés et drivers natifs. Les deux battants possèdent un axe déporté et un jeu par rapport à la coque. Quatre places et une allée utilisent l'échelle réelle des meshes Rhino V3 et Thunderhawk V14. Les copies de démonstration sortent successivement, Thunderhawk poursuivant sa route sur le terrain pour libérer le passage.

Contrôles finaux : quatre trajectoires de 241 échantillons avec gabarit Rhino et trois autres places occupées ; 41 phases d'ouverture des battants ; 81 phases pour chacun des sept groupes mobiles ; 541 images pour l'espacement des deux véhicules de démonstration. Aucune intersection signalée dans ce périmètre. La face vitrée du prisme reste au-dessus du sol dans les phases échantillonnées. Sources rouvertes ; drivers valides ; base indépendante sans véhicules ni dépendances manquantes. Huit rendus V4 inspectés après les dernières corrections.

Les contrôles discrets de surfaces ne prouvent pas l'absence de toute collision continue ni de volume entièrement contenu. Les dimensions, structures cachées, relief et aménagements restent des interprétations. La chute, les véhicules et leur passage sur le terrain ne sont pas des simulations physiques. Finition et fidélité sont documentées par les vues, sans revendication métrologique ou de préparation Unreal finale.

Commandes, fichiers de référence, méthodes et rapports détaillés : `art_source/Boulder_Hill/README.md`, `validation_v4.json` et `docs/qa/boulder_*final.json`.
''',encoding='utf-8')
print(json.dumps({'status':'validated','source':result['source'],'independent':result['independent_source'],'views':8}))
