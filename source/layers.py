import os
import pickle
class AnalysisLayer:
    def runAndSave(self, key):
        if not isinstance(key, str):
            raise TypeError
        command = 'self.' + key + '()'
        data = eval(command)
        path = os.path.join('data', 'analysis', key + '.pkl')
        with open(path,'wb') as f:
            pickle.dump(data,f)

class AxesLayer:
    pass

class FigureLayer:
    def runAndSave(self, key):
        if not isinstance(key, str):
            raise TypeError
        command = 'self.' + key + '()'
        fig = eval(command)
        path = os.path.join('data', 'figures', key + '.eps')
        fig.savefig(path, format='eps')