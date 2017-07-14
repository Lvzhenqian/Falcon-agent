import json
import socket


class client(object):
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(addr)
        self.count = self.__count()

    def __count(self):
        n = 0
        while True:
            yield n
            n += 1

    def SendMetric(self, name, data):
        sender = dict(id=next(self.count), method=name, params=[data])
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

    def __del__(self):
        self.socket.close()
