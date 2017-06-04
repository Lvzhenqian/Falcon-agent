import logging
from util.config import TRANSFER, log_File, console, leve
from Client.RPC import client

ADDRS = TRANSFER['addrs']
trans_log = logging.getLogger('root.TransClient')
trans_log.setLevel(leve)
trans_log.propagate = False
trans_log.addHandler(log_File)
trans_log.addHandler(console)


class Transfer(client):
    def __init__(self, addr: tuple):
        super().__init__(addr)
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
        ip, port = addr.split(':')
        connections[addr] = Transfer((ip, int(port)))
    return connections[addr]


def UpdateMetric(metrics: list):
    if isinstance(ADDRS, list):
        for add in ADDRS:
            ip, port = add.split(':')
            c = __init_client((ip, int(port)))
            for _ in range(5):
                resp = c.SendMetric('Transfer.Update', metrics)
                if resp.get('Message', 'fail') == 'ok':
                    return resp
        else:
            trans_log.error("无法发送到Transfer，请检查网络！")
