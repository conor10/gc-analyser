import unittest

from parsegc import ParseGCLog, YoungGenGCEntry, FullGCEntry
# TODO
# 1. Full GC support
# 2. Mangled old MSC entries (see TODOs below)
# 3. Failure schenarios
# 4. CMS stage parsing
# 5. G1 log parsing


# Serial - young Copy, old MarkSweepCompact
SERIAL_YG1 = "1.321: [GC 1.321: [DefNew: 80256K->9984K(90240K), 0.2542700 secs] 200471K->200470K(290600K), 0.2543095 secs] [Times: user=0.22 sys=0.04, real=0.26 secs]"
# TODO Test
SERIAL_YG2 = "1.638: [GC 1.638: [DefNew: 90240K->9984K(90240K), 0.2338166 secs]1.872: [Tenured: 270741K->270823K(270824K), 0.6977344 secs] 280726K->280725K(361064K), [Perm : 4575K->4575K(21248K)], 0.9328023 secs] [Times: user=0.88 sys=0.04, real=0.93 secs] "
SERIAL_FULL = "26.256: [Full GC 26.256: [Tenured: 349568K->349568K(349568K), 1.3431030 secs] 506815K->506815K(506816K), [Perm : 4607K->4607K(21248K)], 1.3431456 secs] [Times: user=1.31 sys=0.03, real=1.34 secs] "

# Young ParNew, old MarkSweepCompact
# TODO Test
PARNEW_MSC_YG1 = "0.799: [GC 0.799: [ParNew: 17472K->2176K(19648K), 0.0545699 secs]0.853: [Tenured: 53682K->53696K(53696K), 0.1359657 secs] 56534K->55849K(73344K), [Perm : 4572K->4572K(21248K)], 0.1912721 secs] [Times: user=0.25 sys=0.02, real=0.19 secs] "
PARNEW_MSC_YG2 = "1.025: [GC 1.025: [ParNew: 35840K->4480K(40320K), 0.0930836 secs] 89536K->88976K(129816K), 0.0931276 secs] [Times: user=0.25 sys=0.03, real=0.10 secs] "
PARNEW_MSC_FULL = "32.438: [Full GC 32.438: [Tenured: 349567K->349567K(349568K), 1.6792855 secs] 506815K->506815K(506816K), [Perm : 4574K->4574K(21248K)], 1.6793288 secs] [Times: user=1.62 sys=0.05, real=1.68 secs] "

# Young ParNew, old ConcurrentMarkSweep
PARNEW_CMS_YG1 = "2.225: [GC 2.225: [ParNew: 19134K->2110K(19136K), 0.0619736 secs] 395443K->395442K(412864K), 0.0620169 secs] [Times: user=0.21 sys=0.01, real=0.06 secs] "
PARNEW_CMS_FULL_FAIL = ("8.622: [Full GC 8.622: [CMS9.380: [CMS-concurrent-mark: 0.898/0.898 secs] [Times: user=1.01 sys=0.02, real=0.89 secs] "
                        "\n(concurrent mode failure): 458751K->458751K(458752K), 4.1504959 secs] 517759K->516889K(517760K), [CMS Perm : 4619K->4619K(21248K)], 4.2218320 secs] [Times: user=3.17 sys=0.12, real=4.22 secs] ")
PARNEW_CMS_FULL = "12.850: [Full GC 12.850: [CMS: 458751K->458751K(458752K), 2.2371750 secs] 517759K->517722K(517760K), [CMS Perm : 4619K->4609K(21248K)], 2.2372395 secs] [Times: user=2.17 sys=0.05, real=2.23 secs] "
# TODO: Add other stages of CMS

# Young Copy, old ConcurrentMarkSweep
COPY_CMS_YG1 = "1.438: [GC 1.438: [DefNew: 19136K->2111K(19136K), 0.1023744 secs] 191163K->191162K(208192K), 0.1024165 secs] [Times: user=0.10 sys=0.01, real=0.10 secs] "
COPY_CMS_FULL_FAIL = ("11.518: [Full GC 11.518: [CMS12.374: [CMS-concurrent-mark: 0.856/0.856 secs] [Times: user=0.85 sys=0.00, real=0.85 secs] "
                        "\n(concurrent mode failure): 503040K->503040K(503040K), 3.2780906 secs] 522175K->522138K(522176K), [CMS Perm : 4619K->4609K(21248K)], 3.2781452 secs] [Times: user=3.21 sys=0.06, real=3.28 secs] ")
COPY_CMS_FULL = "6.497: [Full GC 6.497: [CMS: 503039K->503040K(503040K), 4.9805391 secs] 522175K->522156K(522176K), [CMS Perm : 4619K->4619K(21248K)], 4.9934847 secs] [Times: user=2.45 sys=0.21, real=4.99 secs] "
# TODO: Add other stages of CMS

