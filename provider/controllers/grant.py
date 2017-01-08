from flask import Blueprint, render_template

from decorators import login_required
from models import Grant

grant_blueprint = Blueprint('grant', __name__, url_prefix='/grant')


@grant_blueprint.route('/')
@login_required
def list_grants():
    ''' List grants.

        Ideally this will show nothing as grants should be deleted once used
        and that process should not last long enough to display here, unless
        the user is particularly lucky when loading the page.
    '''

    grants = Grant.query.all()

    return render_template('grant/list.html', grants=grants)
