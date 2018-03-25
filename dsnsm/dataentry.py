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
                 delay,
                 timestamp,
                 message,
                 method,
                 ip,
                 _id=None):
        self.name = name
        self.delay = delay
        self.timestamp = timestamp
        self.message = message
        self.method = method
        self.ip = ip

    @classmethod
    def from_request(cls, name, request):
        values = request.values

        if request.is_json:
            values = request.get_json()

        try:
            delay = int(values.get('delay'))
        except ValueError:
            raise DataError('delay',
                            'Invalid time offset (integer conversion failed)')
            delay = -1
        except TypeError:
            raise DataError('delay',
                            'No client delay specified')

        timestamp = int(time.time())

        message = values.get('message', '')

        return cls(name=name,
                   delay=delay,
                   timestamp=timestamp,
                   message=message,
                   method=request.method,
                   ip=request.headers.get('X-Forwarded-For',
                                          request.remote_addr))

    def __iter__(self):
        yield from (('name', self.name),
                    ('delay', self.delay),
                    ('timestamp', self.timestamp),
                    ('message', self.message),
                    ('method', self.method),
                    ('ip', self.ip))
