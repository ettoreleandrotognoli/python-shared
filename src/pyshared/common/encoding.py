

def parse_encoding(name):
    return lambda e: e.encode(name), lambda e: e.decode(name)

