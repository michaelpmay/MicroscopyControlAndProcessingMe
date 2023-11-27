import dataclasses
import json

from fastapi import FastAPI
from pydantic import BaseModel,Field
from image_process import CellDetectorCellMask,CellDetectorCellCount
import numpy as np
app=FastAPI()

@app.post("/process")
def process()->None:
    pass