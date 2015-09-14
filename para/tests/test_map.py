import sys

from nose.tools import eq_

from ..map import map


def test_map():
    words = ["foo", "bar", "baz"]

    def get_the_a(word):
        for i, char in enumerate(word):
            if char == 'a':
                yield word, i

    set_of_a = set(map(get_the_a, words))

    eq_(set_of_a,
        {
            ("bar", 1),
            ("baz", 1)
        })

def test_map_single():
    paths = [sys.stdin]

    def is_a_file(path):
        yield hasattr(path, "read")

    eq_(sum(map(is_a_file, paths)), 1)
