class iForm:
    '''A class for displaying interfaces for requesting data'''
    def view(self):
        '''Displays the form and waits for a response. Returns the response.'''
        pass

class iHumanInterfaceFactory:
    '''i class for requesting specific forms'''
    def menu(self):
        pass
    def menuLogin(self):
        pass
    def menuNewUser(self):
        pass
    def menuSelection(self):
        pass
    def menuEditSettings(self):
        pass
    def menuEditDeviceSettings(self):
        pass
    def menuEditAcquisitionSettings(self):
        pass
    def menuEditDataManagerProperties(self):
        pass


class HumanInterfaceFactoryGui(iHumanInterfaceFactory):
    def menuLogin(self):
        # todo
        pass

    def menuEditSettings(self):
        # todo
        pass

    def menuEditDeviceSettings(self):
        # todo
        pass

    def menuEditAcquisitionSettings(self):
        # todo
        pass

    def menuEditDataManagerProperties(self):
        # todo
        pass


class iRequestComponents:
    '''functional units for headless interfaces'''
    def request(self):
        '''displays and asks user input'''
        pass

class iDisplayComponents:
    '''functional units for displaying information'''
    def display(self):
        pass

class RequestComponentBox(iRequestComponents):
    prompt=None
    def __init__(self,prompt=None):
        if prompt:
            if not isinstance(prompt,str):
                raise TypeError
        self.prompt=prompt
    def request(self,answer=None):
        if answer:
            return answer
        else:
            return input(self.prompt)
class RequestComponentList(iRequestComponents):
    prompt = None
    items = None

    def __init__(self, items, prompt=None):
        if prompt:
            if not isinstance(prompt, str):
                raise TypeError
        if not isinstance(items,list):
            raise TypeError
        self.prompt = prompt
        self.items = items
    def request(self,answer=None):
        if answer:
            return answer
        print("\n"+self.prompt)
        for i in range(len(self.items)):
            print("{0} : {1}".format(i+1,self.items[i]))
        while 1:
            response=input("\n")
            try:
                index=int(response)
            except:
                print("\nIndex not found. Try again")
                continue
            if (index < (len(self.items)+1)) & (index>=1):
                return index
            else:
                print("\nIndex not found. Try again")

class RequestComponentButton(iRequestComponents):
    prompt = None
    items = None

    def __init__(self, items, prompt=None):
        if prompt:
            if not isinstance(prompt, str):
                raise TypeError
        if not isinstance(items, list):
            raise TypeError
        self.prompt = prompt
        self.items = items

    def request(self, answer=None):
        if answer:
            return answer
        selection=[False]*len(self.items)
        logoMap=['_',"X"] # maps True False to "X" and "_"
        while 1:
            print("\n"+self.prompt)
            for i in range(len(self.items)):
                print("{2}.[{0}] : {1}".format(logoMap[selection[i]], self.items[i],i+1))
            response=input("\n")
            if response=="":
                break
            if int(response)>len(self.items):
                raise KeyError
            index=int(response)-1
            selection[index]=(selection[index]==False) #this operation always FLIPS the boolean
            return selection


class RequestComponentDict(iRequestComponents):
    prompt = None
    items = None
    def __init__(self, items, prompt=None):
        if prompt:
            if not isinstance(prompt, str):
                raise TypeError
        if not isinstance(items,dict):
            raise TypeError
        self.prompt = prompt
        self.items = items
    def request(self,answer=None):
        if answer:
            return answer
        print("\n" + self.prompt)
        for key in self.items.keys():
            print("{0} : {1}".format(key,self.items[key]))
        while 1:
            key=input("\n")
            if key in self.items.keys():
                return key
            else:
                print("\nKey not found. Try again.")

class DisplayComponentList(iDisplayComponents):
    prompt = None
    items = None

    def __init__(self, items, prompt=None):
        if prompt:
            if not isinstance(prompt, str):
                raise TypeError
        if not isinstance(items, list):
            raise TypeError
        self.prompt = prompt
        self.items = items

    def display(self):
        print("\n" + self.prompt)
        for i in range(len(self.items)):
            print("{0} : {1}".format(i + 1, self.items[i]))

class DisplayComponentDict(iDisplayComponents):
    prompt = None
    items = None

    def __init__(self, items, prompt=None):
        if prompt:
            if not isinstance(prompt, str):
                raise TypeError
        if not isinstance(items, dict):
            raise TypeError
        self.prompt = prompt
        self.items = items

    def display(self):
        print("\n" + self.prompt)
        for key in self.items.keys():
            print("{0} : {1}".format(key, self.items[key]))


