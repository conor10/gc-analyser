import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import cgi
import datetime 
import urllib
import webapp2

from parsegc import ParseGCLog


class MainPage(webapp2.RequestHandler):

    def get(self):

        template_values = { }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))
        

class AnalyseLog(webapp2.RequestHandler):

    def post(self):
        #file = self.request.get("gclog")
        file = self.request.body_file

        parser = ParseGCLog()
        gc_results = parser.parse_data(file)

        template_values = {
            'gc_results': gc_results
        }

        template = jinja_environment.get_template('results.html')
        self.response.out.write(template.render(template_values))


class DisplayResults(webapp2.RequestHandler):

    def get(self):
        template_values = { }

        template = jinja_environment.get_template('results.html')
        self.response.out.write(template.render(template_values))
        

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/analyse', AnalyseLog),
                               ('/results', DisplayResults)],
                              debug=True)