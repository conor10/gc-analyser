import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import cgi
import datetime
import time
import urllib
import webapp2

import gc_datastore
import graph

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers

from csvwriter import BlobResultWriter
from datastore_model import LogData
from parsegc import ParseGCLog
from datastore_model import GraphModel


class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        # We use app.yaml to configure overall authentication
        if not validate_user(user.email()):
            self.redirect(users.create_login_url(self.request.uri))

        template_values = { 
            'user': user,
            'logout': users.create_logout_url("/")
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))
        

class AnalyseLog(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()

        # We use app.yaml to configure overall authentication
        if not validate_user(user.email()):
            self.redirect(users.create_login_url(self.request.uri))

        start = time.time()

        #file = self.request.body_file
        file = self.request.params["gclog"].file

        log_data = LogData(
            filename=self.request.POST["gclog"].filename,
            notes=self.request.get("notes"))
        log_key = log_data.put()

        parser = ParseGCLog()
        gc_results = parser.parse_data(file)

        # persist gc data - too slow at present with large datasets
        gc_datastore.store_data(log_key, gc_results)

        # persist all CSV data we generate to the store so we 
        # won't have to regenerate later
        blob_writer = BlobResultWriter()
        memory_blob_key = graph.generate_cached_graph(log_key, 
            graph.YG_GC_MEMORY, 
            gc_results, 
            blob_writer)

        gc_duration_blob_key = graph.generate_cached_graph(log_key, 
            graph.YG_GC_DURATION, 
            gc_results, 
            blob_writer)
        
        gc_reclaimed_blob_key = graph.generate_cached_graph(log_key, 
            graph.YG_MEMORY_RECLAIMED, 
            gc_results, 
            blob_writer)
        
        duration = time.time() - start

        # Pass the key to our results, as the data will be obtained via a 
        template_values = {
            'user': user,
            'logout': users.create_logout_url("/"),
            'duration': duration,
            'submission_key': log_key,
            'gc_results': gc_results,
            'memory_key': str(memory_blob_key),
            'gc_duration_key': str(gc_duration_blob_key),
            'gc_reclaimed_key': str(gc_reclaimed_blob_key)
        }

        template = jinja_environment.get_template('results.html')
        self.response.out.write(template.render(template_values))


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """Serves up blob requests from store

    These will be in CSV format
    """
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class GraphHandler():
    """Not used yet"""
    def get(self, parent_key, graph_type):

        q = db.GqlQuery("SELECT blob_key FROM GraphModel " +
                    "WHERE parent_key = :1 AND graph_type = :2 " +
                    parent_key, graph_type)

        results = q.get()

        if not results:
            # Generate results
            data_query = db.GqlQuery("SELECT * FROM GCModel " +
                "WHERE parent_key = :1", parent_key)
            results = data_query.get()


def validate_user(user):
    """Temporary function to restrict access to certain domain/users"""
    valid_users = ['conor10@gmail.com']
    valid_domains = ['ecetera.com.au']

    for username in valid_users:
        if user == username:
            return True

    user_domain = user.split('@')
    if len(user_domain) != 2:
        return False

    for domain in valid_domains:
        if user_domain[1] == domain:
            return True

    return False
     

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/analyse', AnalyseLog),
                               ('/serve/([^/]+)?', ServeHandler),
                               ('/graph/[0-9]+', GraphHandler)],
                              debug=True)