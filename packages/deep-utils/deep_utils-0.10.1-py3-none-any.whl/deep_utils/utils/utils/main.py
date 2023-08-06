import argparse
import sys


class frozendict:
    def __init__(self, **kwargs):
        super(frozendict, self).__init__()
        self.repo = dict()
        for key, item in kwargs.items():
            self.repo[key] = item

    def __getitem__(self, item):
        return self.repo[item]

    def __setitem__(self, key, value):
        raise TypeError(f"frozendict object does not support updating")


def shift_lst(lst: list, move_forward):
    return lst[-move_forward:] + lst[:-move_forward]


if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
    from deep_utils.utils.utils.dictnamedtuple_38 import dictnamedtuple
else:
    from deep_utils.utils.utils.dictnamedtuple_37 import dictnamedtuple
