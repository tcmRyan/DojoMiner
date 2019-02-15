import browser_cookie3
from requests_html import HTMLSession
from setting import config

SUPPORTED_BROWSERS = ['chrome', 'firefox']


class DojoRequests:
    """
    Small wrapper around the requests library to make it easy to make calls to the
    dojo/gdp api.  DojoRequests automatically adds the cookies in for to make sure
    the requests are authenticated.  For documentation just view the Pythons Requests
    library.
    """

    def __init__(self):
        self.session = HTMLSession()
        if config.get('browser') == 'firefox':
            self.cookies = browser_cookie3.firefox()
        else:
            self.cookies = browser_cookie3.chrome()

    def request(self, method, url, **kwargs):
        method = method.upper()
        request_args = {
            'url': url,
            'method': method,
            'cookies': self.cookies
        }
        request_args.update(kwargs)
        return self.session.request(**request_args)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)