class HumanInterfaceFactoryHeadless(iHumanInterfaceFactory):
    def menu(self):
        component = RequestComponentList(['Login', 'New User','Quit'],prompt='Welcome')
        response = component.request()
        return response

    def menuLogin(self):
        component = RequestComponentBox('Username:')
        username = component.request()
        component = RequestComponentBox('Password:')
        password = component.request()
        return (username,password)

    def menuNewUser(self):
        print("Type in a username and password")
        component = RequestComponentBox('Username:')
        username = component.request()
        component = RequestComponentBox('Password:')
        password = component.request()
        return (username, password)

    def menuSelection(self):
        options=['Edit Hardware Properties',
                 'Edit Acquisition Events',
                 'Edit Acquisition Hooks',
                 'Edit Acquisition Settings',
                 'Load Acquisition',
                 'Save Acquisition',
                 'Stage Acquisition',
                 'Begin Acquisition',
                 'Begin Acquisition Loop Staged Acquisitions',
                 'Quit']
        component=RequestComponentList(options,prompt="Select an option:")
        response=component.request()
        return response

    def menuEditSettings(self,settings):
        component=RequestComponentDict(settings,prompt="Choose a setting:")
        keySetting=component.request()
        component=RequestComponentBox(prompt="Pick a new value for "+keySetting)
        valueSetting=component.request()
        return (keySetting,valueSetting)

    def menuEditHardwareSettings(self):
        options = ['List Devices Available',
                   'List Device Interfaces',
                   'List Device Hardware',
                   'Add Device',
                   'Remove Device (Not Working Yet)',
                   'Back']
        component=RequestComponentList(options,prompt="Pick a setting:")
        response=component.request()
        return int(response)

    def menuListDevices(self,deviceNames):
        component = RequestComponentList(deviceNames, prompt="Pick a setting:")
        response = component.request()
        return response

    def menuEditAcquisitionSettings(self,settings):
        component = RequestComponentList(settings, prompt="Pick a setting:")
        response = component.request()
        key=settings[int(response)]
        component = RequestComponentBox(prompt="Pick a new Value")
        response=component.request()
        value=eval(response)
        return (key,value)

    def menuEditSystemProperties(self):
        # todo
        pass

    def menuLoadFromFile(self):
        # todo
        pass

    def menuListDevicesAvailable(self,devices):
        component = DisplayComponentDict(devices, prompt="List of Devices Drivers Avaiable")
        response=component.display()
        return response

    def menuListDeviceInterfaces(self,interfaces):
        component = DisplayComponentList(interfaces, prompt="List of Device Interfaces")
        response = component.display()
        return response
    def menuListDeviceHardware(self,hardware):
        component = RequestComponentList(hardware, prompt="List of Current Device Hardware")
        response = component.request()
        return response
    def menuAddDevice(self,hardware,ports):
        component = RequestComponentDict(hardware, prompt="Select a device")
        deviceSelectionKey= component.request()
        deviceName=deviceSelectionKey
        component=RequestComponentList(ports,prompt="Select an available port:")
        portSelectionIndex=int(component.request())-1
        portName=ports[portSelectionIndex][0] #0 always the name property
        return (deviceName,portName)

    def menuSaveAcquisitionSettings(self):
        component=RequestComponentBox(prompt="Filename:")
        response=component.request()
        return response

    def menuLoadAcquisition(self,names):
        component=RequestComponentList(names,prompt="Pick an Acquisition from Library or Folder:")
        response=component.request()
        return response

    def menuSaveAcquisition(self):
        component=RequestComponentBox(prompt="Acquisition Save name:")
        response=component.request()
        return response

    def menuStageAcquisition(self,acquisitions):
        component=RequestComponentList(acquisitions,prompt="Pick an Acquisition to schedule:")
        response=component.request()
        return acquisitions[response-1]

    def menuLoadConfiguration(self,availableConfigurations):
        component=RequestComponentList(availableConfigurations,prompt="Pick a config")
        response=component.request()
        return availableConfigurations[response-1]

    def menuLoginFailed(self):
        print("Credientials invalid")
    def menuMoveFailedAcqusition(self,name):
        print("Error Acquisition {0} Failed ".format(name))

    def menuCompleteStagedAcquisition(self,name):
        print("Acquisition {0} Completed Successfully".format(name))

    def menuAcquisitionLoopReminder(self):
        component=RequestComponentBox(prompt="REMINDER: PLEASE OPEN MICROMANAGER BEFORE CONTINUING.\nPRESS ANY KEY TO CONTINUE")
        response=component.request()
        return response
class HumanInterfaceAbstractFactory:
    '''A factory that makes factories for in'''
    def GuiInterface(self):
        return HumanInterfaceFactoryGui()
    def HeadlessInterface(self):
        return HumanInterfaceFactoryHeadless()

