from postprocessors import *
from decision import *
data=NDTiffDataset('data/core/xyLooseGrid_5')
acq=AcquisitionPlugin()
processor=PostProcessPipeline()
processor.add('sharpest',squish_axes='z')
processedData=processor.process(data,acq)
decision=DecisionSelectOptimalZPlaneFromSharpestZ()
new_acq=decision.propose(processedData,acq)