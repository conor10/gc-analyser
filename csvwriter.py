import csv
import sys

# Required for unit testing purposes
sys.path = sys.path + ['/usr/local/google_appengine', '/usr/local/google_appengine/lib/yaml/lib', '/usr/local/google_appengine/google/appengine']
from google.appengine.api import files

from parsegc import YoungGenGCEntry

class CSVResultWriter(object):
    
    """def write_csv_data(self, gcdata, time_series, custom_attr, file, req_type):
        # Write our headers
        file.write(time_series + ',' + ','.join(custom_attr.keys()) + '\n')

        # Write our data
        for entry in gcdata:
            if isinstance(entry, req_type):
                file.write(str(entry.get_attr_value(time_series)) + ',' + 
                    ','.join(map(str, entry.get_attr_values(custom_attr).values())) + 
                    '\n')"""
        
    """Using Python csv_writer library
        attr = gcdata[0].get_attr_keys()
        csv_writer = csv.DictWriter(file, 
                        lineterminator='\n', fieldnames=attr)
        
        csv_writer.writeheader()
        for entry in gcdata:
            csv_writer.writerow(entry.get_attr_values(custom_attr))
        """

    def write_csv_data(self, result_set, file):
        # Write our headers
        file.write(result_set[0].time_series_key + ',' + 
            ','.join(result_set[0].result_attr.keys()) + '\n')

        # Write our data
        for entry in result_set:
            file.write(str(entry.time_series_value) + ',' + 
                ','.join(map(str, entry.result_attr.values())) + '\n')


    def generate_memory_csv(self, gcdata, filename=None):

        mem_attr = {
            'yg_util_pre': None,
            'yg_util_post': None,
            'yg_size_post': None,
            'heap_util_pre': None,
            'heap_util_post': None,
            'heap_size_post': None
        }

        return self.generate_csv(gcdata, 'timestamp', mem_attr, 
            filename, YoungGenGCEntry)

    def generate_gc_reclaimed_csv(self, gcdata, filename=None):
        """Size of data reclaimed in YG & heap following GC
        """

        size_attr = {
            'yg_reclaimed': None,
            'heap_reclaimed': None
        }

        return self.generate_csv(gcdata, 'timestamp', size_attr, 
            filename, YoungGenGCEntry)

    def generate_gc_duration_csv(self, gcdata, filename=None):
        """Duration of GC
        """

        pause_attr = {
            'yg_pause_time': None,
            'pause_time': None
        }

        return self.generate_csv(gcdata, 'timestamp', pause_attr, 
            filename, YoungGenGCEntry)


class FileResultWriter(CSVResultWriter):
    """Class for writing GC data in CSV format to a regular file
    """
    def generate_csv(self, gcdata, filename):
        file = open(filename, 'wb')

        #self.write_csv_data(gcdata, time_series, custom_attr, file, req_type)
        self.write_csv_data(gcdata, file)

        file.close()

        return filename


class BlobResultWriter(CSVResultWriter):
    """Class for writing GC data in CSV format to App Engine Blobstore
    """
    #def generate_csv(self, gcdata, time_series, custom_attr, filename, req_type):
    def generate_csv(self, gcdata, filename=None):

        # Create the file
        file_name = files.blobstore.create(mime_type='application/octet-stream')

        # Open the file and write to it
        with files.open(file_name, 'a') as f:
             #self.write_csv_data(gcdata, time_series, custom_attr, f, req_type)
             self.write_csv_data(gcdata, f)

        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)        

        return files.blobstore.get_blob_key(file_name)