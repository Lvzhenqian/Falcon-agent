# coding:utf-8
import json
import logging
import os
import socket
import time
import urllib
import urllib2
import win32service
import win32serviceutil
from hashlib import md5 as md5sum
from platform import machine
from shutil import move, rmtree
from zipfile import ZipFile

from config import leve, urlopener, log_File, loadINSTALL

cfg = loadINSTALL()
install_log = logging.getLogger('root.install')
install_log.setLevel(leve)
install_log.addHandler(log_File)


# install_log.addHandler(console)


class Upgrade(object):
    '''
    安装升级类，用于自动更新或者第一次安装。
    '''
    Install_Path = cfg.get('INSTALLPATH')

    def __init__(self):
        self.__ip = cfg.get('GETIP')
        self.__zk_ip = cfg.get('ZKAPI')
        self.__Agent = cfg.get('PACKAGE')
        self.AgentMd5 = cfg.get('PACKAGEMD5')
        self.Download_Path = cfg.get('DOWNLOADPATH')
        self.Package_name = self.__Agent.rsplit('/', 1)[1]
        self.__Download_File = os.path.join(self.Download_Path, 'agent.zip')
        self.__Backup_Path = self.Install_Path + '_%s' % time.strftime('%Y-%m-%d')

    def __ChangeFile(self, ip, x):
        '''
        读取配置文件并修改hostname
        :param ip: 要修改的hostname
        :param x: 要修改的配置文件路径
        :return: 修改成功，Tr
        '''
        try:
            with open(x, mode='rt') as r:
                dit = r.read()
            fdit = json.loads(dit)
            fdit['hostname'] = ip
            install_log.debug(u'更改 hostname=%s ' % ip)
            wf = os.path.join(self.Download_Path, r'agent\cfg.json')
            install_log.debug('write to source file!')
            with open(wf, mode='wt') as w:
                wbody = json.dumps(fdit)
                w.write(wbody)
            install_log.debug(u'更改cfg.json文件成功.')
            return True
        except IOError:
            install_log.error(u'找不到cfg.json文件!')
            return False

    def __SelectIp(self):
        '''
        对比中控，ip.7road.net选择出正确的IP地址，以及要修改的json文件
        :return: 返回(ip,json文件路径)元组
        '''
        install_log.debug(u'选择IP 与 cfg.json文件')
        try:
            with urlopener(self.__ip) as op:
                internet = op.read().split()
            net, we = internet[0].decode(), internet[1]
            parms = {
                'ips': net,
                'props': 'ip1'
            }
            url = urllib.urlencode(parms)
            with urlopener(self.__zk_ip + '?' + url) as oo:
                req = oo.read().decode()
            resp = json.loads(req)
            if resp['code'] == 0:
                zk_res, status = resp['data'][0][net]['ip1'], resp['code']
                if we == '中国'.encode():
                    return zk_res, os.path.join(self.Download_Path, 'agent\cfg.json')
                else:
                    return zk_res, os.path.join(self.Download_Path, 'agent\hwcfg.json')
            else:
                return net, os.path.join(self.Download_Path, 'agent\cfg.json')
        except urllib2.HTTPError:
            hsn = socket.gethostname()
            return socket.gethostbyname(hsn), os.path.join(self.Download_Path, 'agent\cfg.json')

    def Download_And_Install(self, s_md5):
        '''主进程。下载安装包，并安装。'''
        try:
            if not os.path.isdir(self.Download_Path):
                os.mkdir(self.Download_Path)
            install_log.debug(u'下载更新包！')
            with urlopener(self.__Agent) as ag:
                agent = ag.read()
            with open(self.__Download_File, 'wb') as f:
                f.write(agent)
            install_log.debug(u"比对下载包的Md5值。")
            with open(self.__Download_File, 'rb') as ff:
                down_md5 = md5sum(ff.read())
            if s_md5 == down_md5.hexdigest():
                install_log.debug(u'开始安装更新！')
                self.__Install(self.__Download_File, self.Download_Path)
                install_log.debug(u'下载Md5.txt文件')
                urllib.urlretrieve(self.AgentMd5, os.path.join(self.Install_Path, 'md5.txt'))
                install_log.debug(u'清理临时目录！')
                rmtree(self.Download_Path)
                return install_log.debug(u'安装 更新包完成！')
            else:
                return install_log.warning(u'下载出错！请手动下载更新包，地址：%s' % self.__Agent)

        except urllib2.HTTPError:
            return install_log.error(u"无法下载，请检查网络！地址：%s" % self.__Agent)

    def __AddService(self):
        '''
        添加程序进系统服务，调用nssm.exe程序
        :return:返回True
        '''
        install_log.debug(u'加入系统服务.')
        os.system(r'%s install FalconAgent %s' % (os.path.join(
            self.Install_Path, 'nssm64.exe') if machine() == 'AMD64' else os.path.join(
            self.Install_Path, 'nssm32.exe'),
                                                  os.path.join(self.Install_Path, 'agent.exe')
                                                  ))
        time.sleep(2)
        try:
            self.__services_manage('start')
        except Exception as e:
            install_log.error(e)
        return True

    def __services_manage(self, action, service='falconagent'):
        '''
        服务管理，用于更新时的检查，重启服务
        :param action: 服务的动作（传入字符串start|stop|restart）
        :param service: 服务的名称，默认为falconagent
        :return: 返回服务的状态。
        '''
        rule = {'stop': win32serviceutil.StopService, 'start': win32serviceutil.StartService,
                'restart': win32serviceutil.RestartService}
        if action == 'status':
            try:
                if win32serviceutil.QueryServiceStatus(service) == win32service.SERVICE_RUNNING:
                    return 'running'
            except Exception as err:
                return install_log.error(err)
        else:
            return rule.get(action, 'restart')(service)

    def __Install(self, x, ds):
        '''
        安装主步骤，先解压，修改json文件，移动目录，添加windows服务再启动服务。
        :param x: 下载文件的路径。
        :param ds: 安装到的目标目录。
        :return: 返回状态。
        '''
        install_log.debug(u'解压，请等待！')
        f = ZipFile(x, mode='r')
        f.extractall(ds)
        # 更改IP文件
        install_log.debug(u'开始安装客户端！')
        ip, addr = self.__SelectIp()
        Change = self.__ChangeFile(ip, addr)
        if not Change:
            install_log.error(u"修改cfg.json文件错误，请检查cfg.json文件！")
            return False
        # 开始安装
        if not os.path.isdir(self.Install_Path):  # 没有此目录时
            install_log.debug(u'安装到： %s' % self.Install_Path)
            move(os.path.join(self.Download_Path, 'agent'), self.Install_Path)
            self.__AddService()

        elif self.__services_manage('status') == 'running':  # 当服务存在时
            try:
                install_log.debug(u'停止服务中')
                self.__services_manage('stop')
                time.sleep(3)
                if not os.path.exists(self.__Backup_Path):  # 检查备份路径是否已经存在
                    install_log.debug(u'备份到：%s' % self.__Backup_Path)
                    move(self.Install_Path, self.__Backup_Path)
                install_log.debug(u'开始更新文件...')
                move(os.path.join(self.Download_Path, 'agent'), self.Install_Path)
                install_log.debug(u'启动服务！')
                self.__services_manage('start')
            except Exception as err:
                install_log.error(err)
                return False

        else:  # 当有目录，但是无服务，或者服务没有启动时。
            install_log.debug(u'备份到：%s' % self.__Backup_Path)
            try:
                if not os.path.exists(self.__Backup_Path):
                    install_log.debug('Backup File to %s' % self.__Backup_Path)
                    move(self.Install_Path, self.__Backup_Path)
                install_log.debug(u'开始更新文件...')
                move(os.path.join(self.Download_Path, 'agent'), self.Install_Path)
                if self.__services_manage('status') == 'stopped':
                    try:
                        self.__services_manage('start')
                    except Exception as err:
                        install_log.error(err)
                else:
                    self.__AddService()
            except Exception as err:
                install_log.error(err)

    def Remote_Md5(self):
        '''
        对比远程Md5.txt文件
        :return: 返回md5码
        '''
        with urlopener(self.AgentMd5) as f:
            for i in f:
                _md5, pkname = i.split()
                if pkname == self.Package_name:
                    return _md5
            else:
                return install_log.error(u'在md5.txt里找不到对应安装包的MD5码，请确认！')

    def File_Md5(self):
        '''
        读取本地md5.txt文件，来验证是否需要更新
        :return: 返回本地md5.txt里面的md5码。
        '''
        fe = os.path.join(self.Install_Path, 'md5.txt')
        install_log.debug(u"本地MD5%s文件"%fe)
        if os.path.exists(fe):
            with open(fe, 'r') as fd:
                for i in fd:
                    _md5, pkname = i.split()
                    if pkname == self.Package_name:
                        return _md5
                else:
                    return install_log.error(u'在md5.txt里找不到对应安装包的MD5码，请确认！')
        else:
            return u""
