from flask import Blueprint, render_template

from decorators import login_required
from models import Token

token_blueprint = Blueprint('token', __name__, url_prefix='/token')


@token_blueprint.route('/')
@login_required
def list_tokens():
    ''' List tokens. '''

    tokens = Token.query.all()

    return render_template('token/list.html', tokens=tokens)
