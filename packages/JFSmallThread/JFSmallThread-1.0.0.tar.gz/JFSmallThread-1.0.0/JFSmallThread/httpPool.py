import http
from http.client import HTTPConnection, HTTPResponse, HTTPSConnection
from JFSmallThread.contrib import AbstractObject


class HttpOperator(AbstractObject):
    error_type_list_set_not_available = [http.client.CannotSendRequest]

    def __init__(self, host, port=None, timeout=5, source_address=None, is_https=False):
        super().__init__()
        if is_https:
            self.conn = HTTPSConnection(host=host, port=port, timeout=timeout, source_address=source_address, )
        else:
            self.conn = HTTPConnection(host=host, port=port, timeout=timeout, source_address=source_address, )
        self.core_obj = self.conn

    def clean_up(self):
        self.conn.close()

    def before_back_to_queue(self, exc_type, exc_val, exc_tb):
        pass

    def speed_request(self, method, url, body=None, headers=None, *, encode_chunked=False,
                      encoding="utf-8") -> HTTPResponse:
        """
        :param method:
        :param url:
        :param body: 不支持form-data格式
        :param headers:
        :param encode_chunked:
        :param encoding:
        :return:
        """
        if headers is None:
            headers = {}
        self.conn.request(method, url, body=bytes(body, encoding='utf-8'), headers=headers,
                          encode_chunked=encode_chunked)
        resp = self.conn.getresponse()
        resp.content = resp.read()
        resp.text = resp.content.decode(encoding)
        return resp
