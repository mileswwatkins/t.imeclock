import unittest
import os
import sys
sys.path.append(os.path.join('..', 'src'))
from functions import User, Project

class UserTests(unittest.TestCase):

    def setUp(self):
        self.Miles = User(username="Miles", first_proj="ELE")
        
    def test_naming_of_user(self):
        self.assertEqual(self.Miles.username, "Miles")

    def test_