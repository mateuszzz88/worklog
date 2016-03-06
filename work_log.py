#!/usr/bin/env python
import datetime
import os
import subprocess

LOG_FILE = os.path.expanduser('~/hours_log.csv')


cmd = subprocess.Popen(["dbus-monitor \"type='signal',interface='org.freedesktop.ScreenSaver',path='/ScreenSaver'\""],
                       shell=True,
                       stdout=subprocess.PIPE)

last_lock = last_unlock = when = datetime.datetime.now()

with open(LOG_FILE, 'a') as f:
    f.write("\nlogger started on %s\n" % when.ctime())

comment = None

while True:
    line = cmd.stdout.readline().decode('utf-8')
    if "member=ActiveChanged" in line and 'org.freedesktop.ScreenSaver' in line:
        line = cmd.stdout.readline().decode('utf-8')

        when = datetime.datetime.now()
        when_str = when.strftime("%Y-%m-%d %H:%M:%S")

        status = 'UNLOCK' if 'false' in line else 'LOCKED'
        longpause = comment and diff > datetime.timedelta(0, 30 * 60, 0)
        if longpause:
            with open(LOG_FILE, 'a') as f:
                f.write('\n')

        comment = None
        if 'false' in line:
            # screen unlocked
            last_unlock = when
            if last_lock:
                diff = when - last_lock
                comment = " (locked for h:m:s = %s)" % str(diff)
        else:
            # screen locked
            last_lock = when
            if last_unlock:
                diff = when - last_lock
                comment = " (unlocked for h:m:s = %s)" % str(diff)
        if longpause:
            comment += " !!!"
        new_log = "{time} screen {status}{comment}\n".format(
            time=when_str,
            status=status,
            comment=comment
        )
        print(new_log)
        with open(LOG_FILE, 'a') as f:
            f.write(new_log)


