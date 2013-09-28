from datetime import datetime

class User(object):
    def __init__(self, username):
        self.username = username
        self.proj_dict = {}
        self.proj_list = []
        self.open_proj = None

    def new_proj(self, proj_name):
        self.open_proj = proj_name


class Project(object):
    def __init__(self, proj_name):
        self.proj_name = proj_name
        self.start_time = None
        self.end_time = None
        self.total_time = 0.

    def start_proj(self):
        pass

    def end_proj(self):
        pass