from requests import Response


class RelayerClientException(Exception):
    def __init__(self, msg):
        self.msg = msg


class RelayerApiException(RelayerClientException):
    def __init__(self, resp: Response = None, error_msg=None):
        if resp is None and error_msg is None:
            raise ValueError("invalid resp or error msg")
        if resp is not None:
            self.status_code = resp.status_code
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp: Response):
        try:
            return resp.json()
        except Exception:
            return resp.text

    def __repr__(self):
        return f"RelayerApiException[status_code={self.status_code}, error_message={self.error_msg}]"

    def __str__(self):
        return self.__repr__()
