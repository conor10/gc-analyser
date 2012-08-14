import abc

from datastore_model import GraphModel
from parsegc import FullGCEntry, YoungGenGCEntry

YG_GC_MEMORY = 1
YG_GC_DURATION = 2
YG_MEMORY_RECLAIMED = 3


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


def _yg_memory(log_key, gc_data, blob_writer, filename):

    results = []
    for entry in gc_data:
        if isinstance(entry, YoungGenGCEntry):
            results.append(MemoryUtil(entry))

    return blob_writer.generate_csv(results, filename)


def _yg_duration(log_key, gc_data, blob_writer, filename):

    results = []
    for entry in gc_data:
        if isinstance(entry, YoungGenGCEntry):
            results.append(PauseTime(entry))

    return blob_writer.generate_csv(results, filename)


def _yg_memory_reclaimed(log_key, gc_data, blob_writer, filename):

    results = []
    for entry in gc_data:
        if isinstance(entry, YoungGenGCEntry):
            results.append(Reclaimed(entry))

    return blob_writer.generate_csv(results, filename)


_graphs = {
        YG_GC_MEMORY: _yg_memory,
        YG_GC_DURATION: _yg_duration,
        YG_MEMORY_RECLAIMED: _yg_memory_reclaimed
    }


class TimeSeriesEntry(object):
    """Base class used for calculating GC result set.

    Child classes contain logic for determining GC data relevent to 
    generate a particular result set, this may simple be fields, or 
    could include derived results
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, time_series_key, result_attr, gc_entry):
        self.time_series_value = 0
        self.time_series_key = time_series_key
        self.result_attr = result_attr
        self._calc_results(gc_entry)

    def _calc_results(self, gc_entry):
        self.time_series_value = gc_entry.get_attr_value(self.time_series_key)
        self._get_custom_attr(gc_entry)

    @abc.abstractmethod
    def _get_custom_attr(self, gc_entry):
        """Get/calculate custom attribute values for result set"""
        return


class PauseTime(TimeSeriesEntry):
    """Duration of partial GC pauses"""
    def __init__(self, gc_entry):
        self.pause_attr = {
            'yg_pause_time': None,
            'pause_time': None
        }
        super(PauseTime, self).__init__('timestamp', self.pause_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):
        gc_entry.get_attr_values(self.pause_attr)


class Reclaimed(TimeSeriesEntry):
    """Space reclaimed following partial GC"""
    def __init__(self, gc_entry):
        self.result_attr = {
            'yg_reclaimed': None,
            'heap_reclaimed': None
        }
        super(Reclaimed, self).__init__('timestamp', self.result_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):
        self.result_attr['yg_reclaimed'] = \
            gc_entry.yg_util_pre - gc_entry.yg_util_post
        self.result_attr['heap_reclaimed'] = \
            gc_entry.heap_util_pre - gc_entry.heap_util_post


class MemoryUtil(TimeSeriesEntry):
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
        super(MemoryUtil, self).__init__('timestamp', self.mem_attr, gc_entry)

    def _get_custom_attr(self, gc_entry):
        gc_entry.get_attr_values(self.mem_attr)