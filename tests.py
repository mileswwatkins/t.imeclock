from models import User, Project
import unittest
from datetime import datetime


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.only_initialized = Project(proj_name="ELE")

        self.only_started = Project(proj_name="TQD")
        self.only_started.start_time = datetime.strptime("13:20", "%H:%M")

        self.started_and_ended = Project(proj_name="RUR")
        self.started_and_ended.start_time = datetime.strptime("17:35", "%H:%M")
        self.started_and_ended.end_time = datetime.strptime("18:20", "%H:%M")

    def test_project_names_work(self):
        self.assertEqual(self.only_initialized.proj_name, "ELE")

    def test_only_initialized_has_no_start_time(self):
        self.assertEqual(self.only_initialized.start_time, None)

    def test_only_started_has_no_end_time(self):
        self.assertEqual(self.only_started.end_time, None)

    def test_only_started_has_start_time(self):
        start_datetime = datetime.strptime("13:20", "%H:%M")
        self.assertEqual(self.only_started.start_time, start_datetime)

    def test_add_time_to_total_calculation(self):
        self.started_and_ended.add_time_to_total()
        self.assertEqual(self.started_and_ended.total_time, 45)

    def test_start_time_cleared_after_add_time_to_total(self):
        self.started_and_ended.add_time_to_total()
        self.assertEqual(self.started_and_ended.start_time, None)

    def test_one(self):
        self.assertEqual(1, 1)


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


if __name__ == '__main__':
    unittest.main()
