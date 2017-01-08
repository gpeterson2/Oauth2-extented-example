''' The way the flaks_oautlib library works is that it provides decorators
    for functions that you provide. Most of the work is actually done in
    these decorators so some implementations actually require very little.

    The tokenhandler is probably the worst offender as it must be defined, but
    the implementation only requires returning "None".
'''

from datetime import datetime, timedelta

from flask import Blueprint, render_template, g, request
from flask_oauthlib.provider import OAuth2Provider

from decorators import login_required
from models import db, Client, Grant, Token

oauth_blueprint = Blueprint('oauth', __name__, url_prefix='/oauth')

oauth = OAuth2Provider()


@oauth.clientgetter
def load_client(client_id):
    ''' Gets a client. '''

    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    ''' Gets a grant. '''

    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    ''' Save a grant. '''

    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=g.user,
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    ''' Get a token whether access or refresh. '''

    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    ''' Saves a token.

        This will delete any other tokens associated with the client once run.
        This means that any existing refresh tokens will be lost and the new
        one is the only refresh that can be used from that point onward. Which
        is a reasonable way to handle things, although technically the length
        a refresh token is valid for is not specified in the spec, so if you
        want longer lived refresh tokens this will have to be modified.
    '''

    toks = Token.query.filter_by(
        client_id=request.client.client_id,
        user_id=request.user.id
    )
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok


@oauth_blueprint.route('/token', methods=['GET', 'POST'])
@oauth.token_handler
def access_token():
    ''' Token handler, this should return an empty dict or None.  '''

    return None


@oauth_blueprint.route('/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
@login_required
def authorize(*args, **kwargs):
    ''' Displays an authorization page.

        The ideas is that on a get this will display a grant page wher the
        user can see what scopes are being required an authorize it.

        Then this will post back with the response which will then return a
        boolean. If True the grant process will continue.

        It is also possible to return redirects from this page, but unless
        the parameters are explicitely passed onward it will not be possible
        to get back here and continue the process without starting fresh.
    '''

    if request.method == 'GET':
        user = g.user
        client_id = kwargs.get('client_id')
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        kwargs['user'] = user
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'
