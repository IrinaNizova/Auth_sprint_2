from app import app
from flask_oauthlib.client import OAuth

oauth = OAuth(app)

facebook = oauth.remote_app(
    'facebook',
    consumer_key='469241967564553',
    consumer_secret='9d0a5ee417cec2f3837b2fb2e392cf6f',
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth'
)

github = oauth.remote_app(
    'github',
    consumer_key='7ee92c64c039cb4772cc',
    consumer_secret='040cb894025931518a306a0d88a3a5c4b62a2f2e',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

google = oauth.remote_app(
    'google',
    consumer_key='674404786168-vlbu0o54vnjodmcea6r8o6m65m9d4s65.apps.googleusercontent.com',
    consumer_secret='eIkX24b7hOgAVVG8jkwMZ7cC',
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com',
    request_token_url=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth'
)

vk = oauth.remote_app(
    'vk',
    consumer_key='7769603',
    consumer_secret='VYwbx3X7c4GazZkWBSR2',
    request_token_url=None,
    access_token_method='POST',
    request_token_params={'scope': 'email'},
    base_url='https://api.vk.com/method',
    access_token_url='https://oauth.vk.com/access_token',
    authorize_url='https://oauth.vk.com/authorize',
)
