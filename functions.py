from datetime import datetime


class User(object):
    def __init__(self, user_name):
        self.user_name = user_name # could be simply name, we know we're talking about a user already
        self.proj_list = [] # could be just projects, no need to indicate it's a list as that implementation could change

    def switch_proj(self, proj_name, switch_time):
        """End the previous project, then start timing new project"""
        switch_datetime = datetime.strptime(switch_time, "%H:%M")

        for proj in self.proj_list:
            if proj.end_time != None:
                proj.end_time = switch_datetime
                break

        proj_already_used = any(proj.proj_name == proj_name for
                proj in self.proj_list)
        
        if not proj_already_used:
            new_proj = Project(proj_name)
            new_proj.start_time = switch_datetime
            self.proj_list.append(new_proj)
        
        elif proj_already_used:
            for proj in self.proj_list:
                if proj.proj_name == proj_name:
                    proj.start_time = switch_datetime
                    break


class Project(object):
    def __init__(self, proj_name):
        self.proj_name = proj_name # call it simply name
        self.start_time = None # start might be passed to the constructor
        self.end_time = None
        self.total_time = 0

    # maybe just add_time
    def add_time_to_total(self):
        """Calculate time (in minutes) between start_time and end_time,
        and add that to the total_time. Reset start_time and end_time
        to None.
        """
        time_diff = self.end_time - self.start_time
        time_diff_mins = time_diff.seconds / 60
        self.total_time = self.total_time + time_diff_mins

        self.start_time = None
        self.end_time = None
