# TODO
# - There should be a delete. Or at least an "active" flag that can be altered.
# - This should also have csrf protection.
# - Also ideally the user would have a password that would be set here
#   (hopefully not directly by the user). If added a password reset process
#   would also be nice.

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)

from decorators import login_required
from models import db, User

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_blueprint.route('/')
@login_required
def list_users():
    ''' Lists users. '''

    users = User.query.all()

    return render_template('user/list.html', users=users)


# TODO - should use csrf
@user_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def create_user():
    ''' Creates users. '''

    if request.method == 'GET':
        return render_template('user/add.html')

    username = request.form['username']

    user = User(username=username)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('.list_users'))


# TODO - should use csrf
@user_blueprint.route('/update/<user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    ''' Updates users. '''

    user = User.query.filter(User.id == user_id).first()

    if request.method == 'GET':
        return render_template('user/update.html', user=user)

    user_id = request.form['user_id']
    username = request.form.get('username')

    user.username = username

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('.list_users'))
