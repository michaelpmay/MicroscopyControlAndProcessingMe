import requests
import json

class AcquisitionRequest:
    def __init__(self):
        self.name=None

class ServiceClient:
    def __init__(self):
        self.host=None
        self.port=None
        self.comm="http"
    def setHostPort(self,host,port):
        self.host=host
        self.port=port
    def get(self,command,**kwargs):
        command=self.comm+"://"+self.host+":"+str(self.port)+'/'+command
        response=requests.get(command,**kwargs)
        return response.content

    def post(self,command,**kwargs):
        command=self.comm+"://"+self.host+":"+str(self.port)+'/'+command
        response=requests.post(command,**kwargs)
        return response.content

class ProcessingService():
    def __init__(self):
        self.channels=[0,0]
        self.client=ServiceClient()

    def setHostPort(self,host,port):
        self.client.setHostPort(host,port)

    def get(self,command,**kwargs):
        return self.client.get(command,**kwargs)

    def post(self,command,**kwargs):
        return self.client.post(command,**kwargs)

    def process(self,key,request):
        response=self.post(key, json=request)
        return response

class AutomationService():
    def __init__(self):
        self.client=ServiceClient()

    def setHostPort(self, host, port):
        self.client.setHostPort(host, port)

    def get(self, command, **kwargs):
        return self.client.get(command, **kwargs)

    def post(self, command, **kwargs):
        return self.client.post(command, **kwargs)

    def post_acquisition_and_acquire(self,acquisition):
        if not isinstance(acquisition,AcquisitionRequest):
            raise TypeError
        self.get('post_acquisition_and_acquire',params=acquisition)

    def get_image_data(self,key):
        if not isinstance(key,str):
            raise TypeError
        response=self.get('get_image_data',params={"name":key})
        return json.loads(response)

    def list_image_data(self):
        response=self.get('list_image_data')
        return response

    def get_acquisitions_avaiable_list(self):
        response=self.get('get_acquisitions_avaiable_list')
        return response

    def get_scheduled_acquisition_list(self):
        response = self.get('get_scheduled_acquisition_list')
        return response

    def get_completed_acquisition_list(self):
        response = self.get('get_completed_acquisition_list')
        return response

    def get_failed_acquisition_list(self):
        response = self.get('get_failed_acquisition_list')
        return response

    def get_acquisition_history(self):
        response = self.get('get_acquisition_history')
        return response


class DecisionService:
    def __init__(self):
        self.client = ServiceClient()

    def setHostPort(self, host, port):
        self.client.setHostPort(host, port)

    def get(self, command, **kwargs):
        return self.client.get(command, **kwargs)

    def post(self, command, **kwargs):
        return self.client.post(command, **kwargs)

class ConnectedAPIFacade:
    def __init__(self):
        self.automationService = AutomationService()
        self.processingService = ProcessingService()
        self.decisionService = DecisionService()
        

    def connectAutomationService(self,host,port):
        self.automationService.setHostPort(host,port)

    def connectProcessingService(self,host,port):
        self.processingService.setHostPort(host,port)

    def connectDecisionService(self,host,port):
        self.processingService.setHostPort(host,port)

    def process(self,key,image):
        return self.processingService.process(key,image)

    def list_image_data(self):
        self.automationService.list_image_data()

    def post_acquisition_and_acquire(self,acquisition):
        self.automationService.post_acquisition_and_acquire(acquisition)

    def get_image_data(self,key):
        return self.automationService.get_image_data(key)

    def get_acquisitions_avaiable_list(self):
        return self.automationService.get_acquisitions_avaiable_list()

    def get_scheduled_acquisition_list(self):
        return self.automationService.get_scheduled_acquisition_list()

    def get_completed_acquisition_list(self):
        return self.automationService.get_completed_acquisition_list()

    def get_failed_acquisition_list(self):
        return self.automationService.get_failed_acquisition_list()

    def get_acquisition_history(self):
        return self.automationService.get_acquisition_history()
