"""Read the user-supplied YouTube reference interval for visual inspection."""
import sys,json
from pathlib import Path
P=Path(__file__).resolve().parents[3];sys.path.insert(0,str(P/'docs/qa/boulder_tools'))
import yt_dlp
from yt_dlp.utils import download_range_func
out=P/'docs/qa/boulder_video'
options={'format':'bestvideo[height<=480]/bestvideo/worst','outtmpl':str(out/'transformation_1_13.%(ext)s'),'noplaylist':True,'download_ranges':download_range_func(None,[(1,13)]),'force_keyframes_at_cuts':True,'retries':1,'extractor_retries':1,'socket_timeout':15,'quiet':False}
try:
 with yt_dlp.YoutubeDL(options) as y:
  info=y.extract_info('https://www.youtube.com/watch?v=CYgT9k8lJyY',download=True)
  (out/'source.json').write_text(json.dumps({'url':info.get('webpage_url'),'title':info.get('title'),'duration':info.get('duration'),'requested_interval':[1,13],'downloaded':True},indent=2))
except Exception as error:
 (out/'fetch_error.json').write_text(json.dumps({'url':'https://www.youtube.com/watch?v=CYgT9k8lJyY','error':str(error)},indent=2));raise
