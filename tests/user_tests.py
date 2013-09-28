import unittest
import os
import sys
sys.path.append(os.path.join('..', 'src'))
from functions import User

class UserTests(unittest.TestCase):

    def setUp(self):
        self.Miles = User(username="Miles")
        
    def test_naming_of_user(self):
        self.assertEqual(self.Miles.username, "Miles")

    def test_open_project_indicator(self):
        self.Miles.new_proj(proj_name="ELE")
        self.assertEqual(self.Miles.open_proj, "ELE")