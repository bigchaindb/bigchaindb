import functools
import codecs
from functools import lru_cache


class HDict(dict):
    def __hash__(self):
        return hash(codecs.decode(self['id'], 'hex'))


@lru_cache(maxsize=16384)
def from_dict(func, *args, **kwargs):
    return func(*args, **kwargs)


def memoize_from_dict(func):

    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        args = list(args)
        args[1] = HDict(args[1])
        new_args = tuple(args)
        return from_dict(func, *new_args, **kwargs)

    return memoized_func


@lru_cache(maxsize=16384)
def to_dict(func, *args, **kwargs):
    return func(*args, **kwargs)


def memoize_to_dict(func):

    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        if args[0].id:
            return to_dict(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)

    return memoized_func
