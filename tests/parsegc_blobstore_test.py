import filecmp
import os
import shutil
import sys
import unittest

import graph

# Required for unit testing purposes
sys.path = sys.path + ['/usr/local/google_appengine', '/usr/local/google_appengine/lib/yaml/lib', '/usr/local/google_appengine/google/appengine']
from google.appengine.ext import blobstore
from google.appengine.api.blobstore import blobstore_stub, file_blob_storage
from google.appengine.api.files import file_service_stub
from google.appengine.api import datastore_file_stub
from google.appengine.ext import db
from google.appengine.ext import testbed

from csvwriter import BlobResultWriter
from datastore_model import LogData
from parsegc import ParseGCLog


class TestbedWithFiles(testbed.Testbed):
    """Custom implementation of init_blobstore_stub which allows reading and 
    writing to blobstore in unit tests
    """
    def init_blobstore_stub(self, blobstore_dir):
        blob_storage = file_blob_storage.FileBlobStorage(blobstore_dir,
                                                testbed.DEFAULT_APP_ID)
        blob_stub = blobstore_stub.BlobstoreServiceStub(blob_storage)
        file_stub = file_service_stub.FileServiceStub(blob_storage)
        # Not used in these tests
        datastore_stub = datastore_file_stub.DatastoreFileStub(
            testbed.DEFAULT_APP_ID, '/dev/null', '/')
        self._register_stub('blobstore', blob_stub)
        self._register_stub('file', file_stub)
        self._register_stub('datastore_v3', datastore_stub)


class ParseGCBlobTest(unittest.TestCase):

    path = os.path.dirname(os.path.abspath(__file__)) + "/"
    blobstore_dir = path + "testbed.blobstore"
    sample_file = path + "gc-sample.log"

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = TestbedWithFiles()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_blobstore_stub(self.blobstore_dir)

        self.parser = ParseGCLog()
        self.csv_writer = BlobResultWriter()

    def tearDown(self):
        self.testbed.deactivate()
        if os.path.isdir(self.blobstore_dir):
            shutil.rmtree(self.blobstore_dir)

    def _load_file_data(self, filename):
        file = open(filename, 'r')
        data = file.read()
        file.close()
        return data

    def _load_blob_data(self, blob_key):
        blob_info = blobstore.BlobInfo.get(blob_key)
        blob_reader = blob_info.open()
        data = blob_reader.read()
        blob_reader.close()
        return data

    def test_generate_memory_csv(self):
        expected_data = self._load_file_data(self.path + "expected_mem.csv")
        gc_data = self.parser.parse_file(self.sample_file)
        log_key = LogData(
            filename="memory.tmp",
            notes="notes").put()
        blob_key = graph.generate_cached_graph(log_key, 
            graph.YG_GC_MEMORY, 
            gc_data, 
            self.csv_writer)
        result_data = self._load_blob_data(blob_key)
        self.assertTrue(result_data, expected_data)

    def test_generate_gc_reclaimed_csv(self):
        expected_data = self._load_file_data(self.path + "expected_reclaimed.csv")
        gc_data = self.parser.parse_file(self.sample_file)
        log_key = LogData(
            filename="reclaimed.tmp",
            notes="notes").put()
        blob_key = graph.generate_cached_graph(log_key, 
            graph.MEMORY_RECLAIMED, 
            gc_data, 
            self.csv_writer)
        result_data = self._load_blob_data(blob_key)
        self.assertTrue(result_data, expected_data)

    def test_generate_gc_duration_csv(self):
        expected_data = self._load_file_data(self.path + "expected_duration.csv")
        gc_data = self.parser.parse_file(self.sample_file)
        log_key = LogData(
            filename="duration.tmp",
            notes="notes").put()
        blob_key = graph.generate_cached_graph(log_key, 
            graph.GC_DURATION, 
            gc_data, 
            self.csv_writer)
        result_data = self._load_blob_data(blob_key)
        self.assertTrue(result_data, expected_data)