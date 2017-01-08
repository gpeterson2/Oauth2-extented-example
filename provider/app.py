from flask import (
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from decorators import login_required
from controllers import (
    client_blueprint,
    grant_blueprint,
    oauth_blueprint,
    token_blueprint,
    user_blueprint,
)
from controllers.oauth import oauth
from models import db, User

app = Flask(__name__, template_folder='templates')
app.config.from_object('config')

app.register_blueprint(client_blueprint)
app.register_blueprint(grant_blueprint)
app.register_blueprint(oauth_blueprint)
app.register_blueprint(token_blueprint)
app.register_blueprint(user_blueprint)


@app.before_request
def before_request():
    ''' Make sure the user is in session before each request. '''

    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.route('/', methods=('GET', 'POST'))
@app.route('/login', methods=('GET', 'POST'))
def login():
    ''' A relatively standard login page.

        This does not require a password and creates a user if it does not
        exist. Not the best of ideas, but for example purposes it works.
    '''

    # TODO
    # - should not create a user here
    # - handle errors
    # - csrf
    # - should include password.

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.id
    return redirect(url_for('.home'))


@app.route('/logout')
def logout():
    ''' Simple logout. '''

    if 'user_id' in session:
        del session['user_id']
    return redirect(url_for('.login'))


@app.route('/home')
@login_required
def home():
    ''' Once logged in this page will be displayed. '''

    return render_template('home.html')


@app.route('/api/me')
@oauth.require_oauth()
def me():
    ''' Api for use once the oauth authentication is completed.

        This could be in a blueprint as well, but at this point the api does
        so little that it doesn't matter.
    '''

    user = request.oauth.user
    return jsonify(username=user.username)


if __name__ == '__main__':
    db.init_app(app)
    oauth.init_app(app)

    db.create_all(app=app)
    app.run()
