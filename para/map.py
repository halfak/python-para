import logging
import time
import traceback
from multiprocessing import Process, Queue, cpu_count
from queue import Empty
from threading import Thread

logger = logging.getLogger(__name__)

OUTPUT_QUEUE_TIMEOUT = 0.1
"""
This is how long an output queue will block while waiting for output to process
"""

OUTPUT_QUEUE_SIZE = 50


def map(process, items, mappers=None, output_queue_size=OUTPUT_QUEUE_SIZE):
    """
    Implements a distributed stategy for CPU-intensive tasks.  This
    function constructs a set of :mod:`multiprocessing` threads (spread over
    multiple cores) and uses an internal queue to aggregate outputs.  To use
    this function, implement a `process()` function that takes one argument --
    a serializable job.  Anything that this function ``yield``s will be
    `yielded` in turn from the :func:`para.map` function.

    :Parameters:
        process : `func`
            A function that takes an item as a parameter and returns a
            generator of output values.
        items : `iterable` ( `picklable` )
            :mod:`pickle`-able items to process.  Note that this must fit in
            memory.
        mappers : int
            the number of parallel mappers to spool up
        output_queue_size : int
            the number of outputs to buffer before blocking mappers

    :Example:

        >>> import para
        >>> files = ["examples/dump.xml", "examples/dump2.xml"]
        >>>
        >>> def filter_long_lines(path):
        ...     with open(path) as f:
        ...         for line in f:
        ...             if len(line) > 100:
        ...                 yield (path, line)
        ...
        >>> for path, line in para.map(filter_long_lines, files):
        ...     print(path, line)
        ...
    """

    items = list(items)

    # Special case for a single item
    if len(items) == 1:
        return _map_single_item(process, items[0])
    else:
        return _map_many_items(process, items, mappers)


def _map_single_item(process, item):
    yield from process(item)


def _map_many_items(process, items, mappers,
                    output_queue_size=OUTPUT_QUEUE_SIZE):

    # Load paths into the queue
    item_queue = Queue()
    for item in items:
        item_queue.put(item)

    # How many mappers are we going to have?
    mappers = min(max(1, mappers or cpu_count()), len(items))

    # Prepare the output queue
    output = Queue(output_queue_size or OUTPUT_QUEUE_SIZE)

    # Prepare the logs queue
    qlogger = QueueLogger()
    qlogger.start()

    # Prepare the mappers and start them
    map_processes = [Mapper(process, item_queue, output, qlogger, name=str(i))
                     for i in range(mappers)]
    for map_process in map_processes:
        map_process.start()

    # Read from the output queue while there's still a mapper alive or
    # something in the queue to read.
    while not output.empty() or sum(m.is_alive() for m in map_processes) > 0:
        try:
            # if we timeout, the loop will check to see if we are done
            error, value = output.get(timeout=OUTPUT_QUEUE_TIMEOUT)

            if error is None:
                yield value
            else:
                raise error
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt detected.  Finishing...")
            break

        except Empty:
            # This can happen when mappers aren't adding values to the
            # queue fast enough *or* if we're done processing.  Let the while
            # condition determine if we are done or not.
            continue


class Mapper(Process):
    """
    Implements a mapper process worker.  Instances of this class will
    continually try to read from an `item_queue` and execute it's `process()`
    function until there is nothing left to read from the `item_queue`.
    """
    def __init__(self, process, item_queue, output, logger, name=None):
        super().__init__(name="Mapper {0}".format(name), daemon=True)
        self.process = process
        self.item_queue = item_queue
        self.output = output
        self.logger = logger
        self.stats = []

    def run(self):
        logger.info("{0}: Starting up.".format(self.name))
        try:
            while True:
                # Get an item to process
                item = self.item_queue.get(timeout=0.05)
                self.logger.info("{0}: Processing {1}"
                                 .format(self.name, str(item)[:50]))

                try:
                    start_time = time.time()
                    count = 0
                    # For each value that is yielded, add it to the output
                    # queue
                    for value in self.process(item):
                        self.output.put((None, value))
                        count += 1
                    self.stats.append((item, count, time.time() - start_time))
                except Exception as e:
                    self.logger.error(
                        "{0}: An error occured while processing {1}"
                        .format(self.name, str(item)[:50])
                    )
                    formatted = traceback.format_exc(chain=False)
                    self.logger.error("{0}: {1}".format(self.name, formatted))
                    self.output.put((e, None))
                    return  # Exits without polluting stderr

        except Empty:
            self.logger.info("{0}: No more items to process".format(self.name))
            self.logger.info("\n" + "\n".join(self.format_stats()))

    def format_stats(self):
        for path, outputs, duration in self.stats:
            yield "{0}: - Extracted {1} values from {2} in {3} seconds" \
                  .format(self.name, outputs, path, duration)


class QueueLogger(Thread):

    def __init__(self, logger=None):
        super().__init__(daemon=True)
        self.queue = Queue()

    def debug(self, message):
        self.queue.put((logging.DEBUG, message))

    def info(self, message):
        self.queue.put((logging.INFO, message))

    def warning(self, message):
        self.queue.put((logging.WARNING, message))

    def error(self, message):
        self.queue.put((logging.ERROR, message))

    def run(self):
        while True:
            try:
                level, message = self.queue.get(timeout=OUTPUT_QUEUE_TIMEOUT)
                logger.log(level, message)
            except Empty:
                continue
