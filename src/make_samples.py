# Builds synthetic sample photos with hand-written EXIF (GPS, time, device) for the Breadcrumbs demo.
from PIL import Image, ImageDraw, ImageFont
import random, base64, io, json, struct, sys, os
os.chdir(sys.argv[1])

def ascii_(s): return s.encode()+b"\0"
def build_exif(make, model, ts, latlon):
    # entries: (tag, type, count, valuebytes)  types: 2 ASCII, 4 LONG, 5 RATIONAL, 1 BYTE
    def rat(vals): return b"".join(struct.pack("<II",n,d) for n,d in vals)
    def dms(x):
        x=abs(x); d=int(x); m=int((x-d)*60); s=((x-d)*60-m)*60
        return [(d,1),(m,1),(int(round(s*10000)),10000)]
    ifds=[]
    ifd0=[(0x010F,2,ascii_(make)),(0x0110,2,ascii_(model)),(0x0132,2,ascii_(ts)),(0x8769,4,None)]
    if latlon: ifd0.append((0x8825,4,None))
    exif=[(0x9003,2,ascii_(ts))]
    gps=None
    if latlon:
        lat,lon=latlon
        gps=[(0x0000,1,bytes([2,3,0,0])),(0x0001,2,ascii_("N" if lat>=0 else "S")),(0x0002,5,rat(dms(lat))),(0x0003,2,ascii_("E" if lon>=0 else "W")),(0x0004,5,rat(dms(lon)))]
    order=[ifd0,exif]+([gps] if gps else [])
    # layout: header(8) then ifds sequentially, each followed by its data area
    sizes=[]
    def ifd_size(ents): 
        data=sum(len(v) for _,_,v in ents if v is not None and len(v)>4)
        return 2+12*len(ents)+4+data
    offs=[]; o=8
    for ents in order: offs.append(o); o+=ifd_size(ents)
    ptr={0x8769:offs[1]}; 
    if gps: ptr[0x8825]=offs[2]
    blob=bytearray(b"II*\0"+struct.pack("<I",8))
    for ents,off in zip(order,offs):
        ents=sorted(ents,key=lambda e:e[0])
        dataoff=off+2+12*len(ents)+4; body=bytearray(struct.pack("<H",len(ents))); data=bytearray()
        for tag,typ,val in ents:
            if val is None: val=struct.pack("<I",ptr[tag])
            unit={1:1,2:1,4:4,5:8}[typ]; count=len(val)//unit
            if len(val)<=4: body+=struct.pack("<HHI",tag,typ,count)+val.ljust(4,b"\0")
            else: body+=struct.pack("<HHII",tag,typ,count,dataoff+len(data)); data+=val
        body+=struct.pack("<I",0); blob+=body+data
    return b"Exif\0\0"+bytes(blob)

HOME=(40.78120,-73.96650); WORK=(40.75320,-73.98220)
shots=[
 ("dog_morning.jpg","Dog on the couch",HOME,(0.00008,-0.00005),"2026:10:03 07:12:44",(240,200,150)),
 ("dinner.jpg","Homemade dinner",HOME,(-0.00006,0.00004),"2026:10:05 20:41:09",(200,120,80)),
 ("new_shoes.jpg","New shoes",HOME,(0.00003,0.00009),"2026:10:11 22:03:51",(90,110,160)),
 ("balcony_sunset.jpg","Sunset from the balcony",HOME,(-0.00004,-0.00007),"2026:10:18 18:55:30",(250,140,90)),
 ("study_group.jpg","Study group",WORK,(0.00005,0.00002),"2026:10:14 10:22:17",(120,170,140)),
 ("coffee.jpg","Coffee before class",WORK,(-0.00003,0.00006),"2026:10:21 09:05:02",(150,110,90)),
 ("meme.jpg","Screenshot (no location)",None,None,"2026:10:22 13:30:00",(130,130,200)),
]
out=[]
for i,(fn,cap,base,jit,ts,col) in enumerate(shots):
    W,H=480,320; im=Image.new("RGB",(W,H),col); d=ImageDraw.Draw(im); random.seed(i)
    for y in range(H):
        f=0.7+0.45*y/H; d.line([(0,y),(W,y)],fill=tuple(min(255,int(c*f)) for c in col))
    for _ in range(9):
        x,y,r=random.randint(0,W),random.randint(80,H),random.randint(14,60)
        d.ellipse([x-r,y-r,x+r,y+r],fill=tuple(max(0,min(255,c+random.randint(-70,40))) for c in col))
    d.rectangle([0,H-44,W,H],fill=(20,20,20))
    try: fnt=ImageFont.truetype("arial.ttf",22)
    except Exception: fnt=None
    d.text((14,H-36),"Sample: "+cap,fill=(255,255,255),font=fnt)
    ll=(base[0]+jit[0],base[1]+jit[1]) if base else None
    b=io.BytesIO(); im.save(b,"JPEG",quality=62,exif=build_exif("Google","Pixel 8",ts,ll)); data=b.getvalue()
    open(fn,"wb").write(data)
    chk=Image.open(io.BytesIO(data)).getexif(); gps=chk.get_ifd(0x8825)
    print(fn,len(data),dict(gps) if gps else 'no gps',chk.get_ifd(0x8769).get(0x9003),chk.get(0x0110))
    out.append({"name":fn,"data":"data:image/jpeg;base64,"+base64.b64encode(data).decode()})
json.dump(out,open("samples.json","w"))
