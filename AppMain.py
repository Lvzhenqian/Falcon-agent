# coding=utf-8
import logging
import os
import sys

import AutoInstall
import crond
from config import log_File, base_leve, coding, HTTP

main_log = logging.getLogger(u'主进程')
main_log.setLevel(base_leve)
main_log.addHandler(log_File)
# main_log.addHandler(console)
main_log.debug('console coding is: %s' % sys.getdefaultencoding())
coding()


def service():
    '''
    服务进程！开启前台服务作业！
    :return:
    '''
    if HTTP.get('enabled'):
        main_log.debug(u'开启API服务!')
        crond.APIthread()
    main_log.debug(u'开始作业：%s' % (crond.Jobs.get_jobs()))
    try:
        crond.Jobs.start()
    except (KeyboardInterrupt, SystemExit):
        crond.Jobs.shutdown()
        main_log.debug(u'主进程退出！')


def main():
    '''
    主进程，判断是否需要安装或者直接启动前台服务作业。
    :return:
    '''
    m = AutoInstall.Upgrade()
    if not os.path.exists(m.Install_Path) or os.path.exists(m.AgentMd5):
        main_log.debug(u"检查到目录或者MD5文件不存在，开始安装程序！")
        m.Download_And_Install(m.Remote_Md5())
    else:
        main_log.debug(u"程序已存在开启后台进程服务！")
        service()


if __name__ == '__main__':
    # service()
    main()
