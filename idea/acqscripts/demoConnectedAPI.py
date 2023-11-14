from api import *
api=ConnectedAPIFacade()
api.connectAutomationService('localhost', 8000)
api.connectProcessingService('localhost', 8001)
api.connectDecisionService('localhost', 8002)

request = AcquisitionRequest()
request.name = "test_API"

api.post_acquisition_and_acquire(request)