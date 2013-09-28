from datetime import datetime, time, timedelta
from pprint import pprint
from copy import deepcopy

def calc_time_spent(start, end):
    """Calculate the number of hours between two datetime objects."""
    time_diff = round((end - start).seconds / 60. / 60., 1)
    return timediff


def print_sheet (begin_time, current_proj, time_dict):
    """Prettily print the current timesheet to the terminal."""
    # Perform a deepcopy() in order to remove all links to the original object
    temp_time_dict = deepcopy(time_dict)

    time_spent = calc_time_spent(begin_time, datetime.now())
    # Add time spent on current project to earlier time spent on that
    # project, if applicable
    if temp_time_dict.has_key(current_proj):
        temp_time_dict[current_proj] = temp_time_dict[current_proj] + time_spent
    else:
        temp_time_dict[current_proj] = time_spent

    # If it appears that more than 20 hours has been spent on the
    # current project, then throw it out
    if temp_time_dict[current_proj] > 20:
        del temp_time_dict[current_proj]
    
    pprint(temp_time_dict, width=5)


def new_entry (begin_time, current_proj, time_dict, recent_projs):
    """Ask user about starting work on a new project, and add the
    now-completed project to the database.
    """
    # Create a list of possible new projects for the user to select from
    temp_recent_projs = recent_projs[:]
    temp_recent_projs.append("Project not listed here")
    temp_recent_projs.append("Take a break from work")

    # Ask user what they want to work on next
    print "\nWhat project are you starting to work on now? (Enter number)"
    for num, val in enumerate(temp_recent_projs):
        print "{0}) {1}".format()
    
    # If the user is starting on a new project, ask for its name
    new_proj = temp_recent_projs[int(raw_input()) - 1]
    if new_proj == "Project not listed here":
        new_proj = raw_input("\nWhat is the name of the new project? ")
        recent_projs.append(new_proj)

    # If the user is taking a break, then add its time to a special category
    if new_proj == "Take a break from work":
        new_proj = 'Break'
    
    # Ask user when they are starting on the new project
    new_time = int(raw_input("\nHow many minutes from now are you starting it? "))
    end_time = datetime.now() + timedelta(minutes = new_time)

    # Find out how much time the user spent on the project they are finishing
    time_spent = calc_time_spent(begin_time, end_time)
    
    # Add the finished project to the timesheet
    if time_dict.has_key(current_proj):
        time_dict[current_proj] = time_dict[current_proj] + time_spent
    else:
        time_dict[current_proj] = time_spent
    
    return (end_time, new_proj, time_dict, recent_projs)


def endofday (begin_time, current_proj, time_dict):
    """Provides final print of timesheet at the end of a day"""
    # Ask the user when their day ends
    finish_time = datetime.strptime(raw_input("\nWhat time are you going to leave? "), "%H:%M")

    # Calculate how much time the user spent on the final project
    time_spent = calc_time_spent(begin_time, finish_time)

    # Add the final project to the timesheet
    if time_dict.has_key(current_proj):
        time_dict[current_proj] = time_dict[current_proj] + time_spent
    else:
        time_dict[current_proj] = time_spent
    
    # Remove break time from the printout
    # try:
    #   del(time_dict['Break'])
    
    # Print out their timesheet
    print "\n Here's your timesheet!\n"
    pprint(time_dict, width = 5)
    print "\nHave a nice night!\n"

    # Kill the program
    return True


print "\nGood morning!"
begin_time = datetime.strptime(raw_input("\nWhat time did you come in today? "), "%H:%M")
current_proj = raw_input("\nWhat project did you work on first? ")

# Initialize user attributes
time_dict = {}
recent_projs = [current_proj]

# Keep the program running until the user leaves for the day
isitover = False
while isitover == False:
    whichfunction = raw_input("""
What would you like to do? (Enter number)
1) Start work on a new project
2) Print current timesheet
3) Leave for the day
""")
    if whichfunction == '1':
        begin_time, current_proj, time_dict, recent_projs = new_entry(begin_time, current_proj, time_dict, recent_projs)
    elif whichfunction == '2':
        printsheet(begin_time, current_proj, time_dict)
    elif whichfunction == '3':
        isitover = endofday(begin_time, current_proj, time_dict)
