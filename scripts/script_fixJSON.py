import json
import cv2
import numpy as np
f=open('/Users/mpmay/Downloads/MASKSET1.json')
data = json.load(f)
uniqueImages={1,2,3}
for i in data['metadata']:
    linearpath=np.round(np.array(data['metadata'][i]['xy'][1:])).astype('int32')
    splitstring=i.split('_')
    index=str(splitstring[0]).zfill(4)
    uniqueImages.add(int(index))
    mask=np.zeros([512,512,3]).astype('uint8')
    path=[]
    for i in range(0,len(linearpath),2):
        path.append([linearpath[i],linearpath[i+1]])
    path=np.array(path).astype('int32')
    cv2.polylines(mask,np.int32([path]),True,(0,255,255))
    winname = 'example'
    cv2.namedWindow(winname)
    cv2.imshow(winname, mask)
    cv2.waitKey()
    cv2.destroyWindow(winname)
    print(len(uniqueImages))