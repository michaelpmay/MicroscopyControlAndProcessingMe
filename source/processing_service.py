import dataclasses
import json

from fastapi import FastAPI
from pydantic import BaseModel,Field
from image_process import CellDetectorCellMask,CellDetectorCellCount
import numpy as np
app=FastAPI()

class ProcessRequest(BaseModel):
    name:str='null'
    image:list=[]

@app.post("/process")
def process(request:ProcessRequest)->list:
    npImage=np.array(request.image)

    if len(npImage.shape)<3:
        npImage=np.array([npImage,npImage,npImage])
    if request.name=='null':
        response=request.image
    if request.name=='mask':
        detector=CellDetectorCellMask()
        mask=detector.process(npImage)
        response=mask
    if request.name=='count':
        detector = CellDetectorCellCount()
        count = detector.process(npImage)
        response = count
    return response