# Young Parallel Scavange, old Parallell Scavange MarkSweep, with adaptive sizing
PARALLEL_MARKSWEEP_ADAPTIVE_YG1 = "4.607: [GC [PSYoungGen: 83708K->58240K(116480K)] 351227K->351398K(466048K), 0.2748461 secs] [Times: user=0.93 sys=0.04, real=0.27 secs] "
PARALLEL_MARKSWEEP_ADAPTIVE_FULL = "5.257: [Full GC [PSYoungGen: 116480K->58237K(116480K)] [ParOldGen: 349566K->349567K(349568K)] 466046K->407805K(466048K) [PSPermGen: 4574K->4574K(21248K)], 1.8929788 secs] [Times: user=6.03 sys=0.17, real=1.89 secs] "

# Young Parallel Scavange, old Parallell Scavange MarkSweep, without adaptive sizing
PARALLEL_MARKSWEEP_NON_ADAPTIVE_YG1 = "0.285: [GC [PSYoungGen: 16448K->2688K(19136K)] 55510K->54822K(71296K), 0.0370065 secs] [Times: user=0.13 sys=0.01, real=0.03 secs] "
PARALLEL_MARKSWEEP_NON_ADAPTIVE_FULL = "0.322: [Full GC [PSYoungGen: 2688K->2581K(19136K)] [ParOldGen: 52134K->52156K(52160K)] 54822K->54738K(71296K) [PSPermGen: 4572K->4570K(21248K)], 0.1916334 secs] [Times: user=0.54 sys=0.02, real=0.20 secs] "


# Original test entries
SERIAL_ENTRY1 = "47.100: [GC 47.100: [DefNew: 25472K->1143K(25472K), 0.0103151 secs] 66774K->45257K(81968K), 0.0103716 secs] [Times: user=0.01 sys=0.00, real=0.01 secs] "
PARALLEL_ENTRY1 = "2.590: [GC [PSYoungGen: 32768K->26736K(57344K)] 82018K->75986K(140416K), 0.0292595 secs] [Times: user=0.08 sys=0.02, real=0.03 secs] "
PAR_NEW_ENTRY1 = "29.063: [GC 29.063: [ParNew: 471872K->50601K(471872K), 0.1122560 secs] 2294220K->1911156K(4141888K), 0.1127720 secs] [Times: user=2.47 sys=0.09, real=0.12 secs] "
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

CMS_FAILURE = "468.231: [GC 468.232: [ParNew (promotion failed): 471872K->471872K(471872K), 2.5078250 secs]470.739: [CMS470.911: [CMS-concurrent-preclean: 0.267/2.848 secs] [Times: user=16.20 sys=1.00, real=2.85 secs] \n(concurrent mode failure): 3648615K->2923567K(3670016K), 11.9928180 secs] 4105030K->2923567K(4141888K), [CMS Perm : 39717K->39712K(66504K)], 14.5012470 secs] [Times: user=24.53 sys=0.63, real=14.50 secs]"

