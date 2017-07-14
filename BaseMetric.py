# coding=utf-8
import copy
import psutil
import time
import logging

from TransClient import UpdateMetric
from config import HOSTNAME, log_File, VERSION, COLLECTOR, IGNORE, leve

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
    data = {"endpoint": HOSTNAME, "metric": "", "timestamp": time_now,
            "step": 60, "value": "", "counterType": "", "tags": ""}

    # agent alive
    data["metric"] = "agent.alive"
    data["value"] = 1
    data["counterType"] = "GAUGE"
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
        data["metric"] = "cpu.user"
        data["value"] = cpu_status.user
        data["counterType"] = "GAUGE"
        payload.append(copy.copy(data))

        data["metric"] = "cpu.system"
        data["value"] = cpu_status.system
        payload.append(copy.copy(data))

        data["metric"] = "cpu.idle"
        data["value"] = cpu_status.idle
        payload.append(copy.copy(data))
    except Exception, e:
        base_log.error(e)

    # memory
    try:
        swap_status = psutil.swap_memory()
        mem_status = psutil.virtual_memory()
        data["metric"] = "mem.memused.percent"
        data["value"] = mem_status.percent
        payload.append(copy.copy(data))

        data["metric"] = "mem.swapused.percent"
        data["value"] = swap_status.percent
        payload.append(copy.copy(data))
    except Exception, e:
        base_log.error(e)

    # disk
    try:
        disk_status = psutil.disk_partitions()
        for disk in disk_status:
            if 'cdrom' in disk.opts or disk.fstype == '':
                continue
            disk_info = psutil.disk_usage(disk.mountpoint)

            data["metric"] = "df.used.percent"
            data["value"] = disk_info.percent
            data["tags"] = "disk=" + disk.device.split(":")[0]
            payload.append(copy.copy(data))

            data["metric"] = "df.byte.total"
            data["value"] = disk_info.total
            payload.append(copy.copy(data))

            data["metric"] = "df.byte.used"
            data["value"] = disk_info.used
            payload.append(copy.copy(data))

            data["metric"] = "df.byte.free"
            data["value"] = disk_info.free
            payload.append(copy.copy(data))
    except Exception, e:
        base_log.error(e)
    try:
        disk_io_status = psutil.disk_io_counters(perdisk=True)
        for key in disk_io_status:
            data["metric"] = "disk.io.read_count"
            data["value"] = disk_io_status[key].read_count
            data["tags"] = "device=" + key
            data["counterType"] = "COUNTER"
            payload.append(copy.copy(data))

            data["metric"] = "disk.io.write_count"
            data["value"] = disk_io_status[key].write_count
            payload.append(copy.copy(data))

            data["metric"] = "disk.io.read_bytes"
            data["value"] = disk_io_status[key].read_bytes
            payload.append(copy.copy(data))

            data["metric"] = "disk.io.write_bytes"
            data["value"] = disk_io_status[key].write_bytes
            payload.append(copy.copy(data))

            data["metric"] = "disk.io.read_time"
            data["value"] = disk_io_status[key].read_time
            payload.append(copy.copy(data))

            data["metric"] = "disk.io.write_time"
            data["value"] = disk_io_status[key].write_time
            payload.append(copy.copy(data))
    except Exception, e:
        base_log.error(e)

    # network interface
    try:
        net_io_status = psutil.net_io_counters(pernic=True)
        for key in net_io_status:
            if is_interface_ignore(key):
                continue

            data["metric"] = "net.if.in.mbits"
            data["value"] = net_io_status[key].bytes_recv * 8 / 100000
            data["tags"] = "interface=" + key.decode("gbk")
            payload.append(copy.copy(data))

            data["metric"] = "net.if.out.mbits"
            data["value"] = net_io_status[key].bytes_sent * 8 / 100000
            payload.append(copy.copy(data))

            data["metric"] = "net.if.in.packets"
            data["value"] = net_io_status[key].packets_recv
            payload.append(copy.copy(data))

            data["metric"] = "net.if.out.packets"
            data["value"] = net_io_status[key].packets_sent
            payload.append(copy.copy(data))

            data["metric"] = "net.if.in.error"
            data["value"] = net_io_status[key].errin
            payload.append(copy.copy(data))

            data["metric"] = "net.if.out.error"
            data["value"] = net_io_status[key].errout
            payload.append(copy.copy(data))

            data["metric"] = "net.if.in.drop"
            data["value"] = net_io_status[key].dropin
            payload.append(copy.copy(data))

            data["metric"] = "net.if.out.drop"
            data["value"] = net_io_status[key].dropout
            payload.append(copy.copy(data))
    except Exception, e:
        base_log.error(e)

    data = [x for x in payload if x.get('metric') not in IGNORE]

    try:
        result = UpdateMetric(data)
        if result:
            base_log.info(u"上传基础数据成功！")
        base_log.debug(result)
    except Exception as err:
        base_log.error(err)
    else:
        base_log.error(result)
