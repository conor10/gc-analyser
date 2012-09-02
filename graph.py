import abc

from datastore_model import GraphModel
from parsegc import FullGCEntry, YoungGenGCEntry

RAW_CSV_DATA = 0
YG_GC_MEMORY = 1
GC_DURATION = 2
MEMORY_RECLAIMED = 3
FULL_GC_MEMORY = 4
MEMORY_UTIL_POST = 5


def generate_cached_graph(log_key, graph_type, gc_data, blob_writer):
    return generate_graph(log_key, graph_type, gc_data, blob_writer, True)

def generate_graph(log_key, graph_type, gc_data, blob_writer, 
                cache, filename=None):
    try:
        blob_key = _graphs[graph_type](log_key, gc_data, blob_writer, filename)
        if cache:
            GraphModel(parent=log_key,
                graph_type=graph_type,
                blob_key=blob_key).put()
        return blob_key
    except KeyError:
        return "Invalid graph graph_type"

def _raw_csv_data(log_key, gc_data, blob_writer, filename):
    results = []
    for entry in gc_data:
        results.append(GCTSEntry(entry))

    return blob_writer.generate_csv(results, filename)

def _yg_memory(log_key, gc_data, blob_writer, filename):

    results = []
    for entry in gc_data:
        if isinstance(entry, YoungGenGCEntry):
            results.append(YGMemoryUtil(entry))

    return blob_writer.generate_csv(results, filename)

def _full_memory(log_key, gc_data, blob_writer, filename):

    results = []
    for entry in gc_data:
        if isinstance(entry, FullGCEntry):
            results.append(FullMemoryUtil(entry))

    # If we don't have any full GC entries
    if results == []:
        results.append(FullMemoryUtil(None))

    return blob_writer.generate_csv(results, filename)

def _memory_util_post(log_key, gc_data, blob_writer, filename):

    results = []
    for entry in gc_data:
        results.append(MemoryUtilPost(entry))

    return blob_writer.generate_csv(results, filename)


def _duration(log_key, gc_data, blob_writer, filename):

    results = []
    for entry in gc_data:
        results.append(PauseTime(entry))

    return blob_writer.generate_csv(results, filename)


def _memory_reclaimed(log_key, gc_data, blob_writer, filename):

    results = []
    for entry in gc_data:
        #if isinstance(entry, YoungGenGCEntry):
        results.append(Reclaimed(entry))

    return blob_writer.generate_csv(results, filename)


_graphs = {
        RAW_CSV_DATA: _raw_csv_data,
        YG_GC_MEMORY: _yg_memory,
        FULL_GC_MEMORY: _full_memory,
        GC_DURATION: _duration,
        MEMORY_RECLAIMED: _memory_reclaimed,
        MEMORY_UTIL_POST: _memory_util_post
    }


class TimeSeriesEntry(object):
    """Base class used for calculating GC time series result sets.

    Child classes contain logic for determining GC data relevent to 
    generate a particular result set, this may simple be fields, or 
    could include derived results.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, time_series_key, result_attr, gc_entry):
        self.time_series_value = 0
        self.time_series_key = time_series_key
        self.result_attr = result_attr
        if gc_entry:
            self._calc_results(gc_entry)

    def _calc_results(self, gc_entry):
        self.time_series_value = gc_entry.get_attr_value(self.time_series_key)
        self._get_custom_attr(gc_entry)

    @abc.abstractmethod
    def _get_custom_attr(self, gc_entry):
        """Get/calculate custom attribute values for result set"""
        return


class PauseTime(TimeSeriesEntry):
    """Duration of GC pauses"""
    def __init__(self, gc_entry):
        self.pause_attr = {
            'yg_pause_time': None,
            'pause_time': None,
            'tenured_pause_time': None,
        }
        super(PauseTime, self).__init__('timestamp', self.pause_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):
        gc_entry.get_attr_values(self.pause_attr)


class Reclaimed(TimeSeriesEntry):
    """Space reclaimed following partial GC"""
    def __init__(self, gc_entry):
        self.result_attr = {
            'yg_reclaimed': None,
            'heap_reclaimed': None,
            'tenured_reclaimed': None,
            'perm_reclaimed': None
        }
        super(Reclaimed, self).__init__('timestamp', self.result_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):

        self.result_attr['heap_reclaimed'] = \
            gc_entry.heap_util_pre - gc_entry.heap_util_post
        if isinstance(gc_entry, YoungGenGCEntry):
            self.result_attr['yg_reclaimed'] = \
                gc_entry.yg_util_pre - gc_entry.yg_util_post
        elif isinstance(gc_entry, FullGCEntry):
            self.result_attr['tenured_reclaimed'] = \
                gc_entry.tenured_util_pre - gc_entry.tenured_util_post
            self.result_attr['perm_reclaimed'] = \
                gc_entry.perm_util_pre - gc_entry.perm_util_post


class YGMemoryUtil(TimeSeriesEntry):
    """Memory utilisation following partial GC"""
    def __init__(self, gc_entry):
        self.mem_attr = {
            'yg_util_pre': None,
            'yg_util_post': None,
            'yg_size_post': None,
            'heap_util_pre': None,
            'heap_util_post': None,
            'heap_size_post': None
        }
        super(YGMemoryUtil, self).__init__('timestamp', self.mem_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):
        gc_entry.get_attr_values(self.mem_attr)


class FullMemoryUtil(TimeSeriesEntry):
    """Memory utilisation following full GC"""
    def __init__(self, gc_entry):
        self.mem_attr = {
            'tenured_util_pre': None,
            'tenured_util_post': None,
            'tenured_size_post': None,
            'heap_util_pre': None,
            'heap_util_post': None,
            'heap_size_post': None,
            'perm_util_pre': None,
            'perm_util_post': None,
            'perm_size_post': None
        }
        super(FullMemoryUtil, self).__init__('timestamp', self.mem_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):
        gc_entry.get_attr_values(self.mem_attr)


class MemoryUtilPost(TimeSeriesEntry):
    """Memory utilisation breakdown post GC"""
    def __init__(self, gc_entry):
        self.mem_attr = {
            'yg_size_post': None,
            'tenured_size_post': None,
            'perm_size_post': None,
            'heap_size_post': None
        }
        super(MemoryUtilPost, self).__init__('timestamp', self.mem_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):
        gc_entry.get_attr_values(self.mem_attr)


class GCTSEntry(TimeSeriesEntry):
    """Universal GC entry with time series index"""
    def __init__(self, gc_entry):
        self.gc_attr = {
                'gc_timestamp': None,
                'collector': None,
                'yg_util_pre': None,
                'yg_util_post': None,
                'yg_size_post': None,
                'tenured_util_pre': None,
                'tenured_util_post': None,
                'tenured_size_post': None,
                'tenured_pause_time': None,
                'heap_util_pre': None,
                'heap_util_post': None,
                'heap_size_post': None,
                'perm_util_pre': None,
                'perm_util_post': None,
                'perm_size_post': None,
                'pause_time': None,
                'pause_time': None,
                'user_time': None,
                'sys_time': None,
                'real_time': None,
                'system': None
        }
        super(GCTSEntry, self).__init__('timestamp', self.gc_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):
        gc_entry.get_attr_values(self.gc_attr)