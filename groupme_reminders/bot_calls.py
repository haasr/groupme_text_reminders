from tasks import Task, TaskScheduler
from datetime import datetime as dt

import random
import re

# Represents data needed to schedule a single task:
task_data = {
    'title': '',
    'phone_number': '',
    'description': '',
    'start_date': '',
    'task_time': '',
    'notification': ''
}

title_asked = False
notif_asked = False

notif_time = '30 minutes before'
time_pattern = re.compile("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$") # Pattern to validate time strings
notif_pattern = re.compile("[0-9]?[0-9] [a-z*]") # Pattern to validate time strings for notification

task_scheduler = TaskScheduler()

JOKES = [
    ' you were born...',
    '\nQ: What do you call a fish without an eye?\n\nA: A fsh.',
    ' I went to a restaurant on the moon the other day, the food' +
    ' was great but there was just no atmosphere',
    ' two guys walked into a bar, I just walked underneath.',
    ' the 3 unwritten rules of life:\n   1:\n   2:\n   3:',
    ' what do you and a bungalow have in common?\nNothing upstairs!',
    ' my for-loops take longer to end than your relationships',
    ' I\'m an acquired taste. if you don\'t like me, acquire some taste.',
    ' If I had a face like yours, I\'d sue my parents',
]

PROVERBS = [
    'The too-lazy do a few things poorly; the too-busy do many things' +
    ' poorly.',
    'If you store food in your fridge, it may go bad. If you store food in' +
    ' your belly, you don\'t need a fridge.',
    'When you are lacking in motivation, you are lacking in caffeine',
    'Once you exceed your life limit, you cannot upgrade your plan.',
    'Nothing is in control and there\'s nothing you can do about it.',
    'There are 2 types of people: those who can interpret incomplete data' +
    ' sets.',
    '\"Give a man a fish and feed him for a day.\nDon\'t teach a man to fish' +
    ' and feed yourself.\nHe\'s a grown man and fishing\'s not that hard.\" - Ron'
]


def reset_task_data_et_questions():
    global task_data
    global title_asked
    global notif_asked

    task_data = {
        'title': '',
        'phone_number': '',
        'description': '',
        'start_date': '',
        'task_time': '',
        'notification': ''
    }
    title_asked = False
    notif_asked = False


# Ensures task date is not already in past
def validate_date(date):
    dt_date = dt.strptime(date, '%m/%d/%y')
    now = dt.now()
    diff = dt_date - now
    if diff.days < -1: # Return false if date precedes today's date.
        print(diff.days)
        return False
    else:
        return True


# Validates the date format and checks to see whether the date
# is in the past. If validation passed, the task's date is set accordingly.
# Reply string and date_valid bool returned.
def try_set_task_date(date):
    global task_data
    date_valid = False
    try:
        dt.strptime(date, '%m/%d/%y') # Validate date format
        if validate_date(date): # Validate the date isn't already past.
            task_data['start_date'] = date
            reply = 'Task date is set to ' + date
            date_valid = True
        else:
            reply = 'The selected date is already past'
    except:
        # Append current year if not specified:
        try:
            date = date + '/' + str(dt.now().year)[2:]
            dt.strptime(date, '%m/%d/%y') # Validate date format
            if validate_date(date): # Validate the date isn't already past.
                task_data['start_date'] = date
                reply = 'Reminder date is set to ' + date
                date_valid = True
            else:
                reply = 'The selected date is already past'
        except:
            reply = f"Date format is invalid. Use 'MM/DD' or 'MM/DD/YY'"

    return reply, date_valid


# Validates the time format passed by checking it against time_pattern.
# If AM/PM, it converts to 24-hr time. Sets the task's time if validation
# passed. Returns string reply and bool time_valid.
def try_set_task_time(time):
    global task_data
    reply = f"The reminder's time is invalid. Format the time as 'HH:MM' or 'HH:MM pm'"
    time_valid = False

    if 'am' in time:
        time = time.split(' am')[0]
        if re.match(time_pattern, time): # Validate time
            task_data['task_time'] = time
            reply = 'Reminder\'s time is set to ' + time
            time_valid = True

    elif 'pm' in time:
        time = time.split(' pm')[0]
        if re.match(time_pattern, time): # Validate time
            # Convert to 24-hr:
            time_split = time.split(':')
            hour_int = int(time_split[0]) + 12
            task_data['task_time'] = str(hour_int) + ':' + time_split[1]
            reply = 'Reminder\'s time is set to ' + task_data['task_time']
            time_valid = True

    else: # Already in 24-hr time
        if re.match(time_pattern, time):
            task_data['task_time'] = time
            reply = 'Reminder\'s time is set to ' + time
            time_valid = True

    return reply, time_valid


