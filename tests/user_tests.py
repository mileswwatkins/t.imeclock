import unittest
from datetime import datetime

from functions import User, Project


class UserTests(unittest.TestCase):
    def setUp(self):
        self.example_user = User(user_name="Miles")
        
    def test_naming_of_user(self):
        self.assertEqual(self.example_user.user_name, "Miles")

    def test_creating_first_project(self):
        self.example_user.switch_proj("PfP", "2:33")
        self.assertEqual(self.example_user.proj_list[0].proj_name, "PfP")

    def test_switching_projects(self):
        self.example_user.switch_proj("PfP", "2:33")
        self.example_user.switch_proj("TQD", "3:40")
        self.assertEqual(self.example_user.proj_list[1].proj_name, "TQD")
