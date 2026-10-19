from PIL import Image
from pathlib import Path
p=Path(__file__).parent/'dist'/'assets'
def crop(src,name,box):
    im=Image.open(p/src); im.crop(box).save(p/(name+'.jpg'),quality=92)
crop('gallery-a.jpg','pink',(0,188,186,433))
crop('gallery-a.jpg','french',(377,188,560,433))
crop('gallery-a.jpg','detail',(189,690,373,932))
crop('gallery-a.jpg','studio',(189,941,374,1184))
crop('gallery-b.jpg','blue',(0,443,186,684))
crop('gallery-b.jpg','red',(190,443,373,684))
crop('gallery-b.jpg','chrome',(377,188,560,433))
crop('gallery-b.jpg','piercing',(377,944,560,1186))
crop('gallery-c.jpg','green',(0,225,185,425))
crop('gallery-c.jpg','art',(190,225,374,425))
crop('tattoo.jpg','ink',(25,370,490,820))
