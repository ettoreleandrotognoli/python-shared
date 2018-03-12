from rx import Observable


class BuffAndSplit(object):
    def __init__(self, delimiter=b'\r\n', initial=b''):
        self.delimiter = delimiter
        self.buffer = initial

    def __call__(self, e):
        self.buffer += e
        if self.delimiter not in self.buffer:
            return Observable.empty()
        packages = self.buffer.split(self.delimiter)
        self.buffer = packages[-1]
        return Observable.from_(packages[:-1])
