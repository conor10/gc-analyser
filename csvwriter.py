import csv
import sys

# Required for unit testing purposes
sys.path = sys.path + ['/usr/local/google_appengine', '/usr/local/google_appengine/lib/yaml/lib', '/usr/local/google_appengine/google/appengine']
from google.appengine.api import files

class CSVResultWriter(object):
    
    def write_csv_data(self, gcdata, time_series, custom_attr, file):
        # Write our headers
        file.write(time_series + ',' + ','.join(custom_attr.keys()) + '\n')

        # Write our data
        for entry in gcdata:
            file.write(entry.get_attr_value(time_series) + ',' + 
                ','.join(entry.get_attr_values(custom_attr).values()) + '\n')
        
        """Using Python csv_writer library
        attr = gcdata[0].get_attr_keys()
        csv_writer = csv.DictWriter(file, 
                        lineterminator='\n', fieldnames=attr)
        
        csv_writer.writeheader()
        for entry in gcdata:
            csv_writer.writerow(entry.get_attr_values(custom_attr))
        """

    def generate_memory_csv(self, gcdata, filename=None):

        mem_attr = {
            'yg_util_pre': None,
            'yg_util_post': None,
            'yg_size_post': None,
            'heap_util_pre': None,
            'heap_util_post': None,
            'heap_size_post': None
        }

        return self.generate_csv(gcdata, 'timestamp', mem_attr, filename)

    def generate_gc_reclaimed_csv(self, gcdata, filename=None):
        """Size of data reclaimed in YG & heap following GC
        """

        size_attr = {
            'yg_reclaimed': None,
            'heap_reclaimed': None
        }

        return self.generate_csv(gcdata, 'timestamp', size_attr, filename)

    def generate_gc_duration_csv(self, gcdata, filename=None):
        """Duration of GC
        """

        pause_attr = {
            'yg_pause_time': None,
            'pause_time': None
        }

        return self.generate_csv(gcdata, 'timestamp', pause_attr, filename)


class FileResultWriter(CSVResultWriter):
    """Class for writing GC data in CSV format to a regular file
    """
    def generate_csv(self, gcdata, time_series, custom_attr, filename):
        file = open(filename, 'wb')

        self.write_csv_data(gcdata, time_series, custom_attr, file)

        file.close()

        return filename


class BlobResultWriter(CSVResultWriter):
    """Class for writing GC data in CSV format to App Engine Blobstore
    """
    def generate_csv(self, gcdata, time_series, custom_attr, filename):

        # Create the file
        file_name = files.blobstore.create(mime_type='application/octet-stream')

        # Open the file and write to it
        with files.open(file_name, 'a') as f:
             self.write_csv_data(gcdata, time_series, custom_attr, f)

        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)        

        return files.blobstore.get_blob_key(file_name)