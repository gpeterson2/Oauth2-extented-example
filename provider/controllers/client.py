''' Client specific operations. '''

# TODO
# - Add a delete action
# - The create adds minimal info and then sends you to the update, but ideally
#   there would be a better frontend to allow this editing before saving.
# - The update also lacks this editing, so only updates once you save. This
#   means for each redirect uri and scope you have to save each time you add
#   one. Deleting works if you submit an empty form field, but that's
#   particularly good UX.
# - There should probably be a way to generate a new key for an existing
#   client. Although most implementations just require you to create a new
#   client anyway in that situation.

from werkzeug.security import gen_salt

from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from decorators import login_required
from models import db, Client

client_blueprint = Blueprint('client', __name__, url_prefix='/client')


@client_blueprint.route('/')
@login_required
def list_clients():
    ''' Lists clients. '''

    clients = Client.query.all()

    return render_template('client/list.html', clients=clients)


# TODO - should use csrf
@client_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def create_client():
    ''' Creates a new client.

        The frontend does not allow adding multiple redirect uris/scopes so
        once created it redirects to the update where this can be done.

        The client id and secret are generated once this process is started
        and it is not possible to update them after the fact.
    '''

    if request.method == 'GET':
        context = {
            'client_id': gen_salt(40),
            'client_secret': gen_salt(50),
        }

        return render_template('client/add.html', **context)

    client_id = request.form['client_id']
    client_secret = request.form['client_secret']
    name = request.form.get('name')

    user = g.user
    item = Client(
        client_id=client_id,
        client_secret=client_secret,
        name=name,
        _redirect_uris='',
        _default_scopes='',
        user_id=user.id,
    )
    db.session.add(item)
    db.session.commit()

    return redirect(url_for('.update_client', client_id=client_id))


# TODO - should use csrf
@client_blueprint.route('/update/<client_id>', methods=['GET', 'POST'])
@login_required
def update_client(client_id):
    ''' Updates a client.

        This allows updating and removing redirect uris and scopes, but the UX
        could still use some work. Once added hit the "update" button and the
        template will be udpated again. To remove one of those values just
        submit a blank.

        Once done hit the "done" link.
    '''

    # Example redirect urls
    # 'http://localhost:8000/authorized',
    # 'http://127.0.0.1:8000/authorized',
    # 'http://127.0.1:8000/authorized',
    # 'http://127.1:8000/authorized',

    # TODO - should check user, too
    client = Client.query.filter(Client.client_id == client_id).first()

    if request.method == 'GET':
        return render_template('client/update.html', client=client)

    client_id = request.form['client_id']
    client_secret = request.form['client_secret']
    name = request.form.get('name')
    redirect_uris = request.form.getlist('redirect_uris')
    redirect_uris = [r.strip() for r in redirect_uris if r.strip()]
    scopes = request.form.getlist('scopes')
    scopes = [s.strip() for s in scopes if s.strip()]

    client.client_secret = client_secret
    client.name = name
    client._redirect_uris = ' '.join(redirect_uris)
    client._default_scopes = ' '.join(scopes)

    db.session.add(client)
    db.session.commit()

    # Redirecting back to self to allow adding more redirect urls/scopes
    # TODO - Ideally this would be done in javascript and allow deletion.
    return redirect(url_for('.update_client', client_id=client_id))
