import pyotp

from app import db, app
from flask_login import UserMixin
from datetime import datetime
from cryptography.fernet import Fernet


def encrypt(data, secret_key):
    return Fernet(secret_key).encrypt(bytes(data, 'utf-8'))


def decrypt(data, secret_key):
    return Fernet(secret_key).decrypt(data).decode('utf-8')


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    # User PIN
    pin_key = db.Column(db.String(32), nullable=False, default=pyotp.random_base32())

    # Advanced information
    date_of_birth = db.Column(db.String(10), nullable=False)
    postcode = db.Column(db.String(10), nullable=False)

    # Logging information
    registered_on = db.Column(db.DateTime, nullable=False)
    current_login = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    # Logging IP addresses
    current_ip = db.Column(db.String(20), nullable=True)
    last_ip = db.Column(db.String(20), nullable=True)

    # Total number of successful logins
    total_logins = db.Column(db.Integer)

    # Encryption keys
    secret_key = db.Column(db.BLOB, nullable=False, default=Fernet.generate_key())

    # Define the relationship to Draw
    draws = db.relationship('models.Draw')

    def __init__(self, email, firstname, lastname, phone, password, role, pin_key, date_of_birth, postcode):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.role = role
        self.pin_key = pin_key
        self.date_of_birth = date_of_birth
        self.postcode = postcode
        self.registered_on = datetime.now()
        self.current_login = None
        self.last_login = None
        self.current_ip = None
        self.last_ip = None
        self.total_logins = 0


    def get_2fa_uri(self):
        return str(pyotp.totp.TOTP(self.pin_key).provisioning_uri(
            name=self.email,
            issuer_name='Stewart Foundation')
        )

    def verify_password(self, password):
        return self.password == password

    def verify_postcode(self, postcode: str):
        comparator = self.postcode.strip().replace(" ", "").lower()
        # print(postcode, self.postcode, comparator)
        return comparator == postcode.replace(" ", "").lower()

    def verify_pin(self, submitted_pin):
        return pyotp.TOTP(self.pin_key).verify(submitted_pin)


class Draw(db.Model):
    __tablename__ = 'draws'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # ID of user who submitted draw
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # 6 draw numbers submitted
    numbers = db.Column(db.BLOB, nullable=False)

    # Draw has already been played (can only play draw once)
    been_played = db.Column(db.BOOLEAN, nullable=False, default=False)

    # Draw matches with master draw created by admin (True = draw is a winner)
    matches_master = db.Column(db.BOOLEAN, nullable=False, default=False)

    # True = draw is master draw created by admin. User draws are matched to master draw
    master_draw = db.Column(db.BOOLEAN, nullable=False)

    # Lottery round that draw is used
    lottery_round = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, numbers, master_draw, lottery_round, secret_key):
        self.user_id = user_id
        self.numbers = encrypt(numbers, secret_key)
        self.been_played = False
        self.matches_master = False
        self.master_draw = master_draw
        self.lottery_round = lottery_round

    def view_draw(self, secret_key):
        self.numbers = decrypt(self.numbers, secret_key)


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(email='admin@email.com',
                     password='Admin1!',
                     firstname='Alice',
                     lastname='Jones',
                     phone='0191-123-4567',
                     role='admin',
                     pin_key='BFB5S34STBLZCOB22K6PPYDCMZMH46OJ',
                     date_of_birth='01/01/0000',
                     postcode='NE4 5TG')

        db.session.add(admin)
        db.session.commit()





if __name__ == '__main__':
    init_db()
