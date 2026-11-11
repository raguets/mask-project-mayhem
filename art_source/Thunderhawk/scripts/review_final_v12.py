import os
from pathlib import Path
os.environ['THK12_VIEWS']='cabin,pedals_cutaway,road'
exec(compile(Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk/scripts/review_thunderhawk_v12.py').read_text(), 'review_thunderhawk_v12.py','exec'))
os.environ.pop('THK12_VIEWS',None)
