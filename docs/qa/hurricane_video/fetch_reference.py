import sys,json
from pathlib import Path
P=Path(__file__).resolve().parents[3];sys.path.insert(0,str(P/'docs/qa/boulder_tools'))
import yt_dlp
out=P/'docs/qa/hurricane_video';out.mkdir(parents=True,exist_ok=True)
url='https://www.youtube.com/shorts/YUgEYpsLrc4'
opts={'format':'bestvideo[height<=720]/bestvideo/worst','outtmpl':str(out/'toy_transformation.%(ext)s'),'noplaylist':True,'retries':1,'extractor_retries':1,'socket_timeout':20,'quiet':False}
with yt_dlp.YoutubeDL(opts) as y:
    info=y.extract_info(url,download=True)
    (out/'source.json').write_text(json.dumps({'url':url,'title':info.get('title'),'duration':info.get('duration'),'downloaded':True,'source':'User-supplied toy transformation video'},indent=2))
