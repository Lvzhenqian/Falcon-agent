# coding:utf8
import copy
import logging
import time
import pythoncom

from win32com.client import GetObject
from config import base_leve, log_File, HOSTNAME

disk_io_stat = logging.getLogger(u'磁盘IO提取')
disk_io_stat.setLevel(base_leve)
disk_io_stat.propagate = False
disk_io_stat.addHandler(log_File)


# disk io_status
def diskIO():
    '''
    使用wmi来取得磁盘IO信息，并添加到列表中
    当使用wmi在一个thread里时要先初始化函数！否则会报(-2147221020, ‘Invalid syntax’, None, None) 语法错误！
    import pythoncom
    pythoncom.CoInitialize()
    do something...
    ...
    ...
    pythoncom.CoUninitialize()
    使用完wmi后要去除初始化
    :return: 返回磁盘IO的信息给主metric!
    '''
    pythoncom.CoInitialize()
    time_now = int(time.time())
    payload = []
    # disk_io_stat.debug(u"创建WMI对象前！")
    WmiObject = GetObject('winmgmts:/root/cimv2')
    try:
        base_sql = """SELECT 
                        AvgDiskSecPerRead_Base,
                        AvgDiskSecPerWrite_Base,
                        DiskReadBytesPerSec,
                        DiskReadsPerSec,
                        DiskWriteBytesPerSec,
                        DiskWritesPerSec FROM Win32_PerfRawData_PerfDisk_PhysicalDisk WHERE name='_Total' """
        # disk_io_stat.debug(u"执行base_sql前！")
        base_stat = WmiObject.ExecQuery(base_sql)
        # read.count
        data = {"endpoint": HOSTNAME, "metric": "disk.io.msec_read", "timestamp": time_now, "step": 60,
                "value": int(base_stat[0].AvgDiskSecPerRead_Base), "counterType": "COUNTER", "tags": "device=total"}
        payload.append(copy.copy(data))
        # write.count
        data["metric"] = "disk.io.msec_write"
        data["value"] = int(base_stat[0].AvgDiskSecPerWrite_Base)
        payload.append(copy.copy(data))
        # read.bytes
        data["metric"] = "disk.io.read_bytes"
        data["value"] = int(base_stat[0].DiskReadBytesPerSec)
        payload.append(copy.copy(data))
        # read.requests
        data["metric"] = "disk.io.read_requests"
        data["value"] = int(base_stat[0].DiskReadsPerSec)
        payload.append(copy.copy(data))
        # write.bytes
        data["metric"] = "disk.io.write_bytes"
        data["value"] = int(base_stat[0].DiskWriteBytesPerSec)
        payload.append(copy.copy(data))
        # write.requests
        data["metric"] = "disk.io.write_requests"
        data["value"] = int(base_stat[0].DiskWritesPerSec)
        payload.append(copy.copy(data))
    except Exception, e:
        disk_io_stat.error(u"基础磁盘IO获取失败！错误代码：%s", e)
    # util
    try:
        # disk_io_stat.debug(u"执行util_sql前！")
        util_sql = """SELECT PercentIdleTime FROM Win32_PerfFormattedData_PerfDisk_PhysicalDisk WHERE name='_Total'"""
        util_stat = WmiObject.ExecQuery(util_sql)
        data = {"endpoint": HOSTNAME, "metric": "disk.io.util", "timestamp": time_now, "step": 60,
                "value": 100 - int(util_stat[0].PercentIdleTime), "counterType": "GAUGE", "tags": "device=total"}
        payload.append(copy.copy(data))
    except Exception, e:
        disk_io_stat.error(u"磁盘使用率信息获取失败！错误信息：%s", e)
    pythoncom.CoUninitialize()
    return payload


# if __name__ == '__main__':
#     print diskIO()