# Attempts to set the notification time of task. If the time
# string matches the pattern, notif_pattern and the time unit
# used (minute, hour, day, etc.) is recognized, the task_data's
# notification value is set to the string.
# Returns string reply and bool time_valid
def try_set_notif_time(time):
    global task_data

    if re.match(notif_pattern, time): # Check that the pattern matches
        if ((' minute' in time) or (' hour' in time) or (' day' in time)
            or (' week' in time)): # check for one of the valid units of time
            task_data['notification'] = time
            reply = 'Notification set for ' + time
            time_valid = True
    elif 'start time' in time:
        task_data['notification'] = time
        reply = 'Notification set for ' + time
        time_valid = True
    else:
        reply = (
            f"The notification duration is invalid. E.g. '45 minutes before', "
            f" '2 days before', or 'at the task's start time'."
        )
        time_valid = False

    return reply, time_valid


# Processes contents of msg and replies with a pertinent repsponse
# such as the next instruction. Uses regex and simple string matching
# to decide what information is being given to parse data into task_data
# and give appropriate response, etc.
def generate_reply(msg):
    global task_data
    global title_asked
    global notif_asked

    # If none of the outermost if/elif cases evaluate to true,
    # this response is given:
    reply = (
        f"I'm here to schedule your reminders."
        f" To schedule a new reminder, just say '"
        f"Schedule reminder'."
        f"\n\n For usage, type '/usage'"
    )

    if msg == '/usage': # Displays usage instructions.
        reply = (
            f"\n                 MQTTasky Usage"
            f"\n==============================="
            f"\n- Initiate a new task: "
            f"\n\t 'Schedule reminder'"
            f"\n\n- Date and time:"
            f"\n\tMQTTTasky will let you know how"
            f"\n\tto enter date or time when prompted."
            f"\n\tIf the year is not provided in a date"
            f"\n\tstring, the current year is assumed."
            f"\n\n\tTime strings ending in AM or PM are"
            f"\n\tautomatically converted into 24-hr"
            f"\n\tformat."
            f"\n\n- Notifications:"
            f"\n\tNotifications are specified by a unit"
            f"\n\tof time before the time of the task."
            f"\n\tYou may use the following units of"
            f"\n\ttime:"
            f"\n\n\tMinutes:"
            f"\n\t\t E.g. '15 minutes before'"
            f"\n\tHours:"
            f"\n\t\t E.g. '15 hours before'"
            f"\n\tDays:"
            f"\n\t\t E.g. '15 days before'"
            f"\n\tWeeks:"
            f"\n\t\t E.g. '15 weeks before'"
            f"\n\n- Reset:"
            f"\n\tIf you want to cancel or restart the"
            f"\n\tcreation of a task, use the command:"
            f"\n\t\t '/reset'"
            f"\n\n- Delete:"
            f"\n\tTo delete all active tasks:"
            f"\n\t\t '/deleteall'"
            f"\n\n- Bonus:"
            f"\n\tAsk bot to tell a joke or proverb."
        )
    elif msg == '/reset': # Clears task_data thereby allowing user to start over with task scheduling.
        reset_task_data_et_questions()
        reply = 'Task data cleared.'
    elif msg == '/deleteall': # Clear the task_list in task_scheduler
        removed = task_scheduler.remove_all()
        if removed:
            reply = 'All scheduled tasks have been deleted.'
        else:
            reply = 'Deletion of scheduled tasks failed. Please try again.'
    elif re.search('<createreminder> .*', msg): # All task data sent from GUI.
        taskdata_str = msg.split('<createreminder> ')[1]
        taskdata = taskdata_str.split('|')
        task_data['title'] = taskdata[0]
        task_data['phone_number'] = taskdata[1]
        task_data['description'] = taskdata[2]
        task_data['start_date'] = taskdata[3]
        task_data['task_time'] = taskdata[4]
        task_data['notification'] = taskdata[5]

        t = Task(
            task_data['title'], task_data['start_date'], task_data['task_time'],
            task_data['notification'], task_data['description'], task_data['phone_number']
        )
        task_scheduler.schedule(t)
        reset_task_data_et_questions() # Reset for next task to be scheduled.
        reply = 'Created and scheduled'

    elif re.search('tell.*joke', msg): # Tell joke from jokes array:
        reply = JOKES[random.randint(0, ( len(JOKES) - 1 ))]
        print(reply)
    elif re.search('tell.*proverb', msg): # Tell proverb from proverbs array:
        reply = PROVERBS[random.randint(0, ( len(PROVERBS) - 1 ))]
    elif re.search('give.*wisdom', msg): # Tell proverb from proverbs array:
        reply = PROVERBS[random.randint(0, ( len(PROVERBS) - 1 ))]

    elif task_data['title'] == '': # If title string empty, check for new task scheduled
        '''
        if re.search('schedule.*task .* with description .*', msg): # Try to parse title and desc to task_data
            split_str = msg.split(' task ')[1]
            split = split_str.split(' with description ')
            task_data['title'] = split[0][0].upper() + split[0][1:] # Capitalize first char
            task_data['description'] = split[1]
            reply = (
                f"On what date will '{ task_data['title'] }' occur?"
                f" Use 'MM/DD' or 'MM/DD/YY'"
            )
        '''
        if re.search('schedule.*reminder', msg): # Prompt for title
            reply = 'What should be the new reminders\'s title?'
            title_asked = True

        elif title_asked: # After title has been given, this response will be parsed as title:
            task_data['title'] = msg[0].upper() + msg[1:]
            reply = f"Enter the recipient phone number for reminder \'{ task_data['title'] }'"

    # Title is already given; check if phone_number needed:
    elif task_data['phone_number'] == '':
        number = msg.replace('-', '') # Strip out the dashes
        if re.match('^[0-9]{10,16}$', number):
            task_data['phone_number'] = number
            reply = (
                f"Phone number {task_data['phone_number']} set."
                f"\nEnter the description for the reminder \'{ task_data['title'] }'"
            )
        else:
            reply = (
                f"Specify phone number as a 9-13 digit number either with or without hyphens."
            )

    # Title is already given; check if description needed:
    elif task_data['description'] == '':
        task_data['description'] = msg[0].upper() + msg[1:]
        # Set description and ask for date
        reply = (
            f"The reminders\'s description is set to '{ task_data['description'] }'"
            f". On what date will the reminder '{ task_data['title'] }' occur?"
            f" Use 'MM/DD' or 'MM/DD/YY'"
        )

    # Title and description given, parse the date for task to start on:
    elif task_data['start_date'] == '':
        reply, date_valid = try_set_task_date(msg)
        reply += f". At what time will the reminder '{ task_data['title'] }' occur?"
        reply += " Use 'HH:mm' or 'HH:mm AM/PM'"

    # Title, description, and date parsed to task_data. Get the time
    # that task occurs at:
    elif task_data['task_time'] == '':
        reply, time_valid = try_set_task_time(msg)
        notif_str = (
            f". You have the default notification time set to { notif_time }" 
            f" before the reminder occurs. Would you like to change it?"
        )
        reply += notif_str

    # Title, description, date, and start_time parsed. Get the notification
    # string indicating when before the task start time a notification should
    # be given:
    elif task_data['notification'] == '':        
        if not notif_asked:
            # if user replied with yes or y, they don't want default notification time
            # of 30 minutes before. let them change it.
            if ('yes' in msg) or (msg == 'y'):
                reply = (
                    f"When should the notification occur? E.g. '45 minutes before' or"
                    f" '2 days before', or 'at the reminder's start time'."
                )
                notif_asked = True
            # Else, event is ready to be scheduled. Send reply re-iterating task data
            # and schedule the task by first creating a task object and then passing
            # it to task_scheduler's schedule function:
            else:
                try_set_notif_time(notif_time)
                if 'start time' in task_data['notification']:
                    reply = (
                        f"\n\nReminder '{ task_data['title'] }' with description '{ task_data['description'] }'"
                        f" is set to occur at { task_data['task_time'] } on { task_data['start_date'] }."
                        f" You have set the notification to occur at the reminder's start time."
                    )
                else:
                    reply = (
                        f"\n\nReminder '{ task_data['title'] }' with description '{ task_data['description'] }'"
                        f" is set to occur at { task_data['task_time'] } on { task_data['start_date'] }."
                        f" You have set the notification to occur { task_data['notification'] }."
                    )
                # Schedule task here
                t = Task(
                    task_data['title'], task_data['start_date'], task_data['task_time'],
                    task_data['notification'], task_data['description']
                )
                task_scheduler.schedule(t)
                reset_task_data_et_questions() # Reset for next task to be scheduled.
                
        else:
            reply, time_valid = try_set_notif_time(msg)
            if time_valid:
                # Time validated; Event is ready to be scheduled. Send reply re-iterating task data
                # and schedule the task by first creating a task object and then passing
                # it to task_scheduler's schedule function:
                if 'start time' in task_data['notification']:
                    reply = (
                        f"\n\nReminder '{ task_data['title'] }' with description '{ task_data['description'] }'"
                        f" is set to occur at { task_data['task_time'] } on { task_data['start_date'] }."
                        f" You have set the notification to occur at the task's start time."
                    )
                else:
                    reply = (
                        f"\n\nReminder '{ task_data['title'] }' with description '{ task_data['description'] }'"
                        f" is set to occur at { task_data['task_time'] } on { task_data['start_date'] }."
                        f" You have set the notification to occur { task_data['notification'] }."
                    )
                # Schedule task here
                t = Task(
                    task_data['title'], task_data['start_date'], task_data['task_time'],
                    task_data['notification'], task_data['description'], task_data['phone_number']
                )
                task_scheduler.schedule(t)
                reset_task_data_et_questions() # Reset for next task to be scheduled.

    return reply
