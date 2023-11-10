class ReportFull:
    formatStrings=[]
    args=[]
    def __int__(self):
        self.formatStrings=[]
        self.args=[]
    def add(self,formatString,*args):
        if not isinstance(formatString,str):
            raise TypeError
        self.formatStrings.append(formatString)
        self.args.append([*args])
    def print(self):
        for i in range(len(self.formatStrings)):
            args=self.args[i]
            print(self.formatStrings[i].format(*args))
        self.formatStrings=[]
        self.args=[]

class ReportSilent:
    def add(self,formatString,*args):
        # do nothing on purpose
        pass

    def print(self):
        # do nothing on purpose
        pass

    def clear(self):
        # no nothing on purpose
        pass

class ReportLog:
    logFileName=None
    formatStrings=[]
    args=[]
    def __init__(self,*args):
        if len(args) > 1:
            raise ValueError
        if len(args)==1:
            self.logFileName=args[0]
    def setLogFile(self,fileName):
        if not isinstance(fileName,str):
            raise TypeError
        self.logFileName=fileName
    def add(self,formatString,*args):
        if not isinstance(formatString,str):
            raise TypeError
        formatString.format(*args)   #check that it works
        self.formatStrings.append(formatString)
        self.args.append([*args])

    def print(self):
        file=open(self.logFileName,"a")
        for i in range(len(self.formatStrings)):
            args = self.args[i]
            file.write(self.formatStrings[i].format(*args))
        file.close()

class Verbosity:
    log=ReportLog("report.log")
    mode=ReportSilent()
    def add(self,formatString,*args):
        self.log.add(formatString,*args)
        self.mode.add(formatString,*args)
    def print(self):
       self.log.print()
       self.mode.print()

    def clear(self):
        self.mode.clear()
        # never clear log file