# coding:utf8
import os
import logging
from config import log_File, leve
from JsonClient import UpdateMetric
import crond

manage_log = logging.getLogger('root.Mange')
manage_log.setLevel(leve)
manage_log.propagate = False
manage_log.addHandler(log_File)


# manage_log.addHandler(console)


class JobsManage:
    '''
    插件管理类，用于读取并执行plugin里的.py文件。并把获取到的值加入metric列表
    '''
    def __init__(self, plugin):
        self.PluginPath = plugin

    def executive(self, x):
        manage_log.debug(u"开始导入 %s文件！" % x)
        with open(x, 'r') as f:
            code = f.read()
        if 'subprocess' in code and 'STARTF_USESHOWWINDOW' not in code:
            manage_log.error(
                u"""
		[%s] 插件 
		这个插件使用了 subprocess 模块,
		但是并没有添加 [startupinfo] 这个参数进Popen 里，这将会导致主程序异常.
		你的脚本必须添加 (stdin,stdout,stderr) 定向到 PIPE 或者 DEVNULL
		然后添加这个参数： env=os.environ.
		例子:
			si = subprocess.STARTUPINFO()
			si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			subprocess.Popen(startupinfo=si,env=os.environ,
			stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL,
			)
	""" % os.path.basename(x))
            return False
        ret = {'metric': None}
        manage_log.debug(u"执行exec 语句并把文件反回结果捕获！")
        exec (code, ret)
        return ret['metric']

    def push(self, py):
        parms = []
        try:
            data, plugin_err = self.executive(py)
            manage_log.debug(u"%s文件数值： %s" % (py, data))
        except AttributeError:
            data = False
            plugin_err = True
        if data and not plugin_err:
            manage_log.debug(u"开始添加[%s]进列表！" % os.path.basename(py))
            if isinstance(data, dict):
                parms.append(data)
            elif isinstance(data, list):
                parms.extend(data)
        else:
            manage_log.error(u"错误！无法读取[%s] 这个插件." % (os.path.basename(py)))
            manage_log.error(u"%s 插件错误信息：%s" % (os.path.basename(py), plugin_err))
        #准备开始上传插件
        manage_log.debug(u"%s 插件将要上传的数值：%s" % (os.path.basename(py),parms))
        rep = UpdateMetric(parms)
        if rep:
            manage_log.info(u"上传 %s 成功！状态：%s" % (os.path.basename(py), rep))

    def make_jobs(self):
        if not os.path.exists(self.PluginPath):
            return
        for files in os.listdir(self.PluginPath):
            f_name = os.path.basename(files)
            if f_name.endswith('.py') and f_name[0].isdigit():
                try:
                    timer, name = f_name.split("_")
                except ValueError:
                    manage_log.error(u'''无法导入 %s 此文件，格式说明：300_ping.py''' % f_name)
                    continue
                # 加入计划任务列表，在每次客户端启动时。ps:所有的plugin在新增时要重启客户端，才会生效。原因如下：
                crond.Jobs.add_job(func=self.push, args=(os.path.join(self.PluginPath, f_name),), trigger='interval',
                                   seconds=int(timer), id=name[:-3])
            else:
                manage_log.error(u'''无法导入 %s 此文件，格式说明：300_ping.py''' % f_name)
                #
                # def run():
                # 	job = JobsManage(PLUGIN)
                # 	runlist = job.make_jobs()
                # 	runlist.start()
