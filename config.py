# coding=utf-8
import json
import logging
import os
import urllib
import sys
import time

# SCRIPTPATH = r'D:\cp'
SCRIPTPATH = os.path.dirname(os.path.realpath(sys.executable))
cfg_file = os.path.join(SCRIPTPATH, 'cfg.json')
install_file = os.path.join(SCRIPTPATH, 'install.json')
if not os.path.exists(cfg_file) or not os.path.exists(install_file):
    logging.error(u"找不到 %s 文件或者 %s 文件！系统退出！"%(cfg_file,install_file))
    time.sleep(3)
    sys.exit(0)
# cfg.json加载
DEBUG = False
try:
    logging.debug(u"开始加载%s配置文件！"%cfg_file)
    with open(cfg_file) as confile:
        config = json.load(confile)
    HOSTNAME = config.get('hostname')
    DEBUG = config.get('debug')
    IP = config.get('ip')
    HEARTBEAT = config.get('heartbeat')
    TRANSFER = config.get('transfer')
    HTTP = config.get('http')
    COLLECTOR = config.get('collector')
    IGNORE = config.get('ignore')
    VERSION = config.get('version')
    PLUGIN = os.path.join(SCRIPTPATH, 'plugin')
except Exception as e:
    l = logging.getLogger('root.errcfg')
    l.error(e)


def loadINSTALL():
    '''
    加载 install.json文件，方便后期修改下载更新地址。
    :return:
    '''
    # install.json加载
    try:
        logging.debug(u"开始加载%s配置文件！" % install_file)
        with open(install_file) as infile:
            ifile = json.load(infile)
        return dict(GETIP=ifile.get('GetIP'), ZKAPI=ifile.get('ZkAPI'), PACKAGE=ifile.get('Package'),
                    PACKAGEMD5=ifile.get('Package_md5'), INSTALLPATH=ifile.get('Install_Path'),
                    DOWNLOADPATH=ifile.get('Download_Path'))
    except Exception as e:
        l = logging.getLogger('root.errcfg')
        l.error(e)


##日志配置
LOGNAME = 'app.log'
leve = logging.DEBUG if DEBUG else logging.INFO
conf_log = logging.getLogger('root.config')
conf_log.propagate = False
log_fmt = logging.Formatter('[%(asctime)s]:[%(name)s]:[%(levelname)s]:%(message)s')

log_File = logging.FileHandler(filename=LOGNAME, encoding='utf-8')
log_File.setLevel(leve)
log_File.setFormatter(log_fmt)

# console = logging.StreamHandler(stream=sys.stdout)
# console.setLevel(leve)
# console.setFormatter(log_fmt)
# conf_log.addHandler(console)


class urlopener(object):
    '''
    统一url的访问以及关闭。
    '''
    def __init__(self, url):
        self.url = url

    def __enter__(self):
        self.connect = urllib.urlopen(self.url)
        return self.connect

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connect.close()


def coding():
    '''
    终端字符乱码问题解决函数
    :return:
    '''
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf8')
        conf_log.debug(u'当前终端字符集: %s' % sys.getdefaultencoding())
