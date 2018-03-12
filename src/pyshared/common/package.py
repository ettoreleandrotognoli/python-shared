import json

parsers = {
    'json': (json.dumps, json.loads)
}


def parse_parser(name):
    return parsers[name]
