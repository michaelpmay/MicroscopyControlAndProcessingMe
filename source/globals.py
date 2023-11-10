import os
class Globals(object):
    BLUE_CHANNEL=0
    GREEN_CHANNEL=1
    RED_CHANNEL=2

    RED_STRING="Red"
    GREEN_STRING="Green"
    BLUE_STRING="Blue"

    ROOT_PATH = ""
    ROOT_DATA_PATH=""
    DATA_FOLDER = "data"
    DATA_USER_FOLDER='users'
    DATA_CORE_FOLDER='core'
    DATA_TEST_FOLDER = 'test'
    DATA_STAGED_FOLDER='staged'
    DATA_COMPLETED_FOLDER='completed'
    DATA_SCRIPTS_FOLDER='scripts'
    DATA_ACQUISITION_FOLDER='acquisition'
    DATA_ERROR_FOLDER = 'error'
    DATA_OUTPUT_FOLDER='output'

    FILENAME_REPORT='report.log'

    LOG_HISTORY='history.log'
    ACQUISITION_HISTORY='acquisitoin_history.log'

    DATA_CORE_PATH = os.path.join(ROOT_PATH, DATA_FOLDER, DATA_CORE_FOLDER)
    DATA_USER_PATH = os.path.join(ROOT_DATA_PATH,DATA_FOLDER,DATA_USER_FOLDER)
    DATA_SCRIPTS_PATH = os.path.join(ROOT_DATA_PATH,DATA_FOLDER, DATA_USER_FOLDER,DATA_SCRIPTS_FOLDER)
    DATA_STAGED_PATH = os.path.join(ROOT_DATA_PATH,DATA_FOLDER, DATA_USER_FOLDER,DATA_STAGED_FOLDER)
    DATA_COMPLETED_PATH = os.path.join(ROOT_DATA_PATH,DATA_FOLDER, DATA_USER_FOLDER,DATA_COMPLETED_FOLDER)
    DATA_ACQUISITION_PATH = os.path.join(ROOT_DATA_PATH,DATA_FOLDER, DATA_USER_FOLDER,DATA_ACQUISITION_FOLDER)
    DATA_ERROR_PATH = os.path.join(ROOT_DATA_PATH,DATA_FOLDER, DATA_USER_FOLDER, DATA_ERROR_FOLDER)
    DATA_OUTPUT_PATH = os.path.join(ROOT_DATA_PATH, DATA_FOLDER, DATA_USER_FOLDER, DATA_OUTPUT_FOLDER)

    DATAKEY_USERDATA='User'
    DATAKEY_COREDATA='Core'
    DATAKEY_STAGED='Staged'
    DATAKEY_ACQUISITIONDATA = 'Acqusition'
    DATAKEY_COMPLETED = 'Completed'
    DATAKEY_SCRIPTS='Scripts'
    DATAKEY_ERROR='Error'
    DATAKEY_OUTPUT='Output'

    currentEvent=[]

    PASS_LOCAL_FILE="authentication.csv"
    NAMES_LOCAL_FILE="users.csv"

    COORDINATES_PIXEL='Pixel'
    COORDINATES_GALVO='Galvo'
    COORDINATES_STAGE='Stage'
    COORDINATES_VIEW='View'

    KEY_DEVICE_CAMERAS= 'Camera'
    KEY_DEVICE_LASERS = 'Laser'
    KEY_DEVICE_FILTERS = 'Filter'
    KEY_DEVICE_STAGES = 'Stage'
    KEY_DEVICE_ZSTAGES = 'ZStage'
    KEY_DEVICE_GALVOS = 'Galvo'
    KEY_DEVICE_PIEZOSTAGE = 'PiezoStage'
    KEY_DEVICE_STATES='StateDevice'
    KEY_DEVICES=[KEY_DEVICE_CAMERAS,KEY_DEVICE_LASERS,KEY_DEVICE_FILTERS,KEY_DEVICE_STAGES,KEY_DEVICE_ZSTAGES,
                 KEY_DEVICE_GALVOS,KEY_DEVICE_PIEZOSTAGE,KEY_DEVICE_STATES]


    PIXEL_CALIBRATION=dict()

    CHANNEL_KEYS={}

    def __new__(cls,configFile='config.txt'):
        it_id = "__it__"
        it = cls.__dict__.get(it_id, None)
        if it is not None:
            return it
        it = object.__new__(cls)
        setattr(cls, it_id, it)
        it.init(configFile)
        return it

    def init(globals,configFile='config.txt'):
        """MUST KEEP THIS AS globals AND NOT self!! IMPORTANT FOR EVAL OF config.txt VALUES"""
        with open(configFile, 'r') as file:
            line='x' #initialize line as a sample string just to get into loop. when file.readline()=None loop stops
            while line:
                line=file.readline()
                if line[0:7]=="globals":
                    exec(line)

    def configureUser(self,user):
        '''Overwrites default setttings with a user setting'''
        self.DATA_USER_PATH=os.path.join(self.ROOT_DATA_PATH,self.DATA_FOLDER,self.DATA_USER_FOLDER,user)
        self.DATA_STAGED_PATH = os.path.join(self.ROOT_DATA_PATH,self.DATA_FOLDER, self.DATA_USER_FOLDER, user,self. DATA_STAGED_FOLDER)
        self.DATA_COMPLETED_PATH = os.path.join(self.ROOT_DATA_PATH,self.DATA_FOLDER, self.DATA_USER_FOLDER, user,self. DATA_COMPLETED_FOLDER)
        self.DATA_SCRIPTS_PATH = os.path.join(self.ROOT_DATA_PATH,self.DATA_FOLDER, self.DATA_USER_FOLDER, user,self.DATA_SCRIPTS_FOLDER)
        self.DATA_ACQUISITION_PATH = os.path.join(self.ROOT_DATA_PATH,self.DATA_FOLDER, self.DATA_USER_FOLDER, user,self.DATA_ACQUISITION_FOLDER)
        self.DATA_ERROR_PATH = os.path.join(self.ROOT_DATA_PATH,self.DATA_FOLDER, self.DATA_USER_FOLDER, user,self.DATA_ERROR_FOLDER)
        self.DATA_OUTPUT_PATH = os.path.join(self.ROOT_DATA_PATH, self.DATA_FOLDER, self.DATA_USER_FOLDER, user,self.DATA_OUTPUT_FOLDER)