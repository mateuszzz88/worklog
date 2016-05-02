#!/usr/bin/env python
import datetime
import os
import subprocess

LOG_FILE = os.path.expanduser('~/hours_log.txt')


cmd = subprocess.Popen(["dbus-monitor \"type='signal',interface='org.freedesktop.ScreenSaver',path='/ScreenSaver'\""],
                       shell=True,
                       stdout=subprocess.PIPE)

last_lock = last_unlock = datetime.datetime.now()

with open(LOG_FILE, 'a') as f:
    f.write("\nlogger started on %s\n" % last_unlock.ctime())

comment = None


def timedelta_format(delta):
    seconds = delta.total_seconds()
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return '%d:%02d:%02d' % (hours, minutes, seconds)

while True:
    line = cmd.stdout.readline().decode('utf-8')
    if "member=ActiveChanged" in line and 'org.freedesktop.ScreenSaver' in line:
        line = cmd.stdout.readline().decode('utf-8')

        when = datetime.datetime.now()
        when_str = when.strftime("%Y-%m-%d %H:%M:%S")

        status = 'UNLOCK' if 'false' in line else 'LOCKED'

        comment = None
        if status == 'UNLOCK':
            # screen unlocked
            last_unlock = when
            diff = when - last_lock
            comment = " (locked for h:m:s = %s)" % timedelta_format(diff)
        else:
            # screen locked
            last_lock = when
            diff = when - last_unlock
            comment = " (unlocked for h:m:s = %s)" % timedelta_format(diff)

        longpause = diff > datetime.timedelta(0, 30 * 60, 0)
        if longpause and status == 'UNLOCK':
            with open(LOG_FILE, 'a') as f:
                f.write('\n')
            comment += " !!!"

        new_log = "{time} screen {status}{comment}\n".format(
            time=when_str,
            status=status,
            comment=comment
        )
        print(new_log)
        with open(LOG_FILE, 'a') as f:
            f.write(new_log)
