from flask import abort, Blueprint, jsonify, request, session, url_for
from app import db, redis_db_pin_codes
from utils.faker import get_random_code, send_code_to_email
from utils.token import create_access_token
from db.models import User, SocialAccount
import json

sn = Blueprint('sn', __name__)

from config.social_networks import github, google, facebook, vk

NETWORKS = {
        'facebook': facebook,
        'github': github,
        'google': google,
        'vk': vk
    }


def get_facebook_params_from_responce(resp):
    me = facebook.get('/me')
    user_id = me.data['id']
    login = me.data['name']
    email = user_id + "@oath.facebook.com"
    return user_id, login, email


def get_github_params_from_responce(resp):
    me = github.get('user')
    user_id = me.data['id']
    login = me.data['login']
    email = me.data['email']
    return user_id, login, email


def get_google_params_from_responce(resp):
    USER_INFO = google.base_url + '/userinfo/v2/me'
    raw = google.get(USER_INFO).raw_data
    result = json.loads(raw)
    user_id = result['id']
    login = user_id
    email = result['email']
    return user_id, login, email


def get_vk_params_from_responce(resp):
    user_id = resp.get('user_id')
    login = resp.get('user_id')
    email = resp.get('email')
    return user_id, login, email


def get_params_from_responce(sn, resp):
    sn_funcs = {
        'facebook': get_facebook_params_from_responce,
        'github': get_github_params_from_responce,
        'google': get_google_params_from_responce,
        'vk': get_vk_params_from_responce
    }
    return sn_funcs[sn](resp)


@sn.route('/login/<social_network>')
def loging(social_network):
    sn = NETWORKS.get(social_network)
    if not sn:
        abort(400, f"Not support social network {social_network}")
    return sn.authorize(callback=url_for('sn.auth', social_network=social_network, _external=True))


@sn.route('/auth/<social_network>')
def auth(social_network):
    sn = NETWORKS.get(social_network)
    if not sn:
        abort(400, f"Not support social network {social_network}")
    resp = sn.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session[f'{social_network}_token'] = (resp['access_token'], '')
    user_id, login, email = get_params_from_responce(social_network, resp)

    sa = SocialAccount.query.filter_by(social_id=str(user_id), social_name=social_network).first()
    if not sa:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(login=login, email=email)
            db.session.add(user)
            db.session.commit()
        else:
            login = user.login
        sa = SocialAccount(user_id=user.id, user=user, social_id=str(user_id), social_name=social_network)
        db.session.add(sa)
        db.session.commit()

    pin_code = get_random_code()
    send_code_to_email(pin_code, email)
    return jsonify({'pin_code': pin_code, 'email': email, 'message': f"Please, send pin code from you email {email}"})


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_token')


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@vk.tokengetter
def get_vk_oauth_token():
    return session.get('vk_token')