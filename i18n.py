import gettext

def localize(s):
    return gettext.gettext(s)

def install(domain):
    t = gettext.translation(domain, "locale", ['de'])
    t.install()
