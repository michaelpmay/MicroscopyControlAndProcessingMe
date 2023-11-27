import unittest
from human_interface import *
answer=True# if this is None, it enables interaction

class TestRequestComponentBox(unittest.TestCase):
    def testDomain(self):
        component = RequestComponentBox(prompt="Type:")
        component.request(answer=answer)

class TestRequestComponentList(unittest.TestCase):
    def testDomain(self):
        component=RequestComponentList(['This','That','Other'],prompt="Pick from list:")
        component.request(answer=answer)

class TestRequestComponentsDict(unittest.TestCase):
    def testDomain(self):
        component=RequestComponentDict({"1":"One","2":"Two"},prompt="Pick from dict:")
        component.request(answer=answer)

class TestRequestComponentsButton(unittest.TestCase):
    def testDomain(self):
        component=RequestComponentButton(['This','That','Other'],prompt="Pick from List:")
        component.request(answer=answer)
