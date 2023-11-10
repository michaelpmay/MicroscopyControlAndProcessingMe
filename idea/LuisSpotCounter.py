class iImageCalculator:
    def process(self,image,**kwargs):
        '''will do image processing and resutn some type of data'''
        pass

class SpotCounter(iImageCalculator):
    def process(self,image, threshhold=50,sigma=30):
        '''implements spot counting usin g coinvolutions'''
        pass


class SpotCounterSupportObject(...):
    pass

class SpotCounterLuis(iImageCalculator):
    def __init__(self):
        self.support=SpotCounterSupportObject()
    def process(self,image,**kwargs):
        '''Luis Version somethisg complicated'''
        pass



image=np.array(512,512)
imageCalculator=SpotCounterLuis()
dats=imageCalculator.process(image,**kwargs)