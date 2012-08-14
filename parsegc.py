#!/usr/bin/python

# TODO: Add support for additional GC configs
#       Add parsing support for Full GC events
#       Add support for remaining CMS events if applicable

import re

timestamp = re.compile(r"""
    (\d+\.\d+): (.*)
    """, re.VERBOSE)

"""As there are two types of YG gc entry - those with & those without 
the young gc entry timestamp & the YG pause timestamp, we wrap these  
in non-capturing expressions (?...(<match-group>)...)

This enables these entries to be optional in the below expression.

Additionally the group matches are all named using symbolic groups, 
(?P<group-name>...) to ensure groups are referenced explicitly via 
their symbols & not via their numbered groups which can vary. 
"""
yg_gc_entry = re.compile(r"""
    \s*\[GC\ (?:(?P<gc_ts>\d+\.\d+):\ )?\[(?P<collector>[A-Za-z]+):
    \ (?P<yg_pre>\d+)K->(?P<yg_post>\d+)K\((?P<yg_sz>\d+)K\)(?:,\ (?P<yg_pause>\d+\.\d+)\ secs)?\]
    \s*(?P<heap_pre>\d+)K->(?P<heap_post>\d+)K\((?P<heap_sz>\d+)K\),\ (?P<pause>\d+\.\d+)\ secs\]
    \s*\[Times:\ user=(?P<user>\d+\.\d+)\ sys=(?P<sys>\d+\.\d+),?\ real=(?P<real>\d+\.\d+)\ secs\].*
    """, re.VERBOSE)

full_gc_entry = re.compile(r"""
    \s*\[Full\ GC\ (?:\((?P<system>System)\)\ )?(?:(?P<gc_ts>\d+\.\d+):\ )?
    (?:\[(?P<yg_collector>[A-Za-z]+):\ (?P<yg_pre>\d+)K->(?P<yg_post>\d+)K\((?P<yg_sz>\d+)K\)\]\ )?
    \[(?P<collector>[A-Za-z]+):
    \ (?P<tenured_pre>\d+)K->(?P<tenured_post>\d+)K\((?P<tenured_sz>\d+)K\)(?:,\ (?P<tenured_pause>\d+\.\d+)\ secs)?\]
    \s*(?P<heap_pre>\d+)K->(?P<heap_post>\d+)K\((?P<heap_sz>\d+)K\),?
    \ \[([A-Za-z]+\ )?[A-Za-z]+\ ?:\ (?P<perm_pre>\d+)K->(?P<perm_post>\d+)K\((?P<perm_sz>\d+)K\)\],\ (?P<perm_pause>\d+\.\d+)\ secs\]
    \s*\[Times:\ user=(?P<user>\d+\.\d+)\ sys=(?P<sys>\d+\.\d+),?\ real=(?P<real>\d+\.\d+)\ secs\].*
    """, re.VERBOSE)

cms_entry = re.compile(r"""
    \s*\[.*CMS.*
    """, re.VERBOSE)

cms_initial_mark = re.compile(r"""
    \s*\[GC\ \[1 CMS-initial-mark:
    \ (\d+)K\((\d+)\)\] (\d+)\((\d+)K\),\ (\d+\.\d+)\ secs\]
    \s*\[Times:\ user=(\d+\.\d+)\ sys=(\d+\.\d+),?\ real=(\d+\.\d+)\ secs\].*
    """, re.VERBOSE)

cms_remark = re.compile(r"""
    <Placeholder>
    """, re.VERBOSE)


# TODO Remove ParseGCLog class wrapper around these functions?
class ParseGCLog(object):        

    def parse_file(self, file):
        gclog = open(file, "r")
        return self.parse_data(gclog)
            
    def parse_data(self, data):
        gcdata = []
        gclog = data.readlines()
        for line in gclog:
            result = self.parse(line)
            if result:
                gcdata.append(result)
        return gcdata

    def parse(self, line):
        ts = timestamp.match(line)
        if ts:
            #print "timestamp: " + ts.group(1)
            #print "remaining: " + ts.group(ts.lastindex)
            entry = ts.group(ts.lastindex)
            yg_gc = yg_gc_entry.match(entry)
            if yg_gc:
                #print "gc timestamp: " + gc.group(1)
                #print "younggen util pre: " + gc.group(2)
                #print "younggen util post: " + gc.group(3)
                #print "younggen size post: " + gc.group(4)
                #print "younggen duration:" + gc.group(5)
                #print "heap util pre: " + gc.group(6)
                #print "heap util post: " + gc.group(7)
                #print "heap size post: " + gc.group(8)
                #print "gc duration: " + gc.group(9)
                #print "user: " + gc.group(10)
                #print "sys: " + gc.group(11)
                #print "real: " + gc.group(12)
                #print gc.groups()

                #result = YoungGenGCEntry(ts.group(1), *yg_gc.groups())
                result = YoungGenGCEntry(ts.group(1),
                    yg_gc.group('gc_ts'),
                    yg_gc.group('collector'),
                    yg_gc.group('yg_pre'),
                    yg_gc.group('yg_post'),
                    yg_gc.group('yg_sz'),
                    yg_gc.group('yg_pause'),
                    yg_gc.group('heap_pre'),
                    yg_gc.group('heap_post'),
                    yg_gc.group('heap_sz'),
                    yg_gc.group('pause'),
                    yg_gc.group('user'),
                    yg_gc.group('sys'),
                    yg_gc.group('real'))

                return result

            full_gc = full_gc_entry.match(entry)
            if full_gc:
                result = FullGCEntry(ts.group(1),
                    full_gc.group('gc_ts'),
                    full_gc.group('collector'),
                    full_gc.group('tenured_pre'),
                    full_gc.group('tenured_post'),
                    full_gc.group('tenured_sz'),
                    full_gc.group('tenured_pause'),
                    full_gc.group('heap_pre'),
                    full_gc.group('heap_post'),
                    full_gc.group('heap_sz'),
                    full_gc.group('perm_pre'),
                    full_gc.group('perm_post'),
                    full_gc.group('perm_sz'),
                    full_gc.group('perm_pause'),
                    full_gc.group('user'),
                    full_gc.group('sys'),
                    full_gc.group('real'),
                    full_gc.group('system'))

                return result

            """cms = cms_entry.match(entry)
            if cms:
                initial_mark = cms_initial_mark.match(entry)
                if initial_mark:
                    #
                remark = cms_remark.match(entry)
                if remark:
                    #
            else:    
                #print "Ignoring unsupported GC entry: " + entry
                return None"""
        else:
            #print "Ignoring line: " + line
            return None


