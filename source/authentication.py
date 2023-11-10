import csv
import hashlib
class User:
    name=None
    settings=None
    def __init__(self,name=None):
        if not isinstance(name,str):
            raise TypeError
        self.name=name
        self.settings=dict()

    def getUserName(self):
        return self.name

class iValidator:
    def validate(self,user,password):
        """Validate a users credentials"""
        pass
    def makeKey(self,user,password):
        '''make a unique id from a hashed user and password'''
        pass
    def newUser(self,user,password):
        '''make a new user'''
        pass

class iAuthentication:
    '''talks to data store to verify credentitals, then load user data. user data overwrites variables in global'''
    def validate(self):
        """see if the user-password combo is good"""
        pass

    def isValidated(self):
        """see if user is validated"""
        pass

    def addUser(self,user):
        """adds new user to the list"""
        pass

    def getUser(self):
        """return the current users name"""
        pass

    def setUser(self,user):
        """Sets the current user"""
        pass


class Authentication(iAuthentication):
    validator=None
    user=None
    _isValidated = None
    def __init__(self):
        self.validator=iValidator()
        self._isValidated = False

    def setUser(self,user):
        if not isinstance(user,(User,str)):
            return TypeError
        if isinstance(user,str):
            user=User(user)
        self._isValidated = False
        self.user=user

    @property
    def isValidated(self):
        return self._isValidated

    @property
    def username(self):
        return self.user.name

    def validate(self,name,password):
        self._isValidated=self.validator.validate(name,password)

    def getUser(self):
        return self.user

    def newUser(self,name,password):
        self.validator.newUser(name,password)

    def listUsers(self):
        return self.validator.listUsers()



class ValidatorLocal(iValidator):
    passfile=None
    userfile=None
    def __init__(self,passfile,userfile):
        self.passfile=passfile
        self.userfile=userfile
        self._hashkey='7xEi64yI8hhVCJCK'

    def validate(self,name,password):
        if not isinstance(name,str):
            return TypeError
        if not isinstance(password,str):
            return TypeError
        key=self.makeKey(name,password)
        with open(self.passfile) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row[0]==key:
                    return True
        raise PermissionError("Credentials Invalid")

    def makeKey(self,name,password):
        if not isinstance(name,str):
            return TypeError
        if not isinstance(password,str):
            return TypeError
        key='n'+name+'p'+password+self._hashkey
        byteKey=key.encode('utf-8')
        return hashlib.sha256(byteKey).hexdigest()

    def newUser(self,name,password):
        if not isinstance(name,str):
            return TypeError
        if not isinstance(password,str):
            return TypeError
        key=self.makeKey(name, password)
        with open(self.userfile) as csv_file:
            csv_reader = csv.reader(csv_file)
            isInDatabase=False
            for row in csv_reader:
                if row==[name]:
                    isInDatabase=True
        if not isInDatabase:
            with open(self.passfile,'a',newline='') as csv_file:
                writer=csv.writer(csv_file)
                writer.writerow([self.makeKey(name,password)])
            with open(self.userfile,'a',newline='') as csv_file:
                writer=csv.writer(csv_file)
                writer.writerow([name])
        else:
            raise PermissionError('Username is taken')

    def removeUser(self,name,password):
        self.validate(name,password)
        key=self.makeKey(name,password)
        allKeys=[]
        with open(self.passfile) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row[0] !=key:
                    allKeys.append(row[0])
        with open(self.passfile, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
        with open(self.passfile,'a',newline='') as csv_file:
            writer = csv.writer(csv_file)
            for i in range(len(allKeys)):
                writer.writerow([allKeys[i]])
        allNames=[]
        with open(self.userfile) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row[0] !=name:
                    allNames.append(row[0])
        with open(self.userfile, 'w', newline='') as csv_file:
            pass
        with open(self.userfile,'a',newline='') as csv_file:
            writer = csv.writer(csv_file)
            for i in range(len(allNames)):
                writer.writerow([allNames[i]])
        pass

    def listUsers(self):
        users=[]
        with open(self.userfile) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if len(row)>0:
                    users.append(row[0])
        return users

class ValidatorNoPassword(iValidator):
    def validate(self,user,password):
        return True
    def makeKey(self,user,password):
        pass
    def newUser(self,user,password):
        pass
    def removeUser(self,user,password):
        pass