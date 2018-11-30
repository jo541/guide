import os
from subprocess import call

# installation des packages avec pip
call(["pip", "install", "-r", "%s/requirements.txt" % os.getcwd()])

from crontab import CronTab

# Gestion des crons
cron = CronTab(user=True)
list_of_job = [job for job in cron.find_comment("KodiGuidCron")]
# Verification des crons deja existant
if not list_of_job:
    job1 = cron.new(command='%s/venv/bin/python %s/script.py' % (os.getcwd(), os.getcwd()), comment="KodiGuidCron")
    job1.day.every(1)
    job1.hour.also.on(2)
    cron.write()

# Lancement pour la premier fois
call(["python", "script.py"])