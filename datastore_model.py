import sys

# Required for unit testing purposes
sys.path = sys.path + ['/usr/local/google_appengine', '/usr/local/google_appengine/lib/yaml/lib', '/usr/local/google_appengine/google/appengine']

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class CommentData(db.Model):
    """Comments submitted by users"""
    name = db.StringProperty()
    email = db.StringProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    notify = db.BooleanProperty()
    comments = db.StringProperty(multiline=True)
    file = db.BlobProperty()


class LogData(db.Model):
    """Root entry created for a new file upload"""
    user = db.UserProperty(auto_current_user_add=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    filename = db.StringProperty()
    notes = db.StringProperty()


class GraphModel(db.Model):
    """Model used to store details of graph datasets already 
    generated and therefore present in blob store

    Child entity of LogData
    """
    #name = db.StringProperty()
    graph_type = db.IntegerProperty()
    blob_key = blobstore.BlobReferenceProperty()


"""Classes providing datastore mappings from internal representation 
of GC related objects.

We use the polymodel class to provide a superclass data model definition 
"""
class GCModel(polymodel.PolyModel):
    collector = db.StringProperty(required=True)
    timestamp = db.FloatProperty(required=True)


class YoungGenGCModel(GCModel):
    """Young generation GC entry

    Child entity of LogData
    """
    gc_timestamp = db.FloatProperty()
    yg_util_pre = db.IntegerProperty()
    yg_util_post = db.IntegerProperty()
    yg_size_post = db.IntegerProperty()
    yg_pause_time = db.FloatProperty()
    heap_util_pre = db.IntegerProperty()
    heap_util_post = db.IntegerProperty()
    heap_size_post = db.IntegerProperty()
    pause_time = db.FloatProperty()
    user_time = db.FloatProperty()
    sys_time = db.FloatProperty()
    real_time = db.FloatProperty()


class FullGCModel(GCModel):
    """Full GC entry

    Child entity of LogData
    """
    gc_timestamp = db.FloatProperty()
    tenured_util_pre = db.IntegerProperty()
    tenured_util_post = db.IntegerProperty()
    tenured_size_post = db.IntegerProperty()
    tenured_pause_time = db.FloatProperty()
    heap_util_pre = db.IntegerProperty()
    heap_util_post = db.IntegerProperty()
    heap_size_post = db.IntegerProperty()
    perm_util_pre = db.IntegerProperty()
    perm_util_post = db.IntegerProperty()
    perm_size_post = db.IntegerProperty()
    pause_time = db.FloatProperty()
    user_time = db.FloatProperty()
    sys_time = db.FloatProperty()
    real_time = db.FloatProperty()
    system = db.BooleanProperty()
