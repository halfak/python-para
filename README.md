# Para(llel) processing utilities
This library implements a simple set of parallel processing utilities that
take advantage of python's `multiprocessing` module to distribute processing
over multiple CPUs on a single machine.  The most salient feature of this
library is the **map()** function that can be used to distribute CPU-intensive
processing of a collection of items over multiple cores.

* **Installation** `pip install para`

## Basic usage

    >>> import para
    >>> import gzip
    >>>
    >>> items = ["examples/big-file1.gz", "examples/big-file2.gz",
    ...          "examples/big-file3.gz"]
    >>> def log_lines(path):
    ...     with gzip.open(path, 'rt') as f:
    ...         for lineno, line in enumerate(f):
    ...             if len(line) > 50:
    ...                 yield path, lineno, line
    ...
    >>> for path, lineno, line in para.map(log_lines, items):
    ...     print(path, lineno, repr(line))
    ...
    examples/big-file1.gz 2 'this line is going to be much longer than 80 chars -- at least I hope it will\n'
    examples/big-file3.gz 0 'again with the long lines -- this is going to show up in the output, I hope\n'

## Authors
* Aaron Halfaker -- https://github.com/halfak
