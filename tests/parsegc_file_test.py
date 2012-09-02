import filecmp
import os
import unittest

import graph

from csvwriter import FileResultWriter
from parsegc import ParseGCLog

class ParseGCLogTest(unittest.TestCase):
    """Test cases for writing parsed GC data to CSV files"""
    
    path = os.path.dirname(os.path.abspath(__file__)) + "/"
    result_file = path + "results.csv"
    sample_file = path + "gc-sample.log"

    def setUp(self):
        self.parser = ParseGCLog()
        self.csv_writer = FileResultWriter()
        
    def tearDown(self):
        if os.path.isfile(self.result_file):
            os.remove(self.result_file)

    def test_parse_file(self):
        result = self.parser.parse_file(self.path + "gc-sample.log")
        self.assertEqual(len(result), 7)

    def test_generate_memory_csv(self):
        expected_file = self.path + "expected_mem.csv"
        result = self.parser.parse_file(self.sample_file)
        graph.generate_graph(None, 
            graph.YG_GC_MEMORY, 
            result, 
            self.csv_writer, 
            False, 
            self.result_file)
        self.assertTrue(filecmp.cmp(self.result_file, expected_file))

    def test_generate_gc_reclaimed_csv(self):
        expected_file = self.path + "expected_reclaimed.csv"
        result = self.parser.parse_file(self.sample_file)
        graph.generate_graph(None, 
            graph.MEMORY_RECLAIMED, 
            result, 
            self.csv_writer, 
            False, 
            self.result_file)
        self.assertTrue(filecmp.cmp(self.result_file, expected_file))
        
    def test_generate_gc_duration_csv(self):
        expected_file = self.path + "expected_duration.csv"
        result = self.parser.parse_file(self.sample_file)
        graph.generate_graph(None, 
            graph.GC_DURATION, 
            result, 
            self.csv_writer, 
            False, 
            self.result_file)
        self.assertTrue(filecmp.cmp(self.result_file, expected_file))