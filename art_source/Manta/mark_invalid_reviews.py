from pathlib import Path
import json
P=Path(__file__).resolve().parents[2]
for path,reason in [
 ('art_source/Manta/renders/v23_character','INVALID: presentation action overrode requested pose/mask states. Use v24_character.'),
 ('VehicularCombat/Saved/Art/smoke-manta-render-r2','Dynamic checks passed but visual issue: two apparent loose rear panels. Not final visual validation.'),
 ('VehicularCombat/Saved/Art/smoke-manta-render-r3','Dynamic checks passed but rear-panel visual issue persists. Runtime transform diagnosis in progress.')]:
 (P/path/'INVALID_VISUAL_REVIEW.json').write_text(json.dumps({'reason':reason},indent=2))
