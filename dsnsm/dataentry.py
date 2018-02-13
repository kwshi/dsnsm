import time


class DataError(Exception):
    def __init__(self, key, message):
        self.key = key
        self.message = message

    def __str__(self):
        return 'DataError for key `{}`: {}'.format(self.key,
                                                   self.message)


class DataEntry:
    def __init__(self,
                 name,
                 client_timestamp,
                 server_timestamp,
                 message,
                 method,
                 ip,
                 _id=None):
        self.name = name
        self.client_timestamp = client_timestamp
        self.server_timestamp = server_timestamp
        self.message = message
        self.method = method
        self.ip = ip

    @classmethod
    def from_request(cls, name, request):
        values = request.values

        if request.is_json:
            values = request.get_json()

        try:
            client_timestamp = int(values.get('time'))
        except ValueError:
            raise DataError('client_timestamp',
                            'Invalid timestamp (integer conversion failed)')
            client_timestamp = -1

        server_timestamp = int(time.time())

        message = values.get('message', '')

        return cls(name=name,
                   client_timestamp=client_timestamp,
                   server_timestamp=server_timestamp,
                   message=message,
                   method=request.method,
                   ip=request.headers.get('X-Forwarded-For',
                                          request.remote_addr))

    def __iter__(self):
        yield from (('name', self.name),
                    ('client_timestamp', self.client_timestamp),
                    ('server_timestamp', self.server_timestamp),
                    ('message', self.message),
                    ('method', self.method),
                    ('ip', self.ip))
