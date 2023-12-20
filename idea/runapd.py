from apd import *
acqLibrary=AcquisitionPluginLibrary()
acquisition=acqLibrary.xySequence([[0,0],[0,0]])

process=PostProcessPipeline()
process.add('mean')
process.add('null')
process.add('mask')
process.add('cellCount')
process.add('spotCount')

decision=DecisionRepeatAcquisition()

apdSystem = APDSystem(configFileName='myConfig.cfg', rootDataFolder='')
apdSystem.linkAPD(acquisition,process,DecisionRepeatAcquisition())
apdSystem.run()