class GCEntry(object):

    def __init__(self,
                collector,
                timestamp):
        self.collector = collector
        self.timestamp = float(timestamp)

    def __eq__(self, 
                other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def get_attr(self):
        return self.__dict__

    def get_attr_keys(self):
        return self.__dict__.keys()

    def get_attr_values(self):
        return self.__dict__.values()

    def get_attr_value(self, key):
        return self.__dict__[key]

    def get_attr_values(self, dict):
        for key in dict:
            if key in self.__dict__:
                dict[key] = self.__dict__[key]
        return dict

    # TODO: Check JVM source to confirm 1024 not 1000 should be used
    def to_bytes(self, value):
        return value << 10

class YoungGenGCEntry(GCEntry):

    def __init__(self, 
                timestamp,
                gc_timestamp,
                collector,
                yg_util_pre,
                yg_util_post,
                yg_size_post,
                yg_pause_time,
                heap_util_pre, 
                heap_util_post, 
                heap_size_post, 
                pause_time,
                user_time,
                sys_time,
                real_time):
        super(YoungGenGCEntry, self).__init__(collector, timestamp)
        self.gc_timestamp = float(gc_timestamp or "0")
        self.yg_util_pre = self.to_bytes(int(yg_util_pre))
        self.yg_util_post = self.to_bytes(int(yg_util_post))
        self.yg_size_post = self.to_bytes(int(yg_size_post))
        self.yg_pause_time = float(yg_pause_time or "0")
        self.heap_util_pre = self.to_bytes(int(heap_util_pre))
        self.heap_util_post = self.to_bytes(int(heap_util_post))
        self.heap_size_post = self.to_bytes(int(heap_size_post))
        self.pause_time = float(pause_time)
        self.user_time = float(user_time)
        self.sys_time = float(sys_time)
        self.real_time = float(real_time)
        self.yg_reclaimed = self.yg_util_pre - self.yg_util_post
        self.heap_reclaimed = self.heap_util_pre - self.heap_util_post

class FullGCEntry(GCEntry):
    def __init__(self,
                timestamp,
                gc_timestamp,
                collector,
                tenured_util_pre,
                tenured_util_post,
                tenured_size_post,
                tenured_pause_time,
                heap_util_pre, 
                heap_util_post, 
                heap_size_post,
                perm_util_pre,
                perm_util_post,
                perm_size_post,
                perm_pause_time, 
                user_time,
                sys_time,
                real_time,
                system=None):
        super(FullGCEntry, self).__init__(collector, timestamp)
        self.gc_timestamp = float(gc_timestamp or 0)
        self.tenured_util_pre = self.to_bytes(int(tenured_util_pre))
        self.tenured_util_post = self.to_bytes(int(tenured_util_post))
        self.tenured_size_post = self.to_bytes(int(tenured_size_post))
        self.tenured_pause_time = float(tenured_pause_time or 0)
        self.heap_util_pre = self.to_bytes(int(heap_util_pre))
        self.heap_util_post = self.to_bytes(int(heap_util_post))
        self.heap_size_post = self.to_bytes(int(heap_size_post))
        self.perm_util_pre = self.to_bytes(int(perm_util_pre))
        self.perm_util_post = self.to_bytes(int(perm_util_post))
        self.perm_size_post = self.to_bytes(int(perm_size_post))
        self.perm_pause_time = float(perm_pause_time)
        self.user_time = float(user_time)
        self.sys_time = float(sys_time)
        self.real_time = float(real_time)
        if system:
            self.system = True
        else:
            self.system = system
        self.tenured_reclaimed = self.tenured_util_pre - self.tenured_util_post
        self.heap_reclaimed = self.heap_util_pre - self.heap_util_post
        self.perm_reclaimed = self.perm_util_pre - self.perm_util_post

