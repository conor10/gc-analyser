import sys

from collections import OrderedDict

from parsegc import FullGCEntry, YoungGenGCEntry

class SummaryStats(object):
    """Object for calculating various summary statistics on GC data"""
    def __init__(self, gc_data):

        self.stats = OrderedDict({})

        self.yg_size = IntStats()
        self.heap_size = IntStats()
        self.perm_size = IntStats()
        self.tenured_size = IntStats()
        self.yg_reclaimed = IntStats()
        self.heap_reclaimed = IntStats()
        self.perm_reclaimed = IntStats()
        self.tenured_reclaimed = IntStats()
        self.yg_elapsed_duration = FloatStats()
        self.full_elapsed_duration = FloatStats()
        self.yg_duration = FloatStats()
        self.full_duration = FloatStats()

        self._generate_stats(gc_data)
        self._generate_results(gc_data)


    def _generate_stats(self, gc_data):

        for entry in gc_data:
            self.heap_size.process(entry.heap_size_post)
            self.heap_reclaimed.process(
                entry.heap_util_pre - entry.heap_util_post)

            if isinstance(entry, YoungGenGCEntry):
                self._generate_yg_stats(entry)
            elif isinstance(entry, FullGCEntry):
                self._generate_full_stats(entry)


    def _generate_yg_stats(self, entry):
        """YG GC entry specific stats"""
        self.yg_size.process(entry.yg_size_post)
        self.yg_reclaimed.process(entry.yg_util_pre - entry.yg_util_post)
        self.yg_elapsed_duration.process(entry.real_time)
        self.yg_duration.process(entry.pause_time)


    def _generate_full_stats(self, entry):
        """Full GC entry specific stats"""
        self.perm_size.process(entry.perm_size_post)
        self.tenured_size.process(entry.tenured_size_post)
        self.perm_reclaimed.process(entry.perm_util_pre - entry.perm_util_post)
        self.tenured_reclaimed.process(
            entry.tenured_util_pre - entry.tenured_util_post)
        self.full_elapsed_duration.process(entry.real_time)
        self.full_duration.process(entry.pause_time)


    def _generate_results(self, gc_data):
        """Generate dictionary of results stats"""
        events = len(gc_data)
        self.stats['Total Events'] = events

        self.stats['Elapsed Time'] = "%.3f " % \
            (gc_data[-1].timestamp - gc_data[0].timestamp) + ' secs'

        self.stats['Time spent in Full GC'] = "%.3f " % \
            (self.full_duration.total) + ' secs'
        self.stats['Time spent in YG GC'] = "%.3f " % \
            (self.yg_duration.total) + ' secs'

        self.stats['Heap Start / End (Peak)'] = \
            int_bytes_human_readable(self.heap_size.first) + ' / ' + \
            int_bytes_human_readable(self.heap_size.last) + ' (' + \
            int_bytes_human_readable(self.heap_size.max) + ')'

        self.stats['YG Start / End (Peak)'] = \
            int_bytes_human_readable(self.yg_size.first) + ' / ' + \
            int_bytes_human_readable(self.yg_size.last) + ' (' + \
            int_bytes_human_readable(self.yg_size.max) + ')'
        
        self.stats['Tenured Start / End (Peak)'] = \
            int_bytes_human_readable(self.tenured_size.first) + ' / ' + \
            int_bytes_human_readable(self.tenured_size.last) + ' (' + \
            int_bytes_human_readable(self.tenured_size.max) + ')'

        self.stats['Perm Start / End (Peak)'] = \
            int_bytes_human_readable(self.perm_size.first) + ' / ' + \
            int_bytes_human_readable(self.perm_size.last) + ' (' + \
            int_bytes_human_readable(self.perm_size.max) + ')'

        self.stats['Heap Growth'] = int_bytes_human_readable(
            self.heap_size.last - self.heap_size.first)
        self.stats['YG Growth'] = int_bytes_human_readable(
            self.yg_size.last - self.yg_size.first)
        self.stats['Tenured Growth'] = int_bytes_human_readable(
            self.tenured_size.last - self.tenured_size.first)       
        self.stats['Perm Growth'] = int_bytes_human_readable(
            self.perm_size.last - self.perm_size.first)

        self.stats['Avg YG Reclaimed'] = int_bytes_human_readable(
            self.yg_reclaimed.average)
        self.stats['Avg Tenured Reclaimed'] = int_bytes_human_readable(
            self.tenured_reclaimed.average)


def int_bytes_human_readable(size):
    """Convert integer byte value into human readable form"""
    suffix = ['B','KB','MB','GB','TB']
    index = 0
    while size >= 1024 and index != len(suffix) - 1:
        index += 1
        size >>= 10
    return "%d %s" % (size, suffix[index])


def float_bytes_human_readable(size, precision=2):
    """Convert float byte value into human readable form"""
    suffix = ['B','KB','MB','GB','TB']
    index = 0
    while size >= 1024 and index != len(suffix) - 1:
        index += 1
        size /= 1024.0
    return "%.*f %s" % (precision, size, suffix[index])


class IntStats(object):
    """Object for aggregating and storing integer results"""
    def __init__(self):
        self.count = 0
        self.min = sys.maxint
        self.max = 0
        self.first = 0
        self.last = 0
        self.total = 0
        self.average = 0

    def process(self, value):
        self.count += 1
        if value < self.min:
            self.min = value
        if value > self.max:
            self.max = value
        if self.count == 1:
            self.first = value
        self.last = value
        self.total += value
        # Moving average
        self.average = (value + ((self.count - 1) * self.average))\
            / self.count


class FloatStats(object):
    """Object for aggregating and storing float results"""
    def __init__(self):
        self.count = 0.0
        self.min = sys.float_info.max
        self.max = 0.0
        self.first = 0.0
        self.last = 0.0
        self.total = 0.0
        self.average = 0.0

    def process(self, value):
        self.count += 1.0
        if value < self.min:
            self.min = value
        if value > self.max:
            self.max = value
        if self.count == 1.0:
            self.first = value
        self.last = value
        self.total += value
        # Moving average
        self.average = (value + ((self.count - 1.0) * self.average))\
            / (self.count)