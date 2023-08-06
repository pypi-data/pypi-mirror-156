import requests
from .helpers import Utils
import logging
import json


def sendRequest(reqType="GET", url="http://localhost:8080", headers=dict(), payload=None):
    try:
        headers['Content-Type'] = 'application/json'
        data = None
        if payload is not None:
            data = json.dumps(payload)
        response = requests.request(reqType, url, headers=headers, data=data)
        res = ""
        if response is not None and response.status_code < 400:
            try:
                res = Utils.getJson(response.text)
            except:
                res = response.text
        # print("sendRequest:", res)
        return res, response.status_code, response.headers
    except Exception as ex:
        raise Exception("Exception in sendRequest {ex}".format(ex=ex))
