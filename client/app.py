from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_oauthlib.client import OAuth


# Set these once a provider has been created.
CLIENT_ID = 'ADULKYcI4XM2ZLn5pXQftgNRfHK1GyCxjJ4OwZBg'
CLIENT_SECRET = 'uWw8kS5RGjCkXS7BvAuMKlcSVn1ozBtf7dMuszrBrPOI8e91Od'


app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'
oauth = OAuth(app)

remote = oauth.remote_app(
    'remote',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={'scope': 'email'},
    base_url='http://127.0.0.1:5000/api/',
    request_token_url=None,
    access_token_url='http://127.0.0.1:5000/oauth/token',
    authorize_url='http://127.0.0.1:5000/oauth/authorize'
)


@app.route('/')
def index():
    ''' Both login page and once authenticated will be a dashboard. '''

    username = None
    if 'access_token' in session:
        resp = remote.get('me')
        username = resp.data.get('username')

    return render_template('index.html', username=username)


@app.route('/login')
def login():
    ''' Explicit login step.

        Currently there is no way to get a "next" when using this action.
    '''

    # next_url = request.args.get('next') or request.referrer or None
    next_url = None
    return remote.authorize(
        callback=url_for('authorized', next=next_url, _external=True)
    )


@app.route('/logout')
def logout():
    ''' Logout to require re-authentication.

        This makes no attempt to logout on the remote provider.
    '''

    if 'access_token' in session:
        del session['access_token']

    return redirect(url_for('index'))


@app.route('/authorized')
def authorized():
    ''' Handler redirect to once authotization is completed or an error occurs.

        This will have to be set in the "redirect_uri" when creating a client
        on the provider.
    '''

    resp = remote.authorized_response()

    if resp is None:
        context = {
            'error_reason': request.args['error_reason'],
            'error_description': request.args['error_description']
        }
        return render_template('authorized.html', **context)

    session['oauth_response'] = resp
    session['access_token'] = resp.get('access_token', '')
    return redirect(url_for('index'))


@remote.tokengetter
def get_oauth_token():
    ''' If not aotherwise provided when using the remove this will be called.

        As of 2017-01-08
        Oddly enough the oauthlib implies that a string token is valid, but
        when authentication happens it will fail unless the token is provided
        as a dictionaly.

        If a list is provided the first value will be extracted and wrapped in
        a dictionary.
    '''

    access_token = session.get('access_token')
    return {'access_token': access_token}


if __name__ == '__main__':
    import os
    os.environ['DEBUG'] = 'true'
    # Set if testing locally, in production oauth2 depends on valid ssl and
    # the security fails pretty badly if not used over https.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
    app.run(host='localhost', port=8000)
