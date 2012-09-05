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
from datastore_model import CommentData
from datastore_model import GraphModel
from stats import SummaryStats


ROOT_PATH = os.path.dirname(__file__)

class MainPage(webapp2.RequestHandler):
    """Generic page request handler"""

    def get(self):
        user = users.get_current_user()

        # We use app.yaml to configure overall authentication
        if not validate_user(user.email()):
            self.redirect(users.create_login_url(self.request.uri))

        path = self.request.path
        temp = 'static/templates' + path + '.html'

        if not os.path.isfile(os.path.join(ROOT_PATH, 
            temp)):
            path = '/index'
            temp = 'static/templates' + path + '.html'

        template_values = { 
            'user': user,
            'logout': users.create_logout_url("/"),
            'name': path
        }

        template = jinja_environment.get_template(temp)
        self.response.out.write(template.render(template_values))


class ContactHandler(webapp2.RequestHandler):
    """Process submitted contact form data"""
    def post(self):
        user = users.get_current_user()

        # We use app.yaml to configure overall authentication
        if not validate_user(user.email()):
            self.redirect(users.create_login_url(self.request.uri))

        template_values = { 
            'user': user,
            'logout': users.create_logout_url("/"),
            'name': '/contact'
        }

        # write comment to the database
        CommentData(
            name=self.request.get("name"),
            email=self.request.get("email"),
            comments=self.request.get("comments"),
            notify=bool(self.request.get("notify", default_value="False")),
            file=self.request.get("gclog") or None).put()

        template = jinja_environment.get_template(
            'static/templates/thanks.html')
        self.response.out.write(template.render(template_values))


class AnalyseLog(webapp2.RequestHandler):
    """Process submitted log file"""
    def post(self):
        user = users.get_current_user()

        # We use app.yaml to configure overall authentication
        if not validate_user(user.email()):
            self.redirect(users.create_login_url(self.request.uri))

        start = time.time()

        #file = self.request.body_file
        file = self.request.params["gclog"].file

        log_key = LogData(
            filename=self.request.POST["gclog"].filename,
            notes=self.request.get("notes")).put()

        parser = ParseGCLog()
        gc_results = parser.parse_data(file)

        if len(gc_results) > 0:

            # Generate summary stats for results page
            summary_stats = SummaryStats(gc_results).stats

            # persist gc data - too slow at present with large datasets
            gc_datastore.store_data(log_key, gc_results)

            # persist all CSV data we generate to the store so we 
            # won't have to regenerate later
            blob_writer = BlobResultWriter()

            results_csv_key = graph.generate_cached_graph(log_key, 
                graph.RAW_CSV_DATA,
                gc_results, 
                blob_writer)

            yg_memory_blob_key = graph.generate_cached_graph(log_key, 
                graph.YG_GC_MEMORY, 
                gc_results, 
                blob_writer)

            full_memory_blob_key = graph.generate_cached_graph(log_key, 
                graph.FULL_GC_MEMORY, 
                gc_results, 
                blob_writer)

            gc_duration_blob_key = graph.generate_cached_graph(log_key, 
                graph.GC_DURATION, 
                gc_results, 
                blob_writer)
            
            gc_reclaimed_blob_key = graph.generate_cached_graph(log_key, 
                graph.MEMORY_RECLAIMED, 
                gc_results, 
                blob_writer)

            memory_util_post_blob_key = graph.generate_cached_graph(log_key, 
                graph.MEMORY_UTIL_POST, 
                gc_results, 
                blob_writer)
            
            duration = time.time() - start

            # Pass the key to our results, as the data will be obtained via a 
            template_values = {
                'user': user,
                'logout': users.create_logout_url("/"),
                'duration': duration,
                'name': '/uploads',
                'results_key': str(results_csv_key),
                'summary_stats': summary_stats,
                'gc_results': gc_results,
                'yg_memory_key': str(yg_memory_blob_key),
                'full_memory_key': str(full_memory_blob_key),
                'gc_duration_key': str(gc_duration_blob_key),
                'gc_reclaimed_key': str(gc_reclaimed_blob_key),
                'memory_util_post_key': str(memory_util_post_blob_key)
            }

            template = jinja_environment.get_template(
                'static/templates/results.html')

        else:
            template_values = {
                'user': user,
                'logout': users.create_logout_url("/")
            }

            template = jinja_environment.get_template(
                'static/templates/error.html')

        self.response.out.write(template.render(template_values))


