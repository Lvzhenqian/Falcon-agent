# coding=utf-8
import logging
from config import TRANSFER, log_File, leve
from RPC import client


ADDRS = TRANSFER['addrs']
trans_log = logging.getLogger('root.TransClient')
trans_log.setLevel(leve)
trans_log.propagate = False
trans_log.addHandler(log_File)
# trans_log.addHandler(console)


class Transfer(client, object):
    def __init__(self, addr):
        super(Transfer, self).__init__(addr)
        self.addr = addr

    def Ping(self):
        for _ in range(3):
            try:
                self.SendMetric('Transfer.Ping', None)
            except Exception as err:
                trans_log.error(err)
                trans_log.error('rebuild connect.')
                self.socket.connect(self.addr)


def __init_client(addr):
    connections = {}
    if connections.get(addr) is not None:
        connections[addr].Ping()
    else:
        ip, port = addr
        connections[addr] = Transfer((ip, port))
    return connections[addr]


def UpdateMetric(metrics):
    trans_log.debug(u"开始传送数据！")
    if isinstance(ADDRS, list):
        for add in ADDRS:
            trans_log.debug(u"发送地址：%s"%add)
            ip, port = add.split(':')
            c = __init_client((ip, int(port)))
            for _ in range(5):
                resp = c.SendMetric('Transfer.Update', metrics)
                trans_log.debug(u"transful接口返回：%s"%resp)
                if resp.get('Message', 'fail') == 'ok':
                    return resp
        else:
            trans_log.error(u"无法发送到Transfer，请检查网络！".encode('utf8'))
