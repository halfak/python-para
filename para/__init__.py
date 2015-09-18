"""
This library implements a simple set of parallel processing utilities that
take advantage of python's `multiprocessing` module to distribute processing
over multiple CPUs on a single machine.  The most salient feature of this
library is the `map()` function that can be used to distribute CPU-intensive
processing of a collection of items over multiple cores.
"""
from .map import map

__version__ = "0.0.5"

__all__ = [map]
