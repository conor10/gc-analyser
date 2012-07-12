import unittest
import filecmp
import os

from csvwriter import FileResultWriter
from parsegc import ParseGCLog, ParNewGCEntry

class ParseGCTest(unittest.TestCase):

    # Our normal GC entry
    GC_ENTRY1 = "29.063: [GC 29.063: [ParNew: 471872K->50601K(471872K), 0.1122560 secs] 2294220K->1911156K(4141888K), 0.1127720 secs] [Times: user=2.47 sys=0.09, real=0.12 secs] "
    # CMS specific GC entries
    CMS_INITIAL_MARK = "29.177: [GC [1 CMS-initial-mark: 1860555K(3670016K)] 1911295K(4141888K), 0.0331270 secs] [Times: user=0.03 sys=0.01, real=0.03 secs] "
    CMS_MARK_START = "29.210: [CMS-concurrent-mark-start]"
    CMS_MARK = "29.683: [CMS-concurrent-mark: 0.313/0.472 secs] [Times: user=13.67 sys=2.81, real=0.47 secs] "
    CMS_PRECLEAN_START = "29.683: [CMS-concurrent-preclean-start]"
    CMS_PRECLEAN = "29.848: [CMS-concurrent-preclean: 0.135/0.165 secs] [Times: user=2.87 sys=0.26, real=0.17 secs] "
    CMS_ABORT_PRECLEAN_START = "29.848: [CMS-concurrent-abortable-preclean-start]"
    CMS_ABORT_PRECLEAN = "30.184: [CMS-concurrent-abortable-preclean: 0.214/0.335 secs] [Times: user=6.13 sys=0.38, real=0.34 secs]"
    YG_OCCUPANCY = "30.185: [GC[YG occupancy: 267358 K (471872 K)]30.185: [Rescan (parallel) , 0.0160950 secs]30.202: [weak refs processing, 0.0000670 secs] [1 CMS-remark: 1961567K(3670016K)] 2228926K(4141888K), 0.0164580 secs] [Times: user=0.75 sys=0.00, real=0.01 secs] "
    CMS_SWEEP_START = "30.202: [CMS-concurrent-sweep-start]"
    CMS_SWEEP = "32.576: [CMS-concurrent-sweep: 1.749/2.374 secs] [Times: user=50.68 sys=4.68, real=2.38 secs]"
    CMS_RESET_START = "32.576: [CMS-concurrent-reset-start]"
    CMS_RESET = "32.651: [CMS-concurrent-reset: 0.029/0.075 secs] [Times: user=1.94 sys=0.13, real=0.07 secs]"


    def setUp(self):
        self.parser = ParseGCLog()

    def test_gc_parse(self):
        result = self.parser.parse(self.GC_ENTRY1)
        expected = ParNewGCEntry(
            "29.063",
            "29.063",
            "471872",
            "50601",
            "471872",
            "0.1122560",
            "2294220",
            "1911156",
            "4141888",
            "0.1127720",
            "2.47",
            "0.09",
            "0.12")
        self.assertEqual(result, expected)

    def test_invalid_entry(self):
        result = self.parser.parse(self.CMS_INITIAL_MARK)
        self.assertIsNone(result)


class ParseGCLogTest(unittest.TestCase):

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

    def test_generate_csv(self):
        expected_file = self.path + "expected_gc.csv"
        result = self.parser.parse_file(self.sample_file)
        self.csv_writer.generate_gc_csv_file(result, self.result_file)
        self.assertTrue(filecmp.cmp(self.result_file, expected_file))

    def test_generate_memory_csv(self):
        expected_file = self.path + "expected_mem.csv"
        result = self.parser.parse_file(self.sample_file)
        self.csv_writer.generate_memory_csv(result, self.result_file)
        self.assertTrue(filecmp.cmp(self.result_file, expected_file))

    def test_generate_gc_reclaimed_csv(self):
        expected_file = self.path + "expected_reclaimed.csv"
        result = self.parser.parse_file(self.sample_file)
        self.csv_writer.generate_gc_reclaimed_csv(result, self.result_file)
        self.assertTrue(filecmp.cmp(self.result_file, expected_file))
        
    def test_generate_gc_duration_csv(self):
        expected_file = self.path + "expected_duration.csv"
        result = self.parser.parse_file(self.sample_file)
        self.csv_writer.generate_gc_duration_csv(result, self.result_file)
        self.assertTrue(filecmp.cmp(self.result_file, expected_file))

