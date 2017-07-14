import logging
from config import HOSTNAME, IP, VERSION, log_File, leve
from HbsClient import Update

repo_log = logging.getLogger('root.Repo')
repo_log.setLevel(leve)
repo_log.propagate = False
repo_log.addHandler(log_File)
# repo_log.addHandler(console)


def report():
    data = dict(Hostname=HOSTNAME, IP=IP, AgentVersion=str(VERSION), PluginVersion='enable')
    try:
        Update(data)
    except Exception as err:
        repo_log.error(err)
