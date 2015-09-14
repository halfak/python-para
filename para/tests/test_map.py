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
    words = ["baz"]

    def get_the_a(word):
        for i, char in enumerate(word):
            if char == 'a':
                yield word, i

    set_of_a = set(map(get_the_a, words))

    eq_(set_of_a,
        {
            ("baz", 1)
        })
