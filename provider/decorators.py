from functools import wraps

from flask import (
    g,
    flash,
    redirect,
    request,
    url_for,
)


def login_required(f):
    ''' If the user has not been logged in this will redirect them to login. '''

    # TODO - make sure the url is correctly escaped and the redirect from
    # authorization works correctly.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash(u'You need to be signed in for this page.')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function
