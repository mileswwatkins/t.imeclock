from datetime import datetime

class User(object):
    def __init__(self, user_name):
        self.user_name = user_name
        self.proj_list = []

    def switch_proj(self, proj_name, switch_time):
        """End the previous project, then start timing new project"""
        switch_datetime = datetime.strptime(switch_time, "%H:%M")

        for proj in self.proj_list:
            if proj.end_time != None:
                proj.end(end_time=switch_datetime)
                break

        proj_already_used = any(proj.proj_name == proj_name for
                proj in self.proj_list)
        
        if not proj_already_used:
            new_proj = Project(proj_name)
            new_proj.start(start_time=switch_datetime)
            self.proj_list.append(new_proj)
        
        elif proj_already_used:
            for proj in self.proj_list:
                if proj.proj_name == proj_name:
                    proj.start(start_time=switch_datetime)
                    break


class Project(object):
    def __init__(self, proj_name):
        self.proj_name = proj_name
        self.start_time = None
        self.end_time = None
        self.total_time = 0.

    def start(self, start_time):
        pass

    def end(self, end_time):
        pass

    def add_to_total(self, start_time, end_time):
        pass