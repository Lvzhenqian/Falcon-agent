# coding=utf-8
import logging
from flask import Flask, request, jsonify
import TransClient
from config import log_File, leve

app = Flask(__name__)
api_log = logging.getLogger('root.HttpAPI')
api_log.setLevel(leve)
api_log.propagate = False
api_log.addHandler(log_File)


# api_log.addHandler(console)


@app.route('/health', methods=['GET'])
def health():
    return jsonify('ok')


@app.route('/v1/push', methods=['POST'])
def Push_Metric_By_Youreself():
    rep = False
    update = []
    api_log.info(u'自定义数据上传接口')
    try:
        data = request.get_json()
        api_log.debug(data)
        if isinstance(data, dict):
            update.append(data)
            rep = TransClient.UpdateMetric(update)
        elif isinstance(data, list):
            update.extend(data)
            rep = TransClient.UpdateMetric(update)
        else:
            return jsonify('fail %s' % data)
    except Exception as err:
        api_log.error(err)
        return jsonify('fail %s' % err)
    api_log.debug(rep)
    if rep:
        api_log.info(u'上传成功：%s' % rep)
        return jsonify('successful')
    else:
        return jsonify('fail %s' % rep)
