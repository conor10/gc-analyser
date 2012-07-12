import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import cgi
import datetime 
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers

from csvwriter import BlobResultWriter
from parsegc import ParseGCLog


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

        file = self.request.body_file

        parser = ParseGCLog()
        blob_writer = BlobResultWriter()
        gc_results = parser.parse_data(file)

        memory_blob_key = blob_writer.generate_memory_csv(gc_results)
        gc_duration_blob_key = blob_writer.generate_gc_duration_csv(gc_results)
        gc_reclaimed_blob_key = blob_writer.generate_gc_reclaimed_csv(gc_results)

        # Pass the key to our results, as the data will be obtained via a 
        template_values = {
            'user': user,
            'logout': users.create_logout_url("/"),
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
                               ('/serve/([^/]+)?', ServeHandler)],
                              debug=True)