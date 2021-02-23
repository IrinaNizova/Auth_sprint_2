import bcrypt
import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID

from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=str(uuid.uuid4()))
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.Binary, nullable=False)

    def __init__(self, login, password):
        self.id = str(uuid.uuid4())
        self.login = login
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def __repr__(self):
        return f'<User {self.login}>'

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_web" PARTITION OF "users_sign_in" FOR VALUES IN ('web')"""
    )


class UserSignIn(db.Model):
    __tablename__ = 'users_sign_in'
    __table_args__ = {
        'postgresql_partition_by': 'LIST (user_device_type)',
        'listeners': [('after_create', create_partition)],
    }

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    logined_by = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_agent = db.Column(db.Text)
    user_device_type = db.Column(db.Text)
    __mapper_args__ = {
        'primary_key': [user_id, logined_by]
    }

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logined_by}>'

    def to_dict(self):
        return {key: str(value) for key, value in self.__dict__.items() if not key.startswith('_') and key != 'user_id'}
