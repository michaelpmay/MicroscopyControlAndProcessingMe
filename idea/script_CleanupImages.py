from PIL import Image,ImageSequence
import matplotlib as plt
import numpy as np

tiffStack=Image.open('/Volumes/mpmay/MachineLearningDatasets/1296CellImages/coredata/Full resolution/36PowGrid_NDTiffStack.tif')
index=0
for i,page in enumerate(ImageSequence.Iterator(tiffStack)):
    loopIndex=i%3
    print(np.max(page))
    if loopIndex==0:
        print('1')
        rgbImage=np.zeros([512,512,3],dtype='uint8')
        rgbImage[:,:,0]=(np.array(page)/65535*255)
    elif loopIndex==1:
        print('2')
        rgbImage[:,:,1] = (np.array(page)/65535*255).astype('uint8')
    elif loopIndex==2:
        print('3')
        rgbImage[:,:,2] = (np.array(page)/65535*255).astype('uint8')
        rgbPilImage=Image.fromarray(rgbImage,mode='RGB')
        fileName='image_'+str(index).zfill(4)+'.jpg'
        path= 'data/users/mpmay/acquisition/1296Images/images/'
        rgbPilImage.save(path+fileName, quality=100)
        index = index + 1