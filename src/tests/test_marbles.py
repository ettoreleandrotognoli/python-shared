import time

from rx import Observable
from rx.subjects import AsyncSubject,Subject
from rx.testing import marbles


def build_subject(e):
    subject = Subject()
    subject.subscribe(lambda m: print('subject of ' + e + ' receive: ' + m))
    return subject


def build_response(e):
    size = 5
    m = '-'.join(map(''.join, zip([e] * size, map(str, range(size))))) + '|'
    print(m)
    return Observable.from_marbles(m)


Observable.from_marbles('a-b-c-d-e-f-g|') \
    .map(lambda e: (e, build_subject(e))) \
    .subscribe(lambda v: build_response(v[0]).subscribe(v[1]))

time.sleep(10)
