# coding:utf8
import copy
import logging
import time

from win32com.client import GetObject
from config import leve, log_File, HOSTNAME

disk_io_stat = logging.getLogger('root.Disk_IO')
disk_io_stat.setLevel(leve)
disk_io_stat.propagate = False
disk_io_stat.addHandler(log_File)


# disk io_status
def diskIO():
    payload = []
    WmiObject = GetObject('winmgmts:/root/cimv2')
    base_sql = """SELECT
        AvgDiskSecPerRead_Base,
        AvgDiskSecPerWrite_Base,
        DiskReadBytesPerSec,
        DiskReadsPerSec,
        DiskWriteBytesPerSec,
        DiskWritesPerSec FROM Win32_PerfRawData_PerfDisk_PhysicalDisk WHERE name='_Total' """
    base_stat = WmiObject.ExecQuery(base_sql)
    time_now = int(time.time())
    # read.count
    data = {"endpoint": HOSTNAME, "metric": "disk.io.msec_read", "timestamp": time_now, "step": 60,
            "value": base_stat[0].AvgDiskSecPerRead_Base, "counterType": "COUNTER", "tags": "device=total"}
    payload.append(copy.copy(data))
    # write.count
    data["metric"] = "disk.io.msec_write"
    data["value"] = base_stat[0].AvgDiskSecPerWrite_Base
    payload.append(copy.copy(data))
    # read.bytes
    data["metric"] = "disk.io.read_bytes"
    data["value"] = base_stat[0].DiskReadBytesPerSec
    payload.append(copy.copy(data))
    # read.requests
    data["metric"] = "disk.io.read_requests"
    data["value"] = base_stat[0].DiskReadsPerSec
    payload.append(copy.copy(data))
    # write.bytes
    data["metric"] = "disk.io.write_bytes"
    data["value"] = base_stat[0].DiskWriteBytesPerSec
    payload.append(copy.copy(data))
    # write.requests
    data["metric"] = "disk.io.write_requests"
    data["value"] = base_stat[0].DiskWritesPerSec
    payload.append(copy.copy(data))
    # util
    util_sql = """SELECT PercentIdleTime FROM Win32_PerfFormattedData_PerfDisk_PhysicalDisk WHERE name='_Total'"""
    util_stat = WmiObject.ExecQuery(util_sql)
    data["metric"] = "disk.io.util"
    data["value"] = 100 - int(util_stat[0].PercentIdleTime)
    data["counterType"] = 'GAUGE'
    payload.append(copy.copy(data))
    return payload