class ViewUploads(webapp2.RequestHandler):
    """Serves up details of all previous uploads by user"""
    def get(self):
        user = users.get_current_user()

        # We use app.yaml to configure overall authentication
        if not validate_user(user.email()):
            self.redirect(users.create_login_url(self.request.uri))

        q = db.GqlQuery("SELECT * FROM LogData " + 
            "WHERE user = :1", user)

        uploads = q.fetch(None)

        template_values = {
            'user': user,
            'logout': users.create_logout_url("/"),
            'name': '/uploads',
            'uploads': uploads
            }

        template = jinja_environment.get_template(
                'static/templates/uploads.html')

        self.response.out.write(template.render(template_values))


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """Serves up blob requests from store

    These will be in CSV format
    """
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class GetUploadHandler(webapp2.RequestHandler):
    """Serves up previous upload by a user"""

    def get(self):

        user = users.get_current_user()

        # We use app.yaml to configure overall authentication
        if not validate_user(user.email()):
            self.redirect(users.create_login_url(self.request.uri))

        start = time.time()

        key = self.request.get("key")

        gc_data = gc_datastore.get_data(key)
        #need to sort results

        # We regenerate summary stats with each invocation
        summary_stats = SummaryStats(gc_data).stats

        q = db.GqlQuery("SELECT * FROM GraphModel " +
                "WHERE ANCESTOR IS :1 ", key)

        results = q.fetch(6)

        for entry in results:
            if entry.graph_type == graph.RAW_CSV_DATA:
                results_csv_key = str(entry.blob_key.key())
            elif entry.graph_type == graph.YG_GC_MEMORY:
                yg_memory_key = str(entry.blob_key.key())
            elif entry.graph_type == graph.GC_DURATION:
                gc_duration_key = str(entry.blob_key.key())
            elif entry.graph_type == graph.MEMORY_RECLAIMED:
                gc_reclaimed_key = str(entry.blob_key.key())
            elif entry.graph_type == graph.FULL_GC_MEMORY:
                full_memory_key = str(entry.blob_key.key())
            elif entry.graph_type == graph.MEMORY_UTIL_POST:
                memory_util_post_key = str(entry.blob_key.key())

        duration = time.time() - start

        # Pass the key to our results, as the data will be obtained via a 
        template_values = {
            'user': user,
            'logout': users.create_logout_url("/"),
            'name': '/uploads',
            'duration': duration,
            'results_key': results_csv_key,
            'summary_stats': summary_stats,
            'gc_results': gc_data,
            'yg_memory_key': yg_memory_key,
            'full_memory_key': full_memory_key,
            'gc_duration_key': gc_duration_key,
            'gc_reclaimed_key': gc_reclaimed_key,
            'memory_util_post_key': memory_util_post_key
        }

        template = jinja_environment.get_template(
            'static/templates/results.html')
        self.response.out.write(template.render(template_values))


class DeleteUploadHandler(webapp2.RequestHandler):
    """Delete uploaded entry"""
    def get(self):
        user = users.get_current_user()

        # We use app.yaml to configure overall authentication
        if not validate_user(user.email()):
            self.redirect(users.create_login_url(self.request.uri))

        key = self.request.get("key")

        # Ensure user attempting delete is creator of original entry
        q = db.GqlQuery("SELECT * FROM LogData " + 
            "WHERE user = :1 " +
            "AND ANCESTOR is :2", user, key)

        # If result isn't empty perform delete
        if q.count() == 1:
            db.delete(key)

        self.redirect("/uploads")


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
                               ('/uploads', ViewUploads),
                               ('/serve/([^/]+)?', ServeHandler),
                               ('/prev.*', GetUploadHandler),
                               ('/del.*', DeleteUploadHandler),
                               ('/submit-contact', ContactHandler),
                               ('/.*', MainPage)],
                              debug=True)