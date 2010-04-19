import datetime,sys,os
from PIL import Image
from cStringIO import StringIO
def convertBMP(obj):
    fieldName='thumbnailImage'
    field=obj.getField(fieldName)
    mimetype = field.getContentType(obj)
    
    if  mimetype.lower() not in ['image/x-ms-bmp','application/octet-stream']:
        return
    img = field.getRaw(obj)
    if not img:
                return
    data = str(img.data)
    pathOrg='/tmp/bmpImage'+str(datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
    f = open(pathOrg,'w')
    f.write(data)
    f.close()
    im = Image.open(pathOrg)
    im.save(pathOrg,'JPEG')
    f = open(pathOrg,'r')
    data = f.read()
    f.close()
    field.set(obj,data) 
    obj.reindexObject()
    os.remove(pathOrg)

