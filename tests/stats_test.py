import unittest

import stats

from parsegc import FullGCEntry, YoungGenGCEntry
from stats import IntStats, FloatStats, SummaryStats

class StatsTest(unittest.TestCase):
    def test_intstats(self):
        values = [10, 99, 1, 2, 3, 4, 5]

        stats = IntStats()

        for entry in values:
            stats.process(entry)

        self.assertEqual(stats.count, len(values))
        self.assertEquals(stats.min, 1)
        self.assertEquals(stats.max, 99)
        self.assertEquals(stats.first, 10)
        self.assertEquals(stats.last, 5)
        self.assertEquals(stats.total, 124)
        self.assertEquals(stats.average, sum(values) / len(values))

    def test_intstats2(self):
        values = [-10, -99, 1, 2, 3, 4, 0, 5]

        stats = IntStats()

        for entry in values:
            stats.process(entry)

        self.assertEqual(stats.count, len(values))
        self.assertEquals(stats.min, -99)
        self.assertEquals(stats.max, 5)
        self.assertEquals(stats.first, -10)
        self.assertEquals(stats.last, 5)
        self.assertEquals(stats.total, -94)
        # You loose precision calculating moving average with integer values
        self.assertEquals(stats.average, -14)

    def test_floatstats(self):
        values = [10.0, 99.0, 1.0, 2.0, 3.0, 4.0, 5.0]

        stats = IntStats()

        for entry in values:
            stats.process(entry)

        self.assertEqual(stats.count, len(values))
        self.assertEquals(stats.min, 1.0)
        self.assertEquals(stats.max, 99.0)
        self.assertEquals(stats.first, 10.0)
        self.assertEquals(stats.last, 5.0)
        self.assertEquals(stats.total, 124.0)
        self.assertEquals(stats.average, sum(values) / len(values))

    def test_floatstats2(self):
        values = [-10.0, -99.0, 1.0, 2.0, 3.0, 4.0, 0.0, 5.0]

        stats = IntStats()

        for entry in values:
            stats.process(entry)

        self.assertEquals(stats.count, len(values))
        self.assertEquals(stats.min, -99.0)
        self.assertEquals(stats.max, 5.0)
        self.assertEquals(stats.first, -10.0)
        self.assertEquals(stats.last, 5.0)
        self.assertEquals(stats.total, -94.0)
        self.assertEquals(stats.average, sum(values) / len(values))

    def test_int_bytes_human_readable(self):
        self.assertEquals(stats.int_bytes_human_readable(0),  "0 B")
        self.assertEquals(stats.int_bytes_human_readable(1),  "1 B")
        self.assertEquals(stats.int_bytes_human_readable(1 << 10),  "1 KB")
        self.assertEquals(stats.int_bytes_human_readable(1 << 20),  "1 MB")
        self.assertEquals(stats.int_bytes_human_readable(1 << 30),  "1 GB")
        self.assertEquals(stats.int_bytes_human_readable(1 << 40),  "1 TB")
        self.assertEquals(stats.int_bytes_human_readable(1 << 50),  "1024 TB")
        self.assertEquals(stats.int_bytes_human_readable(1 << 64),  "16777216 TB")

    def test_float_bytes_human_readable(self):
        self.assertEquals(stats.float_bytes_human_readable(0),  "0.00 B")
        self.assertEquals(stats.float_bytes_human_readable(1),  "1.00 B")
        self.assertEquals(stats.float_bytes_human_readable(1 << 10),  "1.00 KB")
        self.assertEquals(stats.float_bytes_human_readable(1 << 20),  "1.00 MB")
        self.assertEquals(stats.float_bytes_human_readable(1 << 30),  "1.00 GB")
        self.assertEquals(stats.float_bytes_human_readable(1 << 40),  "1.00 TB")
        self.assertEquals(stats.float_bytes_human_readable(1 << 50),  "1024.00 TB")
        self.assertEquals(stats.float_bytes_human_readable(1 << 64),  "16777216.00 TB")

    def test_generate_stats(self):
        """Test the generation of stats result set"""

        yg_gc1 = YoungGenGCEntry(
            "50.0",
            "50.0",
            "ParNew",
            "2",
            "1",
            "4",
            "0.12345",
            "2048",
            "1024",
            "4096",
            "2.12345",
            "1.0",
            "1.50",
            "2.1")

        yg_gc2 = YoungGenGCEntry(
            "100.25",
            "100.25",
            "ParNew",
            "3",
            "2",
            "8",
            "0.12345",
            "8192",
            "5120",
            "16384",
            "3.12345",
            "1.5",
            "2.0",
            "3.1")

        full_gc = FullGCEntry(
            "200.5",
            "200.5",
            "Tenured",
            "20",
            "10",
            "40",
            "0.23456",
            "8192",
            "5120",
            "16384",
            "200",
            "100",
            "400",
            "3.1234",
            "1.9",
            "0.05",
            "3.11")

        system_gc = FullGCEntry(
            "250.75",
            "250.75",
            "Tenured",
            "30",
            "20",
            "80",
            "0.23456",
            "8192",
            "4096",
            "8192",
            "300",
            "200",
            "800",
            "4.0912",
            "1.98",
            "2.1",
            "4.09",
            "System")

        gc_data = [yg_gc1, yg_gc2, full_gc, system_gc]
        results = SummaryStats(gc_data).stats
        
        expected = {}
        expected['Total Events'] = len(gc_data)
        expected['Elapsed Time'] = '200.750  secs'
        expected['Time spent in Full GC'] = '7.215  secs'
        expected['Time spent in YG GC'] = '5.247  secs'
        expected['Heap Start / End (Peak)'] = '4 MB / 8 MB (16 MB)'
        expected['YG Start / End (Peak)'] = '4 KB / 8 KB (8 KB)'
        expected['Tenured Start / End (Peak)'] = '40 KB / 80 KB (80 KB)'
        expected['Perm Start / End (Peak)'] = '400 KB / 800 KB (800 KB)'
        expected['Heap Growth'] = '4 MB'
        expected['YG Growth'] = '4 KB'
        expected['Tenured Growth'] = '40 KB'
        expected['Perm Growth'] = '400 KB'
        expected['Avg YG Reclaimed'] = '1 KB'
        expected['Avg Tenured Reclaimed'] = '10 KB'

        self.assertEquals(results, expected)
