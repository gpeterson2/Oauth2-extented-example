from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    ''' Simple user model.

        Real name info and a password would be good improvements.
    '''

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)


class Client(db.Model):
    ''' A simple client implementation.  '''

    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.ForeignKey('user.id'))
    user = db.relationship('User')

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        ''' Returns the client type.

            Currently only "public"
        '''

        return 'public'

    @property
    def redirect_uris(self):
        ''' The redirect uris as a list. '''

        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        ''' The default uri.

            This is assumed to be the first uri, although it would be nice
            to allow this to be set.
        '''

        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        ''' Scopes as a list. '''

        if self._default_scopes:
            return self._default_scopes.split()
        return []


class Grant(db.Model):
    ''' A simple grant implementation.

        Ideally all grants will be deleted once used, by calling the "delete"
        function, but this might not be the case if an error occurs. So it
        would not be a bad idea to also implement a batch process that
        occasionally deletes any zombie records.
    '''

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        ''' This is called once the grant has been accessed.  '''

        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        ''' Scopes as a list. '''

        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model):
    ''' Simple token implementation. '''

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @property
    def scopes(self):
        ''' Scopes as a list. '''

        if self._scopes:
            return self._scopes.split()
        return []
