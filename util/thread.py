from AutoUpdate.Install import *
from threading import Thread
from PluginManage.Manage import JobsManage
from api import HttpAPI
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers import interval
from util.config import log_File, console, PLUGIN, leve
from Metric.BaseMetric import collect
from Metric.Repo import report

Jobs = BlockingScheduler()
Plugin = JobsManage(PLUGIN)
Plugin.make_jobs()

thread_log = logging.getLogger('root.thread')
thread_log.setLevel(leve)
thread_log.propagate = False
thread_log.addHandler(log_File)
thread_log.addHandler(console)


@Jobs.scheduled_job(trigger='interval', id='UpdataThread', minutes=5)
def UpdataThread():
    md5file = None
    ins = Upgrade()
    try:
        with request.urlopen(ins.AgentMd5) as f:
            md5file = f.read()
            server_md5 = md5sum(md5file).hexdigest()
        file = os.path.join(ins.Install_Path, 'md5.txt')
        if os.path.exists(file):
            with open(file, 'rb') as fd:
                file_md5 = md5sum(fd.read()).hexdigest()
            if file_md5 == server_md5:
                return thread_log.info("Md5验证通过，跳过更新！ ")
    except error.HTTPError:
        thread_log.error("无法连接到： %s" % ins.AgentMd5)
    t = Thread(target=ins.Download_And_Install, args=(md5file,), name='更新线程', daemon=True)
    thread_log.info('{}--{}'.format(t.name, t.ident))
    t.start()


def APIthread():
    t = Thread(target=HttpAPI.app.run, kwargs=dict(port=1988), name='API接口线程', daemon=True)
    thread_log.info('{}--{}'.format(t.name, t.ident))
    t.start()


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
