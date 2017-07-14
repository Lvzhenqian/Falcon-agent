# coding=utf-8
from AutoInstall import *
from threading import Thread
from Manage import JobsManage
import HttpAPI
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers import interval
from config import log_File, PLUGIN, leve, HTTP
from BaseMetric import collect
from Repo import report

Jobs = BlockingScheduler()
thread_log = logging.getLogger('root.crond')
thread_log.setLevel(leve)
thread_log.propagate = False
thread_log.addHandler(log_File)


# thread_log.addHandler(console)
Plugins = JobsManage(PLUGIN)
Plugins.make_jobs()


@Jobs.scheduled_job(trigger='interval', id='UpdataThread', minutes=5)
def UpdataThread():
    server_md5 = None
    ins = Upgrade()
    try:
        server_md5 = ins.Remote_Md5()
        file_md5 = ins.File_Md5()
        if file_md5 == server_md5:
            return thread_log.info(u"Md5验证通过，跳过更新！ ")
    except urllib2.HTTPError:
        thread_log.error(u"无法连接到： %s" % ins.AgentMd5)
    t = Thread(target=ins.Download_And_Install, args=(server_md5,), name=u'更新线程')
    thread_log.info(u'%s--%s' % (t.name, t.ident))
    t.daemon = True
    t.start()


def APIthread():
    ports = HTTP.get('listen')
    if ports:
        t = Thread(target=HttpAPI.app.run, kwargs=dict(port=ports), name=u'API接口线程')
        thread_log.info(u'%s--%s' % (t.name, t.ident))
        t.daemon = True
        t.start()
    else:
        return thread_log.error(u"端口错误，无法开启API传送数据！")


@Jobs.scheduled_job(trigger='interval', id='BaseMetric', minutes=1)
def BasePush():
    try:
        collect()
    except Exception as err:
        thread_log.error(err)
    return


@Jobs.scheduled_job(trigger='interval', id='HbsRepo', minutes=1)
def RepoPush():
    return report()

