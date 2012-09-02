import csv
import sys

# Required for unit testing purposes
sys.path = sys.path + ['/usr/local/google_appengine', '/usr/local/google_appengine/lib/yaml/lib', '/usr/local/google_appengine/google/appengine']
from google.appengine.api import files

from parsegc import YoungGenGCEntry


xstr = lambda s: '' if s is None else str(s)

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
        """Write csv data indexed by time series"""
        # Write our headers
        file.write(result_set[0].time_series_key + ',' + 
            ','.join(result_set[0].result_attr.keys()) + '\n')

        # Write our data - need to ensure None value is not written as "None"
        for entry in result_set:
            file.write(xstr(entry.time_series_value) + ',' + 
                ','.join(map(xstr, entry.result_attr.values())) + '\n')


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