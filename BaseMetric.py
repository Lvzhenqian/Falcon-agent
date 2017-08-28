# coding=utf-8
import copy
import psutil
import time
import logging

from JsonClient import UpdateMetric
from config import HOSTNAME, log_File, VERSION, COLLECTOR, IGNORE, leve
from diskIOmertic import diskIO

base_log = logging.getLogger('root.BaseMetric')
base_log.setLevel(leve)
base_log.propagate = False
base_log.addHandler(log_File)


# base_log.addHandler(console)


def is_interface_ignore(key):
    for ignore_key in COLLECTOR['ifacePrefixIgnore']:
        if ignore_key in key.decode('gbk'):
            return True


def collect():
    base_log.debug(u'基础数据提交')
    time_now = int(time.time())
    payload = []
    # agent alive
    data = {"endpoint": HOSTNAME, "metric": "agent.alive", "timestamp": time_now, "step": 60, "value": 1,
            "counterType": "GAUGE", "tags": ""}
    payload.append(copy.copy(data))

    # version
    data["metric"] = "agent.version"
    data["value"] = VERSION
    data["counterType"] = "GAUGE"
    payload.append(copy.copy(data))

    # cpu
    try:
        cpu_status = psutil.cpu_times_percent()
        base_log.debug(cpu_status)
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
    except Exception, e:
        base_log.error(e)

    # memory and swap
    try:
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
    except Exception, e:
        base_log.error(e)

    # disk_partitions
    try:
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
    except Exception, e:
        base_log.error(e)

    # disk_io_status
    get_disk_io = diskIO()
    if get_disk_io:
        payload.extend(get_disk_io)
    # network interface
    try:
        net_io_status = psutil.net_io_counters(pernic=True)
        for key in net_io_status:
            if is_interface_ignore(key):
                continue
            # in.bytes
            data["metric"] = "net.if.in.bytes"
            data["value"] = net_io_status[key].bytes_recv
            data["tags"] = "iface=" + key.decode("gbk")
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
    except Exception, e:
        base_log.error(e)

    data = [x for x in payload if x.get('metric') not in IGNORE]
    base_log.debug(data)

    try:
        result = UpdateMetric(data)
        if result:
            base_log.info(u"上传基础数据成功！")
        base_log.debug(result)
    except Exception as err:
        base_log.error(err)
    else:
        base_log.error(result)
