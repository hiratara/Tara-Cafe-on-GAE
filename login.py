from google.appengine.api import users
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
import gaeutil

__all__ = ['openid_required']

def redirectToForm(handler, original_url):
    gaeutil.set_cookie(
        handler.response, 'original_url', original_url
    )
    handler.redirect("/login")

def openid_required(handler_method):
    u"""The decorator to force to login with OpenID.

        For example:
            import login

            class MainPage(webapp.RequestHandler):
                @login.openid_required
                def get(self): pass

     """
    def check_login(self, *args):
        if users.get_current_user():
            return handler_method(self, *args)

        return redirectToForm(self, self.request.url)

    return check_login

class RedirectToForm(webapp.RequestHandler):
    def get(self):
        return redirectToForm(self, self.request.get("continue"))

class LoginForm(webapp.RequestHandler):
    def get(self):
        self.response.out.write(webapp.template.render(
            'login.html', None
        ))

class LoginPost(webapp.RequestHandler):
    def post(self):
        original_url = gaeutil.get_cookie(self.request, 'original_url')
        gaeutil.del_cookie(self.response, 'original_url')

        self.redirect(
            users.create_login_url(
                original_url,
                federated_identity=self.request.get("open_id"),
                )
            )

application = webapp.WSGIApplication([
    ('/_ah/login_required', RedirectToForm), 
    ('/login', LoginForm), 
    ('/login/post', LoginPost), 
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