class ParseGCTest(unittest.TestCase):
    """GC entry parsing test cases"""
    
    def setUp(self):
        self.parser = ParseGCLog()

    def test_yg_copy_old_msc_parse(self):
        """Single threaded YG copy collector with serial garbage collector

        -XX:+UseSerialGC
        """
        result = self.parser.parse(SERIAL_ENTRY1)
        expected = YoungGenGCEntry(
            "47.100",
            "47.100",
            "DefNew",
            "25472",
            "1143",
            "25472", 
            "0.0103151",
            "66774",
            "45257",
            "81968",
            "0.0103716",
            "0.01",
            "0.00", 
            "0.01")
        self.assertEqual(result, expected)

        yg_result2 = self.parser.parse(SERIAL_YG1)
        yg_expected2 = YoungGenGCEntry(
            "1.321",
            "1.321",
            "DefNew",
            "80256",
            "9984",
            "90240",
            "0.2542700",
            "200471",
            "200470",
            "290600",
            "0.2543095",
            "0.22",
            "0.04",
            "0.26")
        self.assertEqual(yg_result2, yg_expected2)

        # TODO SERIAL_YG2 entry

        full_result = self.parser.parse(SERIAL_FULL)
        full_expected = FullGCEntry(
            "26.256",
            "26.256",
            "Tenured",
            "349568",
            "349568",
            "349568",
            "1.3431030",
            "506815",
            "506815",
            "506816",
            "4607",
            "4607",
            "21248",
            "1.3431456",
            "1.31",
            "0.03",
            "1.34")
        self.assertEqual(full_result, full_expected)


    def test_young_ps_old_ps_parse(self):
        """Multi-threaded YG collector with throughput collector

        -XX:+UseParallelGC, auto-enabled with -XX:+UseParallelOldGC
        """
        result = self.parser.parse(PARALLEL_ENTRY1)
        expected = YoungGenGCEntry(
            "2.590",
            None,
            "PSYoungGen",
            "32768",
            "26736",
            "57344",
            None,
            "82018",
            "75986",
            "140416", 
            "0.0292595",
            "0.08",
            "0.02",
            "0.03")
        self.assertEqual(result, expected)


    def test_yg_parnew_old_msc_parse(self):
        """Multi-threaded YG collector with old MarkSweepCompact collector

        -XX:+UseParNewGC
        """
        yg_result = self.parser.parse(PARNEW_MSC_YG2)
        yg_expected = YoungGenGCEntry(
            "1.025",
            "1.025",
            "ParNew",
            "35840",
            "4480",
            "40320",
            "0.0930836",
            "89536",
            "88976",
            "129816",
            "0.0931276",
            "0.25",
            "0.03",
            "0.10")
        self.assertEqual(yg_result, yg_expected)

        full_result = self.parser.parse(PARNEW_MSC_FULL)
        full_expected = FullGCEntry(
           "32.438",
           "32.438",
           "Tenured",
           "349567",
           "349567",
           "349568",
           "1.6792855",
           "506815",
           "506815",
           "506816",
           "4574",
           "4574",
           "21248",
           "1.6793288",
           "1.62",
           "0.05",
           "1.68")
        self.assertEqual(full_result, full_expected)


    def test_yg_parnew_old_cms_parse(self):
        """Multi-threaded YG collector with concurrent old generation 
        collector (CMS)

        -XX:+UseParNewGC, auto-enabled with -XX:+UseConcMarkSweepGC 
        """
        result = self.parser.parse(PAR_NEW_ENTRY1)
        expected = YoungGenGCEntry(
            "29.063",
            "29.063",
            "ParNew",
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

        yg_result = self.parser.parse(PARNEW_CMS_YG1)
        yg_expected = YoungGenGCEntry(
            "2.225",
            "2.225",
            "ParNew",
            "19134",
            "2110",
            "19136",
            "0.0619736",
            "395443",
            "395442",
            "412864",
            "0.0620169",
            "0.21",
            "0.01",
            "0.06")
        self.assertEqual(yg_result, yg_expected)

        full_result = self.parser.parse(PARNEW_CMS_FULL)
        full_expected = FullGCEntry(
        "12.850",
        "12.850",
        "CMS",
        "458751",
        "458751",
        "458752",
        "2.2371750",
        "517759",
        "517722",
        "517760",
        "4619",
        "4609",
        "21248",
        "2.2372395",
        "2.17",
        "0.05",
        "2.23")
        self.assertEqual(full_result, full_expected)
        


    def test_yg_copy_old_cms(self):
        """Young copy collector with old ConcurrentMarkSweep

        -XX:+UseConcMarkSweepGC -XX:-UseParNewGC
        """
        yg_result = self.parser.parse(COPY_CMS_YG1)
        yg_expected = YoungGenGCEntry(
            "1.438",
            "1.438",
            "DefNew",
            "19136",
            "2111",
            "19136",
            "0.1023744",
            "191163",
            "191162",
            "208192",
            "0.1024165",
            "0.10",
            "0.01",
            "0.10")
        self.assertEqual(yg_result, yg_expected)

        full_result = self.parser.parse(COPY_CMS_FULL)
        full_expected = FullGCEntry(
            "6.497",
            "6.497",
            "CMS",
            "503039",
            "503040",
            "503040",
            "4.9805391",
            "522175",
            "522156",
            "522176",
            "4619",
            "4619",
            "21248",
            "4.9934847",
            "2.45",
            "0.21",
            "4.99")
        self.assertEqual(full_result, full_expected)


    def test_young_ps_old_ps(self):
        """Young ParallelScavenge with old ParallelScavenge MarkSweep

        -XX:+UseParallelGC -XX:+UseParallelOldGC, turn adaptive sizeing on/off with -XX:+UseAdaptiveSizePolicy
        """
        result = self.parser.parse(PARALLEL_MARKSWEEP_ADAPTIVE_YG1)
        expected = YoungGenGCEntry(
            "4.607",
            None,
            "PSYoungGen",
            "83708",
            "58240",
            "116480",
            None,
            "351227",
            "351398",
            "466048",
            "0.2748461",
            "0.93",
            "0.04",
            "0.27")
        self.assertEqual(result, expected)

        result2 = self.parser.parse(PARALLEL_MARKSWEEP_NON_ADAPTIVE_YG1)
        expected2 = YoungGenGCEntry(
            "0.285",
            None,
            "PSYoungGen",
            "16448",
            "2688",
            "19136",
            None,
            "55510",
            "54822",
            "71296",
            "0.0370065",
            "0.13",
            "0.01",
            "0.03")
        self.assertEqual(result2, expected2)

        # TODO
        #PARALLEL_MARKSWEEP_ADAPTIVE_FULL
        #PARALLEL_MARKSWEEP_NON_ADAPTIVE_FULL


    def test_invalid_entry(self):
        result = self.parser.parse(CMS_INITIAL_MARK)
        self.assertIsNone(result)


