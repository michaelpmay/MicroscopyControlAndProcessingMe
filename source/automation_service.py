# START
from fastapi import FastAPI
from pydantic import BaseModel
from source.environment import *
app = FastAPI()
verbosity=Verbosity()

builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
builder.setRootDataPath('') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('default','')
env.loadConfiguration(configFileName='myConfig.cfg')
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()
env.backend.connectDevices()
automationService=env.backend

class Images(BaseModel):
  pixels: list
  dimensions: list

@app.get("/listAcquisitionHistory")
def listAcquisitionHistory():
  history=automationService.listAcquisitionHistory()
  return history

@app.get("/listAvailableAcquisitions")
def listAvailableAcquisitions():
  list =automationService.listAvailableAcquisitions()
  return list

@app.get("/listStagedAcquisitions")
def listStagedAcquisitions():
  list=automationService.listStagedAcquisitions()
  return list

@app.get("/listCompletedAcqusititions")
def listCompletedAcqusititions():
  list=automationService.listCompletedAcqusititions()
  return list

@app.get("/listFailedAcquisitions")
def listFailedAcquisitions():
  list=automationService.listFailedAcquisitions()
  return list

@app.post("/stageAcquisition")
def stageAcquisition(name:str):
  automationService.stageAcquisition(name)
  return 1

@app.post("/tryCompleteAllStagedAcquisitions")
def tryCompleteAllStagedAcquisitions(name:str):
  automationService.tryCompleteAllStagedAcquisitions(name)
  return 1


@app.get("/loadImageData(")
def loadImageData(name: str) -> list:
  print(name)
  automationService.setUser('default', '')
  data=automationService.loadImageData(name)
  return data.tolist()

@app.get("/listImageData")
def listImageData()->list:
  list=automationService.listImageData()
  return list


@app.get("/listDeviceHardware")
def listDeviceHardware()->list:
  return automationService.listDeviceHardware()