from google.appengine.ext import db

from datastore_model import  FullGCModel, YoungGenGCModel
from parsegc import FullGCEntry, YoungGenGCEntry


def get_data(gc_key):
    """Get GC data entries corresponding to key"""
    q = db.GqlQuery("SELECT * FROM GCModel " +
                "WHERE parent_key = :1 ", gc_key)

    results = q.get()

    if not results:
        raise DataStoreException("Invalid parent_key specified: " + gc_key)

    gc_data = []
    for entry in results:
        if isinstance(entry, YoungGenGCModel):
            gc_data.append(_create_yg_entry(entry))
        elif isinstance(entry, FullGCModel):
            gc_data.append(_create_full_entry(entry))
        else:
            raise DataStoreException("Unsupported GC model type" +
                type(entry))

    return gc_data


def store_data(gc_key, gc_data):
    """Persist GC data entries"""
    # Batch model entities for persistence
    yg_results = []
    full_results = []

    for entry in gc_data:
        if isinstance(entry, YoungGenGCEntry):
            yg_results.append(_create_yg_model(gc_key, entry))
        elif isinstance(entry, FullGCEntry):
            full_results.append(_create_full_model(gc_key, entry))
        else:
            raise DataStoreException("Unsupported GC entry type" +
                type(entry))

    db.put(yg_results)
    db.put(full_results)


#TODO: Remove explicit conversions once verified db *Property types are equivalent to 
# primitive types in python

def _create_yg_entry(model):
    """Create YoungGenGCEntry from equivalent model object"""
    return YoungGenGCEntry(
        timestamp=float(entry.timestamp),
        gc_timestamp=float(entry.gc_timestamp),
        collector=entry.collector,
        yg_util_pre=int(entry.yg_util_pre),
        yg_util_post=int(entry.yg_util_post),
        yg_size_post=int(entry.yg_size_post),
        yg_pause_time=float(entry.yg_pause_time),
        heap_util_pre=int(entry.heap_util_pre),
        heap_util_post=int(entry.heap_util_post),
        heap_size_post=int(entry.heap_size_post), 
        pause_time=float(entry.pause_time),
        user_time=float(entry.user_time),
        sys_time=float(entry.sys_time),
        real_time=float(entry.real_time))

def _create_full_entry(model):
    """Create FullGCEntry from equivalent model object"""
    return FullGCEntry(
        timestamp=float(entry.timestamp),
        gc_timestamp=float(entry.gc_timestamp),
        collector=entry.collector,
        tenured_util_pre=int(entry.tenured_util_pre),
        tenured_util_post=int(entry.tenured_util_post),
        tenured_size_post=int(entry.tenured_size_post),
        tenured_pause_time=float(entry.tenured_pause_time),
        heap_util_pre=int(entry.heap_util_pre), 
        heap_util_post=int(entry.heap_util_post), 
        heap_size_post=int(entry.heap_size_post),
        perm_util_pre=int(entry.perm_util_pre),
        perm_util_post=int(entry.perm_util_post),
        perm_size_post=int(entry.perm_size_post),
        perm_pause_time=float(entry.perm_pause_time),
        user_time=float(entry.user_time),
        sys_time=float(entry.sys_time),
        real_time=float(entry.real_time),
        system=bool(entry.system))

def _create_yg_model(gc_key, entry):
    """Create YoungGenGCModel from equivalent entry object"""
    return YoungGenGCModel(
        parent=gc_key,
        timestamp=float(entry.timestamp),
        gc_timestamp=float(entry.gc_timestamp),
        collector=entry.collector,
        yg_util_pre=int(entry.yg_util_pre),
        yg_util_post=int(entry.yg_util_post),
        yg_size_post=int(entry.yg_size_post),
        yg_pause_time=float(entry.yg_pause_time),
        heap_util_pre=int(entry.heap_util_pre),
        heap_util_post=int(entry.heap_util_post),
        heap_size_post=int(entry.heap_size_post), 
        pause_time=float(entry.pause_time),
        user_time=float(entry.user_time),
        sys_time=float(entry.sys_time),
        real_time=float(entry.real_time))

def _create_full_model(gc_key, entry):
    """Create FullGCModel from equivalent entry object"""
    return FullGCModel(
        parent=gc_key,
        timestamp=float(entry.timestamp),
        gc_timestamp=float(entry.gc_timestamp),
        collector=entry.collector,
        tenured_util_pre=int(entry.tenured_util_pre),
        tenured_util_post=int(entry.tenured_util_post),
        tenured_size_post=int(entry.tenured_size_post),
        tenured_pause_time=float(entry.tenured_pause_time),
        heap_util_pre=int(entry.heap_util_pre), 
        heap_util_post=int(entry.heap_util_post), 
        heap_size_post=int(entry.heap_size_post),
        perm_util_pre=int(entry.perm_util_pre),
        perm_util_post=int(entry.perm_util_post),
        perm_size_post=int(entry.perm_size_post),
        perm_pause_time=float(entry.perm_pause_time),
        user_time=float(entry.user_time),
        sys_time=float(entry.sys_time),
        real_time=float(entry.real_time),
        system=bool(entry.system))

class DataStoreException(Exception):
    pass