import gpio_status_light_util as status_light
from datetime import datetime as dt, timedelta
from threading import Thread
from time import sleep

import requests
import os

MESSAGE_ENCODING = 'utf-8'
textbelt_url = ''

def set_textbelt_url(url):
    global textbelt_url
    textbelt_url = url

# The task object represents a task and is used as an arg
# to TaskWindow to display it graphically.
class Task:
    def __init__(self, title, start_date, task_time,
                    notif_time, description, phone_number=None):
        self.title        = title
        self.start_date   = start_date
        self.task_time    = task_time
        self.description  = description
        self.phone_number = phone_number

        task_dt = dt.strptime((start_date + ' ' + task_time)
                                , '%m/%d/%y %H:%M')

        # The below code takes a time like '30 minutes before'
        # and creates a datetime object that would actually
        # represent that amount of time before the task's start
        # date and time.
        #
        # If format invalid or not recognized, set notification
        # time to equal task time (notification will be given
        # when the task is set to start).
        if ' minute' in notif_time:
            try:
                delta = notif_time.split(' minute')[0]
                notif_time_dt = task_dt - timedelta(minutes=int(delta))
                self.notif_time = notif_time_dt
            except:
                self.notif_time = task_dt
        elif ' hour' in notif_time:
            try:
                delta = notif_time.split( 'hour')[0]
                notif_time_dt = task_dt - timedelta(hours=int(delta))
                self.notif_time = notif_time_dt
            except:
                self.notif_time = task_dt
        elif ' day' in notif_time:
            try:
                delta = notif_time.split(' day')[0]
                notif_time_dt = task_dt - timedelta(days=int(delta))
                self.notif_time = notif_time_dt
            except:
                self.notif_time = task_dt
        elif ' week' in notif_time:
            try:
                delta = notif_time.split(' week')[0]
                notif_time_dt = task_dt - timedelta(weeks=int(delta))
                self.notif_time = notif_time_dt
            except:
                self.notif_time = task_dt
        else:
            self.notif_time = task_dt


    # This function is used to generate a string to be read by
    # text-to-speech engine simple_google_tts
    def tts(self):
        return (
            f"{ self.title } starts on { self.start_date }"
            f" at { self.task_time }.\n\n"
            f" { self.description }"
        )


    def __str__(self):
        if len(self.description) > 60:
            desc = '{}'.format(self.description[:60]) # Truncate to 60 chars.
        else:
            desc = self.description
        return (
            f"Title:        { self.title }"
            f"\nStart Date:  { self.start_date }"
            f"\nTask Time:   { self.task_time }"
            f"\nNotif. Time: { self.notif_time }"
            f"\nDescription: { desc }"
        )


# Singleton class -- learned from https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
class TaskScheduler:
    class __TaskScheduler:
        def __init__(self):
            self.task_list = []
            self.iterable_task_list = []
            t = Thread(target=self.manage_notifications)
            t.start()


        def schedule(self, task):
            self.task_list.append(task)
            print(task.notif_time)


        def remove(self, task):
            self.task_list.remove(task)


        def remove_all(self):
            try: # May fail if it is being iterated over.
                self.task_list.clear()
                return True
            except:
                sleep(.2)
                try:
                    self.task_list.clear()
                    return True
                except:
                    return False


        def pub_notification(self, task_str, phone_number):
            Thread(target=status_light.blink_notification).start() # Blink lights in sequence.
            try:
                # Set body params
                params = { 'number': phone_number, 'message': task_str }
                # POST
                resp = requests.post(textbelt_url, params)
                if not resp.status_code == 200:
                    print(resp.reason)
                    Thread(target=status_light.blink_unsuccessful_send).start()
            except Exception as e:
                print(e)
                Thread(target=status_light.blink_unsuccessful_send).start()
                pass


        # Call on simple_google_tts to read the task aloud:
        def read_task(self, task_str):
            os.system('simple_google_tts -p en ' + '\"' + task_str + '\"')


        # This function will iterate over each task in list and compare
        # its notification time to the current time. When they match,
        # it broadcasts a notification to pub/tasks, reads the message
        # aloud using simple_google_tts, displays it graphically and
        # deletes the Task object.
        def manage_notifications(self):
            while True:
                for t in self.task_list:
                    self.iterable_task_list.append(t)

                now = dt.now().replace(second=0, microsecond=0)
                for t in self.iterable_task_list:
                    if t.notif_time == now:
                        pub_thread = Thread(target=self.pub_notification, args=(t.tts(), t.phone_number))
                        #tts_thread = Thread(target=self.read_task, args=(t.tts(),))

                        pub_thread.start() # Encrypt and publish to pub/tasks
                        #tts_thread.start() # Read aloud over using simple_google_tts

                        self.task_list.remove(t)

                self.iterable_task_list.clear()
                sleep(13)

    instance = None


    def __new__(cls):
        if not TaskScheduler.instance:
            TaskScheduler.instance = TaskScheduler.__TaskScheduler()
        return TaskScheduler.instance


    def __getattr__(self, name):
        return getattr(self.instance, name)


    def __setattr__(self, name):
        return setattr(self.instance, name)
