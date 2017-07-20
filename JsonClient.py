# coding=utf-8
import json
import socket
import logging
from config import TRANSFER, HEARTBEAT, leve, log_File

ADDRS = TRANSFER['addrs']
HBS = HEARTBEAT.get('addr')
jclient = logging.getLogger('root.JsonClient')
jclient.setLevel(leve)
jclient.propagate = False
jclient.addHandler(log_File)


class client(object):
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port

    def __enter__(self):
        try:
            self.socket.connect((self.ip, self.port))
            return self
        except socket.error, e:
            jclient.error(u"连接%s端口%s失败，请检查！msg:%s" % (self.ip, self.port, e))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()

    @staticmethod
    def count():
        n = 0
        while True:
            yield n
            n += 1

    def SendMetric(self, name, data):
        count = client.count()
        sender = dict(id=next(count), method=name, params=[data])
        s_id = sender.get('id')
        mesg = json.dumps(sender).encode()
        self.socket.sendall(mesg)
        rep = self.socket.recv(4096)
        resp = json.loads(rep)
        if resp.get('id') != s_id:
            raise Exception("expected id=%s, received id=%s: %s" % (
                s_id, resp.get('id'), resp.get('error')
            ))
        if resp.get('error') is not None:
            raise Exception(resp.get('error'))
        return resp.get('result')


def UpdateMetric(metrics):
    if isinstance(ADDRS, list):
        for add in ADDRS:
            ip, port = add.split(':')
            with client(ip, int(port)) as Transfer:
                for _ in range(5):
                    resp = Transfer.SendMetric('Transfer.Update', metrics)
                    if resp.get('Message', 'fail') == 'ok':
                        jclient.debug(u"Transfuer发送数据成功：%s"%resp)
                        return resp
                else:
                    jclient.debug(u"Transfuer发送数据失败!ip: %s"%ip)


def UpdateReport(metrics):
    ip, port = HBS.split(':')
    with client(ip, int(port)) as hbs:
        for _ in range(5):
            try:
                resp = hbs.SendMetric('Agent.ReportStatus', metrics)
            except Exception as err:
                jclient.error(u"Report发送数据失败！msg: %s"%err)
                resp = None
            if resp:
                jclient.debug(u"Report发送数据成功: %s" % resp)
                return resp
