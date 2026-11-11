from pathlib import Path
P=Path(__file__).resolve().parents[3];A=P/'art_source/Boulder_Hill'
p=A/'README.md';old=p.read_text(encoding='utf-8');(A/'README_v4.md').write_text(old,encoding='utf-8')
new=old.replace('# Boulder Hill V4','# Boulder Hill V6').replace('BoulderHill_V4_','BoulderHill_V6_').replace('Les versions V1 à V3','Les versions V1 à V5')
parts=new.split('\n\n',2);parts.insert(2,"V6 corrige l'aspect : marron chaud intermédiaire après le rejet du beige V4 et du brun trop sombre V5. Lumière d’ambiance renforcée, soleil et lumière principale relevés, grand éclairage frontal doux. Le viewport utilise les lumières et le monde de la scène. Géométrie et mécanismes identiques à V4 ; leurs contrôles restent applicables. Les deux vues V6 servent à vérifier la couleur et l’éclairage.");new='\n\n'.join(parts)
new=new.replace('Rendus : `renders/v4/`.','Rendus actuels de couleur et d’éclairage : `renders/v6/`. Les huit vues géométriques V4 restent dans `renders/v4/`.')
new=new.replace('Synthèse : `validation_v4.json`.','Synthèse géométrique V4 : `validation_v4.json`. Correction et réouverture V6 : `color_light_v6.json` et `validation_v6.json`.')
p.write_text(new,encoding='utf-8')
p=P/'README.md';text=p.read_text(encoding='utf-8');a=text.index('## Boulder Hill V4');b=text.index('## Rhino V3',a);section=text[a:b].replace('Boulder Hill V4','Boulder Hill V6').replace('BoulderHill_V4_','BoulderHill_V6_').replace('renders/v4/','renders/v6/')
section=section.replace('Base secrète adossée','Couleur V6 : marron chaud intermédiaire et éclairage de scène renforcé. Géométrie et mécanismes V4 conservés. Base secrète adossée')
p.write_text(text[:a]+section+text[b:],encoding='utf-8')
# Reuse the verified normal-save export and reopen workflow with version-specific reports.
code=(A/'scripts/export_base_v4.py').read_text(encoding='utf-8').replace('V4','V6').replace('export_v4','export_v6')
(A/'scripts/export_base_v6.py').write_text(code,encoding='utf-8')
code=(A/'scripts/reopen_check_v4.py').read_text(encoding='utf-8').replace('V4','V6').replace('boulder_standalone_final.json','boulder_standalone_v6.json')
code=code.replace("report[kind]={'file'", "assert bpy.data.objects.get('BH_SoftDayFill') is not None\n    assert abs(bpy.data.materials['BH_Sandstone'].diffuse_color[0]-.21)<.0001\n    report[kind]={'file'")
(A/'scripts/reopen_check_v6.py').write_text(code,encoding='utf-8')
print('V6 notes and export prepared')
