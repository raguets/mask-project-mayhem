"""Rasterize our editable procedural flame outlines; no reference image modified."""
from pathlib import Path
import ast,json,math,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'docs/qa/hurricane_tools'))
import numpy as np
from PIL import Image,ImageDraw
A=Path(__file__).resolve().parents[1];tree=ast.parse((A/'scripts/paint_flames_v4.py').read_text());poly=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='sidepoly' for t in n.targets))
def rounded(poly):
 pts=[np.array(p,dtype=float) for p in poly];out=[]
 def tangent(i):
  a=pts[(i-1)%len(pts)]-pts[i];b=pts[(i+1)%len(pts)]-pts[i]
  return np.zeros(2) if np.dot(a/np.linalg.norm(a),b/np.linalg.norm(b))>.62 else (pts[(i+1)%len(pts)]-pts[(i-1)%len(pts)])*.16
 for i,a in enumerate(pts):
  b=pts[(i+1)%len(pts)];c=a+tangent(i);d=b-tangent((i+1)%len(pts))
  for k in range(16):
   t=k/16;out.append(a*(1-t)**3+3*c*(1-t)**2*t+3*d*(1-t)*t*t+b*t**3)
 return out
W,H,SS=2048,512,3
def point(p):return ((p[0]+2.7)/5.4*W*SS,(1-(p[1]-.30)/1.10)*H*SS)
mask=Image.new('L',(W*SS,H*SS));draw=ImageDraw.Draw(mask);draw.polygon([point(p) for p in rounded(poly)],fill=255)
for x,z in [(-1,.96),(-.35,.94),(.30,1.02)]:draw.polygon([point(p) for p in rounded([(x+.11,z-.025),(x,z-.041),(x-.105,z+.027),(x-.025,z+.041)])],fill=255)
alpha=np.asarray(mask.resize((W,H),Image.Resampling.LANCZOS),dtype=float)/255
x=np.linspace(-2.7,2.7,W)[None,:];z=np.linspace(1.4,.3,H)[:,None];t=np.clip(.8*(2.3-x)/4.1+.2*np.clip((z-.45)/.6,0,1),0,1)
a=np.array([.95,.62,.010]);b=np.array([.98,.15,.006]);c=np.array([.65,.018,.006]);u=np.clip((t-.35)/.50,0,1)[...,None];rgb=a*(1-u)+b*u;v=np.clip((t-.85)/.15,0,1)[...,None];rgb=rgb*(1-v)+c*v
# Stored in sRGB; values above were Blender linear colors.
rgb=np.where(rgb<=.0031308,12.92*rgb,1.055*rgb**(1/2.4)-.055);rgba=np.dstack([rgb,alpha]);folder=A/'textures';folder.mkdir(exist_ok=True);Image.fromarray(np.uint8(np.clip(rgba,0,1)*255)).save(folder/'side_flames_rgba.png')
(folder/'side_flames_editable.json').write_text(json.dumps({'coordinates':'x,z; UV U=(x+2.7)/5.4, V=(z-.30)/1.10','outline':poly,'embers':[[-1,.96],[-.35,.94],[.30,1.02]],'source':'Original procedural interpretation of supplied photographs, not a copied reference bitmap.'},indent=2))
print('SIDE_FLAME_TEXTURE_PREPARED')
