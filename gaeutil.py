import Cookie
import datetime
import urllib2

def set_cookie(res, key, val, days=None):
    # Don't use SimpleCookie for old WebOb in GAE
    # Though, it violates RFC2109 :(
    cookies = Cookie.BaseCookie()
    cookies[key] = val
    cookies[key]["path"] = '/'

    if days:
        expires = datetime.datetime.utcnow() + datetime.timedelta(days)
        cookies[key]["expires"] = expires.strftime("%d %b %Y %H:%M:%S GMT")

    for cookie in cookies.itervalues():
        res.headers.add_header('Set-Cookie', cookie.OutputString())

def del_cookie(res, key):
    set_cookie(res, key, "", -1)
