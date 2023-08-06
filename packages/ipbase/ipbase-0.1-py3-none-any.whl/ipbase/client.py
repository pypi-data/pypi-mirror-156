import everapi


class Client(everapi.Client):
    def __init__(self, api_key, base='https://api.ipbase.com/v2'):
        super(Client, self).__init__(base, api_key)

    def status(self):
        return self._request('/status')

    def info(self, ip=None, language=None):
        return self._request('/info', params={
            'ip': ip,
            'language': language
        })
