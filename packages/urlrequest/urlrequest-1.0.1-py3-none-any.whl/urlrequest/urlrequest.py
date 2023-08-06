"""
    wrapper for urllib.request.urlopen
    very limited drop-in replacement for requests when you cant import requests
    and need to use the built in urllib.request library
"""
class UrlRequest:
    """
        urllib.request in a class to make it easier to use
    """
    def __init__(self,
                url:str,
                data:str = None,
                json = None,
                method:str = 'GET',
                headers:dict = None,
                timeout:float = 10,
                auth:tuple = None,
                raiseme = True # False to not raise exceptions
                ):

        # importing here to keep it all contained
        # so can copy and paste this class into other scripts
        # pylint: disable=import-outside-toplevel
        import urllib.request
        import urllib.error
        import json as jsonclass

        if headers is None: # python quirk with default mutables
            headers = {}

        # writes in a user agent if not there
        # default Python-urllib/X.X seems to be blocked by some
        if not headers.get('User-Agent'):
            headers['User-Agent'] = 'UrlRequest v1.0.0'

        if auth: # Basic Auth
            authhandle = urllib.request.HTTPPasswordMgrWithPriorAuth()
            authhandle.add_password(None, url, auth[0], auth[1],is_authenticated=True)
            opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(authhandle))
            urllib.request.install_opener(opener)

        if json: # json formatting and adding header
            headers['Content-Type'] = 'application/json'
            data = jsonclass.dumps(json)

        if isinstance(data,dict): # formatting dicts to urlencoded
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            output = ''
            for key,value in data.items():
                output = output + key + '=' + value + '&'
            data = output

        if data: # data formatting
            data = data.encode('utf-8',errors='ignore')

        req = urllib.request.Request(url,data=data,method=method,headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as request:
                self.raw = request.read()
                self.text = self.raw.decode('utf-8',errors='backslashreplace')
                self.status_code = request.status
                self.headers = dict(request.headers)
                try:
                    self.json = jsonclass.loads(self.text)
                except jsonclass.JSONDecodeError:
                    self.json = None

        except urllib.error.HTTPError as exception:
            self.text = exception.reason
            self.status_code = exception.code
            self.headers = dict(exception.headers)
            self.json = {"Error":f'{exception.reason}'}
            if raiseme:
                raise exception

        # catches connection errors
        except urllib.error.URLError as exception:
            self.text = exception.reason
            self.status_code = 483 # unused code
            self.headers = {}
            self.json = {"Error":f'{exception.reason}'}
            if raiseme:
                raise exception

    def __str__(self):
        return str(self.status_code)

    # next part is for drop-in replacement for requests
    # doesnt really do anything else
    # pylint: disable=no-self-argument,no-method-argument,missing-function-docstring
    def get(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='GET')
    def post(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='POST')
    def put(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='PUT')
    def delete(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='DELETE')
    def head(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='HEAD')
    def patch(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='PATCH')
