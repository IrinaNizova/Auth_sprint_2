from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import logging
import redis

from config.config import redis_0_params, postgres_dsl as pd, SECRET_KEY
from flasgger import Swagger
from flask_marshmallow import Marshmallow

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)
ma = Marshmallow(app)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{pd.user}:{pd.password}@{pd.host}:{pd.port}/{pd.dbname}'
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)
redis_db = redis.Redis(host=redis_0_params.host, port=redis_0_params.port, db=redis_0_params.db)

logging.basicConfig(filename='log.log', level=logging.DEBUG)

import api.views as api_resources

api.add_resource(api_resources.New, '/new')
api.add_resource(api_resources.Login, '/login')
api.add_resource(api_resources.Login2, '/login2')
api.add_resource(api_resources.Logout, '/logout')
api.add_resource(api_resources.ChangeLogin, '/change-login')
api.add_resource(api_resources.RefreshToken, '/refresh')
api.add_resource(api_resources.Sessions, '/sessions')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

