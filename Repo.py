# coding:utf8
import logging
from config import HOSTNAME, IP, VERSION, log_File, base_leve
from JsonClient import UpdateReport

repo_log = logging.getLogger(u'Repo客户端')
repo_log.setLevel(base_leve)
repo_log.propagate = False
repo_log.addHandler(log_File)


# repo_log.addHandler(console)


def report():
    data = dict(Hostname=HOSTNAME, IP=IP, AgentVersion=str(VERSION), PluginVersion='enable')
    try:
        UpdateReport(data)
    except Exception as err:
        repo_log.error(err)
