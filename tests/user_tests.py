import unittest
import os
import sys
from datetime import datetime

sys.path.append(os.path.join('..', 'src'))
from functions import User, Project


class UserTests(unittest.TestCase):
    def setUp(self):
        self.example_user = User(user_name="Miles")
        
    def test_naming_of_user(self):
        self.assertEqual(self.example_user.user_name, "Miles")

    def test_creating_first_project(self):
        another_instance = User(user_name="Some other guy")
        another_instance.switch_proj("PfP", "2:33")
        self.assertEqual(another_instance.proj_list[0].proj_name, "PfP")

    def test_switching_projects(self):
        another_instance = User(user_name="Some other guy")
        another_instance.switch_proj("PfP", "2:33")
        another_instance.switch_proj("TQD", "3:40")
        self.assertEqual(another_instance.proj_list[1].proj_name, "TQD")


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.only_initialized = Project(proj_name="ELE")

        self.only_started = Project(proj_name="TQD")
        self.only_started.start(start_time=
                datetime.strptime("13:20", "%H:%M"))

        self.started_and_ended = Project(proj_name="RUR")
        self.started_and_ended.start(start_time=
                datetime.strptime("17:35", "%H:%M"))
        self.started_and_ended.end(end_time=
                datetime.strptime("18:20", "%H:%M"))

    def test_project_names_work(self):
        self.assertEqual(self.only_initialized.proj_name, "ELE")

    def test_only_initialized_has_no_start_time(self):
        self.assertEqual(self.only_initialized.start_time, None)

    def test_only_started_has_no_end_time(self):
        self.assertEqual(self.only_started.end_time, None)

    def test_only_started_has_start_time(self):
        start_datetime = datetime.strptime("13:20", "%H:%M")
        self.assertEqual(self.only_started.start_time, start_datetime)