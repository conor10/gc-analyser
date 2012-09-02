import unittest

import stats

from stats import IntStats, FloatStats

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

		self.assertEqual(stats.count, len(values))
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



