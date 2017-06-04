import json
import logging
import os
import sys

SCRIPTPATH = r'D:\FalconAgent'
# SCRIPTPATH = os.path.dirname(os.path.realpath(sys.executable))
cfg_file = os.path.join(SCRIPTPATH, 'cfg.json')
logging.debug(cfg_file)
config = None
try:
    with open(cfg_file) as confile:
        config = json.load(confile)
except Exception as e:
    l = logging.getLogger('root.config2')
    l.error(e)

HOSTNAME = config.get('hostname')
DEBUG = config.get('debug')
IP = config.get('ip')
HEARTBEAT = config.get('heartbeat')
TRANSFER = config.get('transfer')
HTTP = config.get('http')
COLLECTOR = config.get('collector')
IGNORE = config.get('ignore')
VERSION = config.get('version')
INSTALL = config.get('InstallPath')
PLUGIN = os.path.join(SCRIPTPATH, 'plugin')

##日志配置
LOGNAME = 'app.log'
leve = logging.DEBUG if DEBUG else logging.INFO
conf_log = logging.getLogger('root.config')
conf_log.propagate = False
log_fmt = logging.Formatter('[%(asctime)s]:[%(name)s]:[%(levelname)s]:%(message)s')

log_File = logging.FileHandler(filename=LOGNAME, encoding='utf-8')
log_File.setLevel(leve)
log_File.setFormatter(log_fmt)

console = logging.StreamHandler(stream=sys.stdout)
console.setLevel(leve)
console.setFormatter(log_fmt)

conf_log.addHandler(console)

