import unittest
from authentication import *
from globals import *
class testUser(unittest.TestCase):
    def testUser(self):
        user = User("mpmay")
        pass
    def testUser_int_returnsTypeError(self):
        self.assertRaises(TypeError,User,(1))
    def testUser_list_returnsTypeError(self):
        self.assertRaises(TypeError,User,([]))
    def testUser_tuple_returnsTypeError(self):
        self.assertRaises(TypeError,User,(()))


class TestValidationNoPassword(unittest.TestCase):
    def setUp(self) -> None:
        self.object=ValidatorNoPassword()

    def testDomain(self):
        key=self.object.makeKey('default', '')
        self.object.validate('default', '')
        self.object.newUser('default', '')
        self.object.removeUser('default', '')
        self.object.newUser('default', '')

class TestValidationLocal(unittest.TestCase):
    def testDomain(self):
        validator = ValidatorLocal('authentication.csv','users.csv')
        validator.newUser('test0','')
        validator.newUser('test1', '')
        validator.newUser('test2', '')
        self.assertIn('test0',validator.listUsers())
        self.assertIn('test1', validator.listUsers())
        self.assertIn('test2', validator.listUsers())
        validator.removeUser('test0', '')
        validator.removeUser('test1', '')
        validator.removeUser('test2', '')
        self.assertRaises(PermissionError,validator.validate,'test0','')
        self.assertRaises(PermissionError, validator.validate, 'test1', '')
        self.assertRaises(PermissionError, validator.validate, 'test2', '')

class TestAuthentication(unittest.TestCase):
    def testDomain(self):
        pass
