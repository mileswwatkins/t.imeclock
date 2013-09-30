import unittest
import os
import sys
from datetime import datetime

sys.path.append(os.path.join('..', 'src'))
from functions import User, Project


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
