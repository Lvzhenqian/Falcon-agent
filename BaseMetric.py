# coding=utf-8
import copy
import psutil
import time
import logging

from JsonClient import UpdateMetric
from config import HOSTNAME, log_File, VERSION, COLLECTOR, IGNORE, base_leve, MLOG
from diskIOmertic import diskIO

base_log = logging.getLogger(u'基础监控')
base_log.setLevel(base_leve)
base_log.propagate = False
base_log.addHandler(log_File)


# base_log.addHandler(console)


def is_interface_ignore(key):
    """
    是否忽略某些接口的值
    :param key: 传入接口名称
    :return: 返回true
    """
    for ignore_key in COLLECTOR['ifacePrefixIgnore']:
        if ignore_key in key.decode('gbk'):
            return True


def collect():
    """
    基础 数据获取、上传函数。函数获取监控指标列表：
agent alive
version
cpu:
    cpu.user
    cpu.idle
    cpu.busy
    cpu.system
memory and swap:
    mem.memtotal
    mem.memused
    mem.memfree.percent
    mem.memfree
    mem.memused.percent
    mem.swapused.percent
    mem.swaptotal
    mem.swapused
    mem.swapfree
    mem.swapfree.percent
disk_partitions:
    df.bytes.used.percent
    df.bytes.total
    df.bytes.used
    df.bytes.free
    df.bytes.free.percent
disk io_status:
    disk.io.msec_read
    disk.io.msec_write
    disk.io.read_bytes
    disk.io.read_requests
    disk.io.write_bytes
    disk.io.write_requests
    disk.io.util
network interface:
    net.if.in.bytes
    net.if.out.bytes
    net.if.in.packets
    net.if.out.packets
    net.if.in.errors
    net.if.out.errors
    net.if.in.dropped
    net.if.out.dropped
    net.if.total.bytes
    net.if.total.packets
    net.if.total.errors
    net.if.total.dropped
    :return:
    """
    base_log.debug(u'基础数据提交')
    time_now = int(time.time())
    payload = []
    start = payload.__len__()
    # agent alive
    base_log.debug(u"开始导入agent.alive值到列表中！")
    data = {"endpoint": HOSTNAME, "metric": "agent.alive", "timestamp": time_now, "step": 60, "value": 1,
            "counterType": "GAUGE", "tags": ""}
    payload.append(copy.copy(data))
    _next = payload.__len__() - start
    start = payload.__len__()
    base_log.debug(u"导入agent.alive值成功！导入数量：%s" % _next)

    # version
    base_log.debug(u"开始导入agent.version值到列表中！")
    data["metric"] = "agent.version"
    data["value"] = VERSION
    data["counterType"] = "GAUGE"
    payload.append(copy.copy(data))
    _next = payload.__len__() - start
    start = payload.__len__()
    base_log.debug(u"导入agent.version值到成功！导入数量：%s" % _next)

    # cpu
    try:
        base_log.debug(u"开始导入CPU监控值到列表中！")
        cpu_status = psutil.cpu_times_percent()
        # cpu.user
        data["metric"] = "cpu.user"
        data["value"] = cpu_status.user
        data["counterType"] = "GAUGE"
        payload.append(copy.copy(data))
        # cpu.system
        data["metric"] = "cpu.system"
        data["value"] = cpu_status.system
        payload.append(copy.copy(data))
        # cpu.idle
        data["metric"] = "cpu.idle"
        data["value"] = cpu_status.idle
        payload.append(copy.copy(data))
        # cpu.busy
        data["metric"] = "cpu.busy"
        data["value"] = round(100 - cpu_status.idle, 2)
        payload.append(copy.copy(data))
        _next = payload.__len__() - start
        start = payload.__len__()
        base_log.debug(u"导入CPU监控值成功！导入量：%s" % _next)
    except Exception, e:
        base_log.error(u"获取CPU数据失败！错误信息：%s" % e)

    # memory and swap
    try:
        base_log.debug(u"开始导入memory以及swap监控值到列表中！")
        swap_status = psutil.swap_memory()
        mem_status = psutil.virtual_memory()
        #########memory########
        # total
        data["metric"] = "mem.memtotal"
        data["value"] = mem_status.total
        payload.append(copy.copy(data))
        # used
        data["metric"] = "mem.memused"
        data["value"] = mem_status.used
        payload.append(copy.copy(data))
        # free.percent
        data["metric"] = "mem.memfree.percent"
        data["value"] = round(100 - mem_status.percent, 2)
        payload.append(copy.copy(data))
        # free
        data["metric"] = "mem.memfree"
        data["value"] = mem_status.free
        payload.append(copy.copy(data))
        # used.percent
        data["metric"] = "mem.memused.percent"
        data["value"] = mem_status.percent
        payload.append(copy.copy(data))
        ########swap##########
        # used.percent
        data["metric"] = "mem.swapused.percent"
        data["value"] = swap_status.percent
        payload.append(copy.copy(data))
        # total
        data["metric"] = "mem.swaptotal"
        data["value"] = swap_status.total
        payload.append(copy.copy(data))
        # used
        data["metric"] = "mem.swapused"
        data["value"] = swap_status.used
        payload.append(copy.copy(data))
        # free
        data["metric"] = "mem.swapfree"
        data["value"] = swap_status.free
        payload.append(copy.copy(data))
        # free.percent
        data["metric"] = "mem.swapfree.percent"
        data["value"] = round(100 - swap_status.percent, 2)
        payload.append(copy.copy(data))
        _next = payload.__len__() - start
        start = payload.__len__()
        base_log.debug(u"导入memory以及swap监控值成功！导入量:%s" % _next)
    except Exception, e:
        base_log.error(u"获取内存或者虚拟内存信息失败！错误信息：%s" % e)

    # disk_partitions
    try:
        base_log.debug(u"开始导入磁盘分区信息监控值到列表中！")
        disk_status = psutil.disk_partitions()
        for disk in disk_status:
            if 'cdrom' in disk.opts or disk.fstype == '':
                continue
            disk_info = psutil.disk_usage(disk.mountpoint)
            # used.percent
            data["metric"] = "df.bytes.used.percent"
            data["value"] = disk_info.percent
            data["tags"] = "fstype=%s,mount=%s" % (disk.fstype, disk.device.split(":")[0])
            payload.append(copy.copy(data))
            # total
            data["metric"] = "df.bytes.total"
            data["value"] = disk_info.total
            payload.append(copy.copy(data))
            # used
            data["metric"] = "df.bytes.used"
            data["value"] = disk_info.used
            payload.append(copy.copy(data))
            # free
            data["metric"] = "df.bytes.free"
            data["value"] = disk_info.free
            payload.append(copy.copy(data))
            # free.percent
            data["metric"] = "df.bytes.free.percent"
            data["value"] = round(100 - disk_info.percent, 2)
            payload.append(copy.copy(data))
        _next = payload.__len__() - start
        start = payload.__len__()
        base_log.debug(u"导入磁盘分区信息监控值成功！导入量：%s" % _next)
    except Exception, e:
        base_log.error(u"获取磁盘分区信息失败！错误信息：%s" % e)

    # disk_io_status
    try:
        base_log.debug(u"开始执行diskIO函数！并导入磁盘IO信息")
        get_disk_io = diskIO()
        # base_log.debug(get_disk_io)
        if get_disk_io:
            payload.extend(get_disk_io)
            _next = payload.__len__() - start
            start = payload.__len__()
            base_log.debug(u"导入磁盘IO信息成功！导入量：%s" % _next)
    except Exception, e:
        base_log.error(u"获取磁盘信息错误！错误信息：%s" % e)
    # network interface
    try:
        base_log.debug(u"开始导入网卡监控值！")
        net_io_status = psutil.net_io_counters(pernic=True)
        for key in net_io_status:
            if is_interface_ignore(key):
                continue
            # in.bytes
            data["metric"] = "net.if.in.bytes"
            data["value"] = net_io_status[key].bytes_recv
            data["tags"] = "iface=" + key.decode("gbk")
            data["counterType"] = "COUNTER"
            payload.append(copy.copy(data))
            # out.bytes
            data["metric"] = "net.if.out.bytes"
            data["value"] = net_io_status[key].bytes_sent
            payload.append(copy.copy(data))
            # in.packets
            data["metric"] = "net.if.in.packets"
            data["value"] = net_io_status[key].packets_recv
            payload.append(copy.copy(data))
            # out.packets
            data["metric"] = "net.if.out.packets"
            data["value"] = net_io_status[key].packets_sent
            payload.append(copy.copy(data))
            # in.errors
            data["metric"] = "net.if.in.errors"
            data["value"] = net_io_status[key].errin
            payload.append(copy.copy(data))
            # out.errors
            data["metric"] = "net.if.out.errors"
            data["value"] = net_io_status[key].errout
            payload.append(copy.copy(data))
            # in.dropped
            data["metric"] = "net.if.in.dropped"
            data["value"] = net_io_status[key].dropin
            payload.append(copy.copy(data))
            # out.dropped
            data["metric"] = "net.if.out.dropped"
            data["value"] = net_io_status[key].dropout
            payload.append(copy.copy(data))
            # total.bytes
            data["metric"] = "net.if.total.bytes"
            data["value"] = (net_io_status[key].bytes_recv + net_io_status[key].bytes_sent)
            payload.append(copy.copy(data))
            # total.packets
            data["metric"] = "net.if.total.packets"
            data["value"] = (net_io_status[key].packets_recv + net_io_status[key].packets_sent)
            payload.append(copy.copy(data))
            # total.errors
            data["metric"] = "net.if.total.errors"
            data["value"] = (net_io_status[key].errin + net_io_status[key].errout)
            payload.append(copy.copy(data))
            # total.dropped
            data["metric"] = "net.if.total.dropped"
            data["value"] = (net_io_status[key].dropin + net_io_status[key].dropout)
            payload.append(copy.copy(data))
        _next = payload.__len__() - start
        base_log.debug(u"导入网卡监控值成功！导入量：%s" % _next)
    except Exception, e:
        base_log.error(u"获取网络接口信息失败！错误信息：%s", e)

    data = [x for x in payload if x.get('metric') not in IGNORE]
    # metric log
    if MLOG:
        from config import metric_file, metric_leve
        metriclog = logging.getLogger(u'基础监控日志')
        metriclog.setLevel(metric_leve)
        metriclog.propagate = False
        metriclog.addHandler(metric_file)
        metriclog.debug(data)

    try:
        base_log.debug(u"即将上传的数据总数：%s", len(data))
        result = UpdateMetric(data)
        if result:
            base_log.info(u"上传基础数据成功！")

    except Exception, err:
        base_log.error(u"上传基础数据出错！报错信息:%s", err)
