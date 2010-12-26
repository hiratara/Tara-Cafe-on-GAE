from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
import model

class CleanMembers(webapp.RequestHandler):
    def get(self):
        model.Member.clean_members()
        self.response.out.write("Deleted.\n")

application = webapp.WSGIApplication([
    ('/tasks/clean_members', CleanMembers),
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
