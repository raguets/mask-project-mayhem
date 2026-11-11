import bpy,json
r=bpy.data.objects['HondoMacLean_Rig'];suit=bpy.data.objects['HMC_ContinuousFlightSuit'];out={}
for z in [.36,.40,.44,.48,.54,.60,.66,.70,.74,.78]:
    vs=[v.co for v in suit.data.vertices if abs(v.co.z-z)<.002 and v.co.y>0 and v.co.y<.23]
    out[z]={'xrange':[min(v.x for v in vs),max(v.x for v in vs)],'yrange':[min(v.y for v in vs),max(v.y for v in vs)]} if vs else None
print(json.dumps(out))